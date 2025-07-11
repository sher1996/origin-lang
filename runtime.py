import re
import os
from typing import Any, List
from parser import SayNode, LetNode, RepeatNode, FuncDefNode, FuncCallNode, ExprStmtNode, ImportNode
import lexer
import parser

global_loaded_modules = set()

def execute(ast: List[Any], base_path=None, variables=None, functions=None):
    if variables is None:
        variables = {}
    if functions is None:
        functions = {}

    def make_func(name):
        def _func(*args):
            func = functions[name]
            if len(args) != len(func['params']):
                raise RuntimeError(f"Function '{name}' expects {len(func['params'])} arguments, got {len(args)}")
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
                    raise RuntimeError(f"Unknown statement type in function: {type(stmt)}")
            return result
        return _func

    def eval_expr(expr: str, variables: dict) -> Any:
        allowed_names = {**variables, "__builtins__": {}}
        # Add user functions as callables
        for fname in functions:
            allowed_names[fname] = make_func(fname)
        expr = re.sub(r"\s+", " ", expr.strip())
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
                raise RuntimeError(f"Function '{node.name}' expects {len(func['params'])} arguments, got {len(node.args)}")
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
                    raise RuntimeError(f"Unknown statement type in function: {type(stmt)}")
            return result
        elif isinstance(node, ImportNode):
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
            raise RuntimeError(f"Unknown AST node: {node}")

    for node in ast:
        exec_node(node) 