"""
Visitor-based evaluator for Origin AST.
Replaces eval() with explicit tree walking for better performance and security.
"""

import os
from typing import Any, Dict, List, Optional
from ..parser.ast_nodes import (
    ASTVisitor, ASTNode, NumberNode, StringNode, BinaryOpNode, UnaryOpNode,
    VariableNode, FunctionCallNode, IfExprNode, WhileExprNode, ListExprNode,
    DictExprNode, IndexExprNode, AttributeExprNode
)
from ..recorder import Recorder

class OriginError(RuntimeError):
    pass

class EvaluatorVisitor(ASTVisitor):
    """Visitor that evaluates AST nodes without using eval()."""
    
    def __init__(self, variables: Dict[str, Any], functions: Dict[str, Any], 
                 recorder: Optional[Recorder] = None, net_allowed: bool = False):
        self.variables = variables
        self.functions = functions
        self.recorder = recorder
        self.net_allowed = net_allowed
        self.node_counts = {}  # For profiling
        self.base_path = None
        self.files_allowed = True
        self.global_loaded_modules = set()
        self._attr_cache = {}  # Attribute lookup cache for tight loops
    
    def _record_execution(self, node: ASTNode) -> None:
        """Record execution step if recorder is active."""
        if self.recorder:
            node_type = type(node).__name__
            node_id = f"{node_type}:{id(node)}"
            env = {
                "variables": self.variables.copy(),
                "functions": list(self.functions.keys()),
                "node_type": node_type
            }
            self.recorder.record(node_id, env)
    
    def _increment_node_count(self, node_type: str) -> None:
        """Increment node execution count for profiling."""
        self.node_counts[node_type] = self.node_counts.get(node_type, 0) + 1
    
    def visit_number(self, node: NumberNode) -> Any:
        """Evaluate a number literal."""
        self._increment_node_count("NumberNode")
        self._record_execution(node)
        return node.value
    
    def visit_string(self, node: StringNode) -> Any:
        """Evaluate a string literal."""
        self._increment_node_count("StringNode")
        self._record_execution(node)
        return node.value
    
    def visit_binary_op(self, node: BinaryOpNode) -> Any:
        """Evaluate a binary operation."""
        self._increment_node_count("BinaryOpNode")
        self._record_execution(node)
        
        left_val = node.left.accept(self)
        right_val = node.right.accept(self)
        
        if node.operator == '+':
            # String concatenation or numeric addition
            if isinstance(left_val, str) or isinstance(right_val, str):
                return str(left_val) + str(right_val)
            return left_val + right_val
        elif node.operator == '-':
            return left_val - right_val
        elif node.operator == '*':
            return left_val * right_val
        elif node.operator == '/':
            return left_val / right_val
        elif node.operator == '%':
            return left_val % right_val
        elif node.operator == '==':
            return left_val == right_val
        elif node.operator == '!=':
            return left_val != right_val
        elif node.operator == '<':
            return left_val < right_val
        elif node.operator == '<=':
            return left_val <= right_val
        elif node.operator == '>':
            return left_val > right_val
        elif node.operator == '>=':
            return left_val >= right_val
        elif node.operator == 'and':
            return left_val and right_val
        elif node.operator == 'or':
            return left_val or right_val
        else:
            raise OriginError(f"Unknown binary operator: {node.operator}")
    
    def visit_unary_op(self, node: UnaryOpNode) -> Any:
        """Evaluate a unary operation."""
        self._increment_node_count("UnaryOpNode")
        self._record_execution(node)
        
        operand_val = node.operand.accept(self)
        
        if node.operator == '-':
            return -operand_val
        elif node.operator == 'not':
            return not operand_val
        else:
            raise OriginError(f"Unknown unary operator: {node.operator}")
    
    def visit_variable(self, node: VariableNode) -> Any:
        """Evaluate a variable reference."""
        self._increment_node_count("VariableNode")
        self._record_execution(node)
        
        if node.name in self.variables:
            return self.variables[node.name]
        else:
            raise OriginError(f"Undefined variable: {node.name}")
    
    def visit_function_call(self, node: FunctionCallNode) -> Any:
        """Evaluate a function call."""
        self._increment_node_count("FunctionCallNode")
        self._record_execution(node)
        
        # Evaluate arguments
        args = [arg.accept(self) for arg in node.arguments]
        
        # Handle built-in functions
        if node.name == 'http_get':
            if not self.net_allowed:
                raise OriginError("Network access not permitted — run with --allow-net")
            from ..runtime.net import safe_http_get
            return safe_http_get(*args)
        elif node.name == '_PLUS_':
            # Custom plus function for string/numeric concatenation
            if len(args) != 2:
                raise OriginError("_PLUS_ requires exactly 2 arguments")
            a, b = args
            if isinstance(a, str) or isinstance(b, str):
                return str(a) + str(b)
            return a + b
        elif node.name == 'len':
            return len(args[0]) if args else 0
        
        # Handle user-defined functions
        if node.name in self.functions:
            func = self.functions[node.name]
            if len(args) != len(func['params']):
                raise OriginError(f"function '{node.name}' expects {len(func['params'])} arguments, got {len(args)}")
            
            # Create local environment
            local_vars = self.variables.copy()
            for param, arg in zip(func['params'], args):
                local_vars[param] = arg
            
            # Create new visitor for function execution
            func_visitor = EvaluatorVisitor(local_vars, self.functions, self.recorder, self.net_allowed)
            func_visitor.base_path = self.base_path
            func_visitor.files_allowed = self.files_allowed
            
            result = None
            for stmt in func['body']:
                result = stmt.accept(func_visitor)
            return result
        
        # Handle JSON object
        if node.name == 'json':
            from ..builtins.json import parse as json_parse
            if len(args) == 1:
                return json_parse(args[0])
            else:
                raise OriginError("json.parse requires exactly 1 argument")
        
        # Handle AI object
        if node.name == 'ai':
            if len(args) == 1:
                return f"(AI-Answer: {str(args[0])[:15]})"
            else:
                raise OriginError("ai.ask requires exactly 1 argument")
        
        raise OriginError(f"Undefined function: {node.name}")
    
    def visit_if_expr(self, node: IfExprNode) -> Any:
        """Evaluate an if expression."""
        self._increment_node_count("IfExprNode")
        self._record_execution(node)
        
        condition_val = node.condition.accept(self)
        
        if condition_val:
            return node.then_expr.accept(self)
        elif node.else_expr:
            return node.else_expr.accept(self)
        else:
            return None
    
    def visit_while_expr(self, node: WhileExprNode) -> Any:
        """Evaluate a while expression using iterative loop to avoid recursion."""
        self._increment_node_count("WhileExprNode")
        self._record_execution(node)
        
        result = None
        while True:
            self._attr_cache.clear()  # Clear attribute cache at start of each iteration
            condition_val = node.condition.accept(self)
            if not condition_val:
                break
            result = node.body.accept(self)
        
        return result
    
    def visit_list_expr(self, node: ListExprNode) -> Any:
        """Evaluate a list literal."""
        self._increment_node_count("ListExprNode")
        self._record_execution(node)
        
        return [element.accept(self) for element in node.elements]
    
    def visit_dict_expr(self, node: DictExprNode) -> Any:
        """Evaluate a dictionary literal."""
        self._increment_node_count("DictExprNode")
        self._record_execution(node)
        
        result = {}
        for key_node, value_node in node.items:
            key = key_node.accept(self)
            value = value_node.accept(self)
            result[key] = value
        return result
    
    def visit_index_expr(self, node: IndexExprNode) -> Any:
        """Evaluate an index expression."""
        self._increment_node_count("IndexExprNode")
        self._record_execution(node)
        
        target_val = node.target.accept(self)
        index_val = node.index.accept(self)
        
        return target_val[index_val]
    
    def visit_attribute_expr(self, node: AttributeExprNode) -> Any:
        """Evaluate an attribute access with caching in tight loops."""
        self._increment_node_count("AttributeExprNode")
        self._record_execution(node)
        
        target_val = node.target.accept(self)
        cache_key = (id(target_val), node.attribute)
        if cache_key in self._attr_cache:
            return self._attr_cache[cache_key]
        if hasattr(target_val, node.attribute):
            value = getattr(target_val, node.attribute)
        elif isinstance(target_val, dict) and node.attribute in target_val:
            value = target_val[node.attribute]
        else:
            raise OriginError(f"Attribute '{node.attribute}' not found on {type(target_val).__name__}")
        self._attr_cache[cache_key] = value
        return value
    
    def get_profile_stats(self) -> Dict[str, int]:
        """Get node execution counts for profiling."""
        return self.node_counts.copy() 