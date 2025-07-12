"""
Test roundtrip transformation: code → blocks → code
"""

import pytest
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.transform.blocks_to_ast import (
    code_to_ast, ast_to_blocks, blocks_to_ast, ast_to_code,
    BlockInstance
)

def test_hello_world_roundtrip():
    """Test roundtrip for hello world program"""
    original_code = 'say "Hello, Origin."'
    
    # Code → AST → Blocks → AST → Code
    ast1 = code_to_ast(original_code)
    blocks = ast_to_blocks(ast1)
    ast2 = blocks_to_ast(blocks)
    final_code = ast_to_code(ast2)
    
    # Should be semantically equivalent
    assert final_code.strip() == original_code.strip()

def test_arithmetic_roundtrip():
    """Test roundtrip for arithmetic program"""
    original_code = """let x = 5
let y = x * 3 - 4
say y
say x + y"""
    
    # Code → AST → Blocks → AST → Code
    ast1 = code_to_ast(original_code)
    blocks = ast_to_blocks(ast1)
    ast2 = blocks_to_ast(blocks)
    final_code = ast_to_code(ast2)
    
    # Should be semantically equivalent
    original_lines = [line.strip() for line in original_code.split('\n') if line.strip()]
    final_lines = [line.strip() for line in final_code.split('\n') if line.strip()]
    assert final_lines == original_lines

def test_import_roundtrip():
    """Test roundtrip for import statement"""
    original_code = 'import "math_utils"'
    
    # Code → AST → Blocks → AST → Code
    ast1 = code_to_ast(original_code)
    blocks = ast_to_blocks(ast1)
    ast2 = blocks_to_ast(blocks)
    final_code = ast_to_code(ast2)
    
    # Should be semantically equivalent
    assert final_code.strip() == original_code.strip()

def test_empty_program():
    """Test empty program"""
    original_code = ""
    
    ast1 = code_to_ast(original_code)
    blocks = ast_to_blocks(ast1)
    ast2 = blocks_to_ast(blocks)
    final_code = ast_to_code(ast2)
    
    assert final_code.strip() == ""

def test_blocks_to_ast_ordering():
    """Test that blocks are ordered correctly by position"""
    # Create blocks in reverse order
    blocks = []
    for i in range(3):
        block = BlockInstance(
            block_id=f"block-{i}",
            definition={
                'id': 'say',
                'label': 'Say',
                'astType': 'SayNode',
                'inputs': [{'id': 'expr', 'label': 'Expression', 'type': 'expression', 'required': True}],
                'outputs': [],
                'serialize': lambda inputs: {'type': 'SayNode', 'expr': inputs['expr']},
                'deserialize': lambda ast_node: {'expr': ast_node.expr},
                'color': 'blue',
            },
            inputs={'expr': f'"{i}"'},
            position={'x': 0, 'y': 200 - (i * 50)}  # Reverse order
        )
        blocks.append(block)
    
    # Convert to AST
    ast = blocks_to_ast(blocks)
    
    # Should be in correct order (top to bottom)
    assert len(ast.statements) == 3
    assert getattr(ast.statements[0], 'expr', '') == '"0"'
    assert getattr(ast.statements[1], 'expr', '') == '"1"'
    assert getattr(ast.statements[2], 'expr', '') == '"2"'

if __name__ == "__main__":
    pytest.main([__file__]) 