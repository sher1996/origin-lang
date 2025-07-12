import re
import os
from typing import Any, List, Dict, Optional
from parser import SayNode, LetNode, RepeatNode, FuncDefNode, FuncCallNode, ExprStmtNode, ImportNode, StringNode
import lexer
import parser
from .recorder import Recorder

class OriginError(RuntimeError):
    pass

class Evaluator:
    """Evaluates Origin AST with optional execution recording."""
    
    def __init__(self, recorder: Optional[Recorder] = None):
        self.recorder = recorder
        self.global_loaded_modules = set()
    
    def _generate_node_id(self, node: Any) -> str:
        """Generate a unique ID for an AST node."""
        node_type = type(node).__name__
        if hasattr(node, 'name'):
            return f"{node_type}:{node.name}"
        elif hasattr(node, 'expr'):
            return f"{node_type}:{str(node.expr)[:20]}"
        else:
            return f"{node_type}:{id(node)}"
    
    def _record_execution(self, node: Any, variables: Dict[str, Any], functions: Dict[str, Any]) -> None:
        """Record execution step if recorder is active."""
        if self.recorder:
            node_id = self._generate_node_id(node)
            env = {
                "variables": variables.copy(),
                "functions": list(functions.keys()),  # Don't record function bodies
                "node_type": type(node).__name__
            }
            self.recorder.record(node_id, env)
    
    def _plus(self, a, b):
        """String concatenation or numeric addition."""
        if isinstance(a, str) or isinstance(b, str):
            return str(a) + str(b)
        return a + b
    
    def _replace_plus_outside_strings(self, expr):
        """Replace a + b with _PLUS_(a, b) where a and b are quoted strings or identifiers/numbers."""
        pattern = r'((?:"[^"]*")|(?:\w+))\s*\+\s*((?:"[^"]*")|(?:\w+))'
        while re.search(pattern, expr):
            expr = re.sub(pattern, r'_PLUS_(\1, \2)', expr)
        return expr
    
    def _http_get(self, url, net_allowed=False):
        """HTTP GET function stub."""
        if net_allowed:
            return f"(NetStub: {url})"
        else:
            raise OriginError("network access denied")
    
    def _ai_ask(self, prompt):
        """AI ask function stub."""
        return f"(AI-Answer: {str(prompt)[:15]})"
    
    def _ai_classify(self, text, *labels):
        """AI classify function stub."""
        return min(labels, key=len) if labels else ""
    
    def _make_func(self, name: str, functions: Dict[str, Any], variables: Dict[str, Any]):
        """Create a callable function from function definition."""
        def _func(*args):
            func = functions[name]
            if len(args) != len(func['params']):
                raise OriginError(f"function '{name}' expects {len(func['params'])} arguments, got {len(args)}")
            local_vars = variables.copy()
            for param, arg in zip(func['params'], args):
                local_vars[param] = self._eval_expr(arg, local_vars, functions)
            result = None
            for stmt in func['body']:
                if isinstance(stmt, LetNode):
                    local_vars[stmt.name] = self._eval_expr(stmt.expr, local_vars, functions)
                elif isinstance(stmt, SayNode):
                    result = self._eval_expr(stmt.expr, local_vars, functions)
                    if isinstance(result, float) and result.is_integer():
                        print(int(result))
                    else:
                        print(result)
                elif isinstance(stmt, ExprStmtNode):
                    result = self._eval_expr(stmt.expr, local_vars, functions)
                else:
                    raise OriginError(f"unknown statement type in function: {type(stmt)}")
            return result
        return _func
    
    def _eval_expr(self, expr: str, variables: Dict[str, Any], functions: Dict[str, Any]) -> Any:
        """Evaluate an expression with the given environment."""
        allowed_names = {**variables, "__builtins__": {}}
        # Add user functions as callables
        for fname in functions:
            allowed_names[fname] = self._make_func(fname, functions, variables)
        # Add built-in functions
        allowed_names['http_get'] = lambda url: self._http_get(url, self.net_allowed)
        allowed_names['_PLUS_'] = self._plus
        
        # Add AI object
        class _AI:
            ask = staticmethod(self._ai_ask)
            classify = staticmethod(self._ai_classify)
        allowed_names['ai'] = _AI
        
        expr = re.sub(r"\s+", " ", expr.strip())
        # Pre-process + operators to use our plus function, but only outside strings
        expr = self._replace_plus_outside_strings(expr)
        return eval(expr, allowed_names)
    
    def _exec_node(self, node: Any, variables: Dict[str, Any], functions: Dict[str, Any]) -> Any:
        """Execute a single AST node."""
        # Record execution step
        self._record_execution(node, variables, functions)
        
        if isinstance(node, LetNode):
            variables[node.name] = self._eval_expr(node.expr, variables, functions)
            return None
        elif isinstance(node, SayNode):
            result = self._eval_expr(node.expr, variables, functions)
            if isinstance(result, float) and result.is_integer():
                print(int(result))
            else:
                print(result)
            return None
        elif isinstance(node, StringNode):
            # Handle standalone string literals
            print(node.value)
            return None
        elif isinstance(node, RepeatNode):
            for _ in range(node.count):
                for stmt in node.body:
                    self._exec_node(stmt, variables, functions)
            return None
        elif isinstance(node, FuncDefNode):
            functions[node.name] = {
                'params': node.params,
                'body': node.body
            }
            return None
        elif isinstance(node, FuncCallNode):
            # Direct function call at top level (not via eval)
            func = functions[node.name]
            if len(node.args) != len(func['params']):
                raise OriginError(f"function '{node.name}' expects {len(func['params'])} arguments, got {len(node.args)}")
            local_vars = variables.copy()
            for param, arg in zip(func['params'], node.args):
                local_vars[param] = self._eval_expr(arg, variables, functions)
            result = None
            for stmt in func['body']:
                if isinstance(stmt, LetNode):
                    local_vars[stmt.name] = self._eval_expr(stmt.expr, local_vars, functions)
                elif isinstance(stmt, SayNode):
                    result = self._eval_expr(stmt.expr, local_vars, functions)
                    if isinstance(result, float) and result.is_integer():
                        print(int(result))
                    else:
                        print(result)
                elif isinstance(stmt, ExprStmtNode):
                    result = self._eval_expr(stmt.expr, local_vars, functions)
                else:
                    raise OriginError(f"unknown statement type in function: {type(stmt)}")
            return result
        elif isinstance(node, ImportNode):
            # Check if file access is allowed
            if not self.files_allowed:
                raise OriginError("file access denied")
            # Only load if not already loaded
            import_path = node.path
            if self.base_path is not None:
                import_path = os.path.join(self.base_path, import_path)
            if import_path not in self.global_loaded_modules:
                self.global_loaded_modules.add(import_path)
                with open(import_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                tokens = lexer.tokenize(source)
                ast = parser.parse(tokens)
                # Use the directory of the imported file as base_path for its imports
                import_base = os.path.dirname(import_path)
                self.execute(ast, base_path=import_base, variables=variables, functions=functions)
            return None
        else:
            raise OriginError(f"unknown keyword \"{type(node).__name__}\"")
    
    def execute(self, ast: List[Any], base_path=None, variables=None, functions=None, 
                net_allowed=False, files_allowed=True) -> None:
        """Execute an AST with the given environment and options."""
        if variables is None:
            variables = {}
        if functions is None:
            functions = {}
        
        self.base_path = base_path
        self.net_allowed = net_allowed
        self.files_allowed = files_allowed
        
        for node in ast:
            self._exec_node(node, variables, functions) 