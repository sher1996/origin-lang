import re
from typing import Any, List
from parser import SayNode, LetNode, RepeatNode

def eval_expr(expr: str, variables: dict) -> Any:
    allowed_names = {**variables, "__builtins__": {}}
    expr = re.sub(r"\s+", " ", expr.strip())
    return eval(expr, allowed_names)

def execute(ast: List[Any]):
    variables = {}
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
        else:
            raise RuntimeError(f"Unknown AST node: {node}")
    for node in ast:
        exec_node(node) 