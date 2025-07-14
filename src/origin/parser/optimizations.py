"""
AST optimization utilities for Origin language.
Includes constant folding for simple arithmetic expressions.
"""
from .ast_nodes import ASTNode, NumberNode, BinaryOpNode
from typing import Any

def constant_fold(node: ASTNode) -> ASTNode:
    """Recursively fold constant binary operations in the AST."""
    if isinstance(node, BinaryOpNode):
        left = constant_fold(node.left)
        right = constant_fold(node.right)
        if isinstance(left, NumberNode) and isinstance(right, NumberNode):
            # Only fold simple arithmetic
            try:
                if node.operator == '+':
                    return NumberNode(left.value + right.value)
                elif node.operator == '-':
                    return NumberNode(left.value - right.value)
                elif node.operator == '*':
                    return NumberNode(left.value * right.value)
                elif node.operator == '/':
                    return NumberNode(left.value / right.value)
                elif node.operator == '%':
                    return NumberNode(left.value % right.value)
            except Exception:
                pass  # Don't fold if error (e.g., division by zero)
        return BinaryOpNode(node.operator, left, right)
    # Recursively fold children for other node types if needed
    # (Extend as needed for more node types)
    return node 