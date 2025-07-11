import re
import os
from typing import Any, List
from parser import SayNode, LetNode, RepeatNode, FuncDefNode, FuncCallNode, ExprStmtNode, ImportNode, StringNode
import lexer
import parser

class OriginError(RuntimeError):
    pass

global_loaded_modules = set()

def plus(a, b):
    if isinstance(a, str) or isinstance(b, str):
        return str(a) + str(b)
    return a + b

def replace_plus_outside_strings(expr):
    # Replace a + b with _PLUS_(a, b) where a and b are quoted strings or identifiers/numbers
    pattern = r'((?:"[^"]*")|(?:\w+))\s*\+\s*((?:"[^"]*")|(?:\w+))'
    while re.search(pattern, expr):
        expr = re.sub(pattern, r'_PLUS_(\1, \2)', expr)
    return expr

def execute(ast: List[Any], base_path=None, variables=None, functions=None, net_allowed=False, files_allowed=True):
    if variables is None:
        variables = {}
    if functions is None:
        functions = {}

    def http_get(url):
        if net_allowed:
            return f"(NetStub: {url})"
        else:
            raise OriginError("network access denied")

    def make_func(name):
        def _func(*args):
            func = functions[name]
            if len(args) != len(func['params']):
                raise OriginError(f"function '{name}' expects {len(func['params'])} arguments, got {len(args)}")
            local_vars = variables.copy()
            for param, arg in zip(func['params'], args):
                local_vars[param] = arg
            result = None
            for stmt in func['body']:
                if isinstance(stmt, LetNode):
                    local_vars[stmt.name] = eval_expr(stmt.expr, local_vars)
                elif isinstance(stmt, SayNode):
                    result = eval_expr(stmt.expr, local_vars)
                    if isinstance(result, float) and result.is_integer():
                        print(int(result))
                    else:
                        print(result)
                elif isinstance(stmt, ExprStmtNode):
                    result = eval_expr(stmt.expr, local_vars)
                else:
                    raise OriginError(f"unknown statement type in function: {type(stmt)}")
            return result
        return _func

    def ai_ask(prompt):
        return f"(AI-Answer: {str(prompt)[:15]})"

    def ai_classify(text, *labels):
        return min(labels, key=len) if labels else ""

    class _AI:
        ask = staticmethod(ai_ask)
        classify = staticmethod(ai_classify)

    def eval_expr(expr: str, variables: dict) -> Any:
        allowed_names = {**variables, "__builtins__": {}}
        # Add user functions as callables
        for fname in functions:
            allowed_names[fname] = make_func(fname)
        # Add http_get function
        allowed_names['http_get'] = http_get
        # Add plus function for string concatenation
        allowed_names['_PLUS_'] = plus
        # Add AI object
        allowed_names['ai'] = _AI
        expr = re.sub(r"\s+", " ", expr.strip())
        # Pre-process + operators to use our plus function, but only outside strings
        expr = replace_plus_outside_strings(expr)
        return eval(expr, allowed_names)

    def exec_node(node):
        if isinstance(node, LetNode):
            variables[node.name] = eval_expr(node.expr, variables)
        elif isinstance(node, SayNode):
            result = eval_expr(node.expr, variables)
            if isinstance(result, float) and result.is_integer():
                print(int(result))
            else:
                print(result)
        elif isinstance(node, StringNode):
            # Handle standalone string literals
            print(node.value)
        elif isinstance(node, RepeatNode):
            for _ in range(node.count):
                for stmt in node.body:
                    exec_node(stmt)
        elif isinstance(node, FuncDefNode):
            functions[node.name] = {
                'params': node.params,
                'body': node.body
            }
        elif isinstance(node, FuncCallNode):
            # Direct function call at top level (not via eval)
            func = functions[node.name]
            if len(node.args) != len(func['params']):
                raise OriginError(f"function '{node.name}' expects {len(func['params'])} arguments, got {len(node.args)}")
            local_vars = variables.copy()
            for param, arg in zip(func['params'], node.args):
                local_vars[param] = eval_expr(arg, variables)
            result = None
            for stmt in func['body']:
                if isinstance(stmt, LetNode):
                    local_vars[stmt.name] = eval_expr(stmt.expr, local_vars)
                elif isinstance(stmt, SayNode):
                    result = eval_expr(stmt.expr, local_vars)
                    if isinstance(result, float) and result.is_integer():
                        print(int(result))
                    else:
                        print(result)
                elif isinstance(stmt, ExprStmtNode):
                    result = eval_expr(stmt.expr, local_vars)
                else:
                    raise OriginError(f"unknown statement type in function: {type(stmt)}")
            return result
        elif isinstance(node, ImportNode):
            # Check if file access is allowed
            if not files_allowed:
                raise OriginError("file access denied")
            # Only load if not already loaded
            import_path = node.path
            if base_path is not None:
                import_path = os.path.join(base_path, import_path)
            if import_path not in global_loaded_modules:
                global_loaded_modules.add(import_path)
                with open(import_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                tokens = lexer.tokenize(source)
                ast = parser.parse(tokens)
                # Use the directory of the imported file as base_path for its imports
                import_base = os.path.dirname(import_path)
                execute(ast, base_path=import_base, variables=variables, functions=functions)
        else:
            raise OriginError(f"unknown keyword \"{type(node).__name__}\"")

    for node in ast:
        exec_node(node) 