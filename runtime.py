import re
from typing import Any, List
from parser import SayNode, LetNode, RepeatNode, FuncDefNode, FuncCallNode, ExprStmtNode

def execute(ast: List[Any]):
    variables = {}
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
        else:
            raise RuntimeError(f"Unknown AST node: {node}")

    for node in ast:
        exec_node(node) 