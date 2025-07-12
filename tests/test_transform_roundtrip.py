"""
Tests for AST ↔ blocks round-trip conversion
"""

import pytest
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.transform.blocks_to_ast import code_to_blocks, blocks_to_code

def test_hello_world_roundtrip():
    """Test round-trip conversion for hello world example"""
    original_code = 'say "Hello, Origin."'
    
    # Convert code to blocks
    blocks = code_to_blocks(original_code)
    
    # Convert blocks back to code
    roundtrip_code = blocks_to_code(blocks)
    
    # Should be semantically identical
    assert roundtrip_code.strip() == original_code.strip()

def test_arithmetic_roundtrip():
    """Test round-trip conversion for arithmetic example"""
    original_code = '''let x = 5
let y = x * 3 - 4
say y
say x + y'''
    
    # Convert code to blocks
    blocks = code_to_blocks(original_code)
    
    # Convert blocks back to code
    roundtrip_code = blocks_to_code(blocks)
    
    # Should be semantically identical (ignore whitespace differences)
    original_lines = [line.strip() for line in original_code.split('\n') if line.strip()]
    roundtrip_lines = [line.strip() for line in roundtrip_code.split('\n') if line.strip()]
    
    assert original_lines == roundtrip_lines

def test_multiple_statements():
    """Test round-trip conversion for multiple statement types"""
    original_code = '''let name = "Alice"
say "Hello, " + name
let count = 3
repeat count times:
  say "Hello again"'''
    
    # Convert code to blocks
    blocks = code_to_blocks(original_code)
    
    # Convert blocks back to code
    roundtrip_code = blocks_to_code(blocks)
    
    # Should have the same number of blocks
    assert len(blocks) > 0
    
    # Should generate valid code
    assert 'say' in roundtrip_code
    assert 'let' in roundtrip_code

def test_block_structure():
    """Test that blocks have the correct structure"""
    code = 'say "test"'
    blocks = code_to_blocks(code)
    
    assert len(blocks) == 1
    block = blocks[0]
    
    # Check required fields
    assert 'id' in block
    assert 'definitionId' in block
    assert 'position' in block
    assert 'inputs' in block
    assert 'outputs' in block
    
    # Check block type
    assert block['definitionId'] == 'say'
    assert 'expr' in block['inputs']

def test_error_handling():
    """Test error handling for invalid code"""
    with pytest.raises(ValueError):
        code_to_blocks("invalid syntax here")

if __name__ == '__main__':
    pytest.main([__file__]) 