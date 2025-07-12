#!/usr/bin/env python3
"""
Simple test runner for visual mode functionality
"""

import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.transform.blocks_to_ast import (
    code_to_ast, ast_to_blocks, blocks_to_ast, ast_to_code,
    blocks_to_json, json_to_blocks, validate_round_trip,
    BlockInstance, block_registry
)

def test_hello_world_roundtrip():
    """Test roundtrip for hello world program"""
    print("Testing hello world roundtrip...")
    original_code = 'say "Hello, Origin."'
    
    # Code → AST → Blocks → AST → Code
    ast1 = code_to_ast(original_code)
    blocks = ast_to_blocks(ast1)
    ast2 = blocks_to_ast(blocks)
    final_code = ast_to_code(ast2)
    
    # Should be semantically equivalent
    success = final_code.strip() == original_code.strip()
    print(f"  {'✅ PASS' if success else '❌ FAIL'}")
    if not success:
        print(f"    Original: {original_code}")
        print(f"    Result:   {final_code}")
    return success

def test_arithmetic_roundtrip():
    """Test roundtrip for arithmetic program"""
    print("Testing arithmetic roundtrip...")
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
    success = final_lines == original_lines
    print(f"  {'✅ PASS' if success else '❌ FAIL'}")
    if not success:
        print(f"    Original: {original_lines}")
        print(f"    Result:   {final_lines}")
    return success

def test_complex_program_roundtrip():
    """Test roundtrip for a complex program with multiple block types"""
    print("Testing complex program roundtrip...")
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
    success = final_lines == original_lines
    print(f"  {'✅ PASS' if success else '❌ FAIL'}")
    if not success:
        print(f"    Original: {original_lines}")
        print(f"    Result:   {final_lines}")
    return success

def test_json_serialization():
    """Test JSON serialization and deserialization of blocks"""
    print("Testing JSON serialization...")
    
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
    success = len(deserialized_blocks) == len(blocks)
    print(f"  {'✅ PASS' if success else '❌ FAIL'}")
    if not success:
        print(f"    Original count: {len(blocks)}")
        print(f"    Deserialized count: {len(deserialized_blocks)}")
    return success

def test_block_registry():
    """Test block registry functionality"""
    print("Testing block registry...")
    
    # Test getting all blocks
    all_blocks = block_registry.get_all()
    success1 = len(all_blocks) > 0
    
    # Test getting specific blocks
    say_block = block_registry.get('say')
    success2 = say_block is not None and say_block['id'] == 'say'
    
    # Test getting by AST type
    say_block_by_type = block_registry.get_by_ast_type('SayNode')
    success3 = say_block_by_type is not None and say_block_by_type['id'] == 'say'
    
    # Test getting non-existent block
    non_existent = block_registry.get('non_existent')
    success4 = non_existent is None
    
    success = success1 and success2 and success3 and success4
    print(f"  {'✅ PASS' if success else '❌ FAIL'}")
    return success

def test_validate_round_trip_function():
    """Test the validate_round_trip function"""
    print("Testing validate_round_trip function...")
    original_code = 'say "Hello, World!"'
    
    result = validate_round_trip(original_code)
    
    success = result['success'] and result['result'].strip() == original_code.strip()
    print(f"  {'✅ PASS' if success else '❌ FAIL'}")
    if not success:
        print(f"    Error: {result.get('error', 'Unknown error')}")
    return success

def main():
    """Run all visual mode tests"""
    print("Running Visual Mode Tests")
    print("=" * 40)
    
    tests = [
        test_hello_world_roundtrip,
        test_arithmetic_roundtrip,
        test_complex_program_roundtrip,
        test_json_serialization,
        test_block_registry,
        test_validate_round_trip_function,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ❌ FAIL - Exception: {e}")
    
    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 