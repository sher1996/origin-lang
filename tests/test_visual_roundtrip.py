"""
Test visual mode round-trip transformation: code ↔ blocks ↔ code
"""

import pytest
import sys
import os
import json

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.transform.blocks_to_ast import (
    code_to_ast, ast_to_blocks, blocks_to_ast, ast_to_code,
    blocks_to_json, json_to_blocks, validate_round_trip,
    BlockInstance, block_registry
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

def test_number_literals_roundtrip():
    """Test roundtrip for number literals"""
    original_code = """42
3.14
-5"""
    
    ast1 = code_to_ast(original_code)
    blocks = ast_to_blocks(ast1)
    ast2 = blocks_to_ast(blocks)
    final_code = ast_to_code(ast2)
    
    # Should be semantically equivalent
    original_lines = [line.strip() for line in original_code.split('\n') if line.strip()]
    final_lines = [line.strip() for line in final_code.split('\n') if line.strip()]
    assert final_lines == original_lines

def test_repeat_roundtrip():
    """Test roundtrip for repeat statement"""
    original_code = """repeat 3 times:
  say "Hello"
  let x = 42"""
    
    ast1 = code_to_ast(original_code)
    blocks = ast_to_blocks(ast1)
    ast2 = blocks_to_ast(blocks)
    final_code = ast_to_code(ast2)
    
    # Should be semantically equivalent
    original_lines = [line.strip() for line in original_code.split('\n') if line.strip()]
    final_lines = [line.strip() for line in final_code.split('\n') if line.strip()]
    assert final_lines == original_lines

def test_if_roundtrip():
    """Test roundtrip for if statement"""
    original_code = """if x > 0:
  say "Positive"
else:
  say "Negative" """
    
    ast1 = code_to_ast(original_code)
    blocks = ast_to_blocks(ast1)
    ast2 = blocks_to_ast(blocks)
    final_code = ast_to_code(ast2)
    
    # Should be semantically equivalent
    original_lines = [line.strip() for line in original_code.split('\n') if line.strip()]
    final_lines = [line.strip() for line in final_code.split('\n') if line.strip()]
    assert final_lines == original_lines

def test_function_roundtrip():
    """Test roundtrip for function definition"""
    original_code = """function greet(name):
  say "Hello, " + name"""
    
    ast1 = code_to_ast(original_code)
    blocks = ast_to_blocks(ast1)
    ast2 = blocks_to_ast(blocks)
    final_code = ast_to_code(ast2)
    
    # Should be semantically equivalent
    original_lines = [line.strip() for line in original_code.split('\n') if line.strip()]
    final_lines = [line.strip() for line in final_code.split('\n') if line.strip()]
    assert final_lines == original_lines

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
        say_def = block_registry.get('say')
        if say_def:
            block = BlockInstance(
                block_id=f"block-{i}",
                definition=say_def,
                inputs={'expr': f'"{i}"'},
                position={'x': 0, 'y': 200 - (i * 50)}  # Reverse order
            )
            blocks.append(block)
        blocks.append(block)
    
    # Convert to AST
    ast = blocks_to_ast(blocks)
    
    # Should be in correct order (top to bottom)
    assert len(ast.statements) == 3
    assert getattr(ast.statements[0], 'expr', '') == '"0"'
    assert getattr(ast.statements[1], 'expr', '') == '"1"'
    assert getattr(ast.statements[2], 'expr', '') == '"2"'

def test_json_serialization():
    """Test JSON serialization and deserialization of blocks"""
    # Create some blocks
    blocks = []
    for i in range(2):
        say_def = block_registry.get('say')
        if say_def:
            block = BlockInstance(
                block_id=f"block-{i}",
                definition=say_def,
                inputs={'expr': f'"{i}"'},
                position={'x': 50, 'y': 50 + (i * 100)}
            )
            blocks.append(block)
    
    # Serialize to JSON
    json_data = blocks_to_json(blocks)
    
    # Deserialize from JSON
    deserialized_blocks = json_to_blocks(json_data)
    
    # Should have same number of blocks
    assert len(deserialized_blocks) == len(blocks)
    
    # Should have same data
    for i, (original, deserialized) in enumerate(zip(blocks, deserialized_blocks)):
        assert original.id == deserialized.id
        assert original.inputs == deserialized.inputs
        assert original.position == deserialized.position
        assert original.definition['id'] == deserialized.definition['id']

def test_validate_round_trip_function():
    """Test the validate_round_trip function"""
    original_code = 'say "Hello, World!"'
    
    result = validate_round_trip(original_code)
    
    assert result['success'] == True
    assert result['original'] == original_code
    assert result['result'].strip() == original_code.strip()

def test_validate_round_trip_failure():
    """Test validate_round_trip with invalid code"""
    # This should fail gracefully
    result = validate_round_trip("invalid code that will cause errors")
    
    # Should not crash, but may not succeed
    assert 'success' in result
    assert 'original' in result

def test_block_registry():
    """Test block registry functionality"""
    # Test getting all blocks
    all_blocks = block_registry.get_all()
    assert len(all_blocks) > 0
    
    # Test getting specific blocks
    say_block = block_registry.get('say')
    assert say_block is not None
    assert say_block['id'] == 'say'
    
    # Test getting by AST type
    say_block_by_type = block_registry.get_by_ast_type('SayNode')
    assert say_block_by_type is not None
    assert say_block_by_type['id'] == 'say'
    
    # Test getting non-existent block
    non_existent = block_registry.get('non_existent')
    assert non_existent is None

def test_complex_program_roundtrip():
    """Test roundtrip for a complex program with multiple block types"""
    original_code = """import "math_utils"
let x = 10
let y = 20
if x > y:
  say "x is greater"
else:
  say "y is greater"
repeat 3 times:
  say "Loop iteration"
function add(a, b):
  let result = a + b
  say result"""
    
    ast1 = code_to_ast(original_code)
    blocks = ast_to_blocks(ast1)
    ast2 = blocks_to_ast(blocks)
    final_code = ast_to_code(ast2)
    
    # Should be semantically equivalent
    original_lines = [line.strip() for line in original_code.split('\n') if line.strip()]
    final_lines = [line.strip() for line in final_code.split('\n') if line.strip()]
    assert final_lines == original_lines

if __name__ == "__main__":
    pytest.main([__file__]) 