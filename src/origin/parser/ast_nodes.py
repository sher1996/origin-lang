"""
Strongly-typed AST node classes for Origin language.
Implements visitor pattern for double dispatch evaluation.
"""

from dataclasses import dataclass
from typing import List, Any, Optional, Union
from abc import ABC, abstractmethod

class ASTVisitor(ABC):
    """Abstract visitor for AST nodes."""
    
    @abstractmethod
    def visit_number(self, node: 'NumberNode') -> Any:
        pass
    
    @abstractmethod
    def visit_string(self, node: 'StringNode') -> Any:
        pass
    
    @abstractmethod
    def visit_binary_op(self, node: 'BinaryOpNode') -> Any:
        pass
    
    @abstractmethod
    def visit_unary_op(self, node: 'UnaryOpNode') -> Any:
        pass
    
    @abstractmethod
    def visit_variable(self, node: 'VariableNode') -> Any:
        pass
    
    @abstractmethod
    def visit_function_call(self, node: 'FunctionCallNode') -> Any:
        pass
    
    @abstractmethod
    def visit_if_expr(self, node: 'IfExprNode') -> Any:
        pass
    
    @abstractmethod
    def visit_while_expr(self, node: 'WhileExprNode') -> Any:
        pass
    
    @abstractmethod
    def visit_list_expr(self, node: 'ListExprNode') -> Any:
        pass
    
    @abstractmethod
    def visit_dict_expr(self, node: 'DictExprNode') -> Any:
        pass
    
    @abstractmethod
    def visit_index_expr(self, node: 'IndexExprNode') -> Any:
        pass
    
    @abstractmethod
    def visit_attribute_expr(self, node: 'AttributeExprNode') -> Any:
        pass

class ASTNode(ABC):
    """Base class for all AST nodes."""
    
    @abstractmethod
    def accept(self, visitor: ASTVisitor) -> Any:
        """Accept a visitor for double dispatch."""
        pass

@dataclass
class NumberNode(ASTNode):
    """Represents a numeric literal."""
    value: Union[int, float]
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_number(self)

@dataclass
class StringNode(ASTNode):
    """Represents a string literal."""
    value: str
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_string(self)

@dataclass
class BinaryOpNode(ASTNode):
    """Represents a binary operation."""
    operator: str
    left: ASTNode
    right: ASTNode
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_binary_op(self)

@dataclass
class UnaryOpNode(ASTNode):
    """Represents a unary operation."""
    operator: str
    operand: ASTNode
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_unary_op(self)

@dataclass
class VariableNode(ASTNode):
    """Represents a variable reference."""
    name: str
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_variable(self)

@dataclass
class FunctionCallNode(ASTNode):
    """Represents a function call."""
    name: str
    arguments: List[ASTNode]
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_function_call(self)

@dataclass
class IfExprNode(ASTNode):
    """Represents an if expression."""
    condition: ASTNode
    then_expr: ASTNode
    else_expr: Optional[ASTNode]
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_if_expr(self)

@dataclass
class WhileExprNode(ASTNode):
    """Represents a while expression."""
    condition: ASTNode
    body: ASTNode
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_while_expr(self)

@dataclass
class ListExprNode(ASTNode):
    """Represents a list literal."""
    elements: List[ASTNode]
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_list_expr(self)

@dataclass
class DictExprNode(ASTNode):
    """Represents a dictionary literal."""
    items: List[tuple[ASTNode, ASTNode]]  # key-value pairs
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_dict_expr(self)

@dataclass
class IndexExprNode(ASTNode):
    """Represents an index expression (e.g., list[index])."""
    target: ASTNode
    index: ASTNode
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_index_expr(self)

@dataclass
class AttributeExprNode(ASTNode):
    """Represents an attribute access (e.g., obj.attr)."""
    target: ASTNode
    attribute: str
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_attribute_expr(self)

# Statement nodes (for backward compatibility with existing parser)
@dataclass
class SayNode(ASTNode):
    """Represents a say statement."""
    expr: ASTNode
    
    def accept(self, visitor: ASTVisitor) -> Any:
        # For now, just evaluate the expression
        return self.expr.accept(visitor)

@dataclass
class LetNode(ASTNode):
    """Represents a let statement."""
    name: str
    expr: ASTNode
    
    def accept(self, visitor: ASTVisitor) -> Any:
        # Let statements are handled specially by the evaluator
        return self.expr.accept(visitor)

@dataclass
class RepeatNode(ASTNode):
    """Represents a repeat statement."""
    count: ASTNode
    body: List[ASTNode]
    
    def accept(self, visitor: ASTVisitor) -> Any:
        # Repeat statements are handled specially by the evaluator
        return self.count.accept(visitor)

@dataclass
class FuncDefNode(ASTNode):
    """Represents a function definition."""
    name: str
    params: List[str]
    body: List[ASTNode]
    
    def accept(self, visitor: ASTVisitor) -> Any:
        # Function definitions are handled specially by the evaluator
        return None

# FuncCallNode removed - use FunctionCallNode instead

@dataclass
class ExprStmtNode(ASTNode):
    """Represents an expression statement."""
    expr: ASTNode
    
    def accept(self, visitor: ASTVisitor) -> Any:
        return self.expr.accept(visitor)

@dataclass
class ImportNode(ASTNode):
    """Represents an import statement."""
    path: str
    
    def accept(self, visitor: ASTVisitor) -> Any:
        # Import statements are handled specially by the evaluator
        return None 