"""
Transform functions for AST ↔ blocks mapping (Python version)
Mirrors the TypeScript transform.ts functionality
"""

import json
from typing import List, Dict, Any, Optional
import sys
import os

# Add the parent directory to the path so we can import the parser
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import Parser, Node, SayNode, LetNode, RepeatNode, FuncDefNode, FuncCallNode, ImportNode, StringNode
from lexer import tokenize

# Block definitions (mirror of TypeScript version)
BLOCK_DEFINITIONS = {
    'say': {
        'id': 'say',
        'label': 'Say',
        'astType': 'SayNode',
        'inputs': [
            {'id': 'expr', 'label': 'Expression', 'type': 'expression', 'required': True}
        ],
        'outputs': [
            {'id': 'statement', 'label': 'Statement', 'type': 'statement'}
        ]
    },
    'let': {
        'id': 'let',
        'label': 'Let',
        'astType': 'LetNode',
        'inputs': [
            {'id': 'name', 'label': 'Variable Name', 'type': 'string', 'required': True},
            {'id': 'expr', 'label': 'Expression', 'type': 'expression', 'required': True}
        ],
        'outputs': [
            {'id': 'statement', 'label': 'Statement', 'type': 'statement'}
        ]
    },
    'repeat': {
        'id': 'repeat',
        'label': 'Repeat',
        'astType': 'RepeatNode',
        'inputs': [
            {'id': 'count', 'label': 'Count', 'type': 'number', 'required': True}
        ],
        'outputs': [
            {'id': 'statement', 'label': 'Statement', 'type': 'statement'}
        ]
    },
    'define': {
        'id': 'define',
        'label': 'Define Function',
        'astType': 'FuncDefNode',
        'inputs': [
            {'id': 'name', 'label': 'Function Name', 'type': 'string', 'required': True},
            {'id': 'params', 'label': 'Parameters', 'type': 'string', 'required': False}
        ],
        'outputs': [
            {'id': 'statement', 'label': 'Statement', 'type': 'statement'}
        ]
    },
    'call': {
        'id': 'call',
        'label': 'Call Function',
        'astType': 'FuncCallNode',
        'inputs': [
            {'id': 'name', 'label': 'Function Name', 'type': 'string', 'required': True},
            {'id': 'args', 'label': 'Arguments', 'type': 'string', 'required': False}
        ],
        'outputs': [
            {'id': 'expression', 'label': 'Expression', 'type': 'value'}
        ]
    },
    'import': {
        'id': 'import',
        'label': 'Import',
        'astType': 'ImportNode',
        'inputs': [
            {'id': 'path', 'label': 'Path', 'type': 'string', 'required': True}
        ],
        'outputs': [
            {'id': 'statement', 'label': 'Statement', 'type': 'statement'}
        ]
    },
    'string': {
        'id': 'string',
        'label': 'String',
        'astType': 'StringNode',
        'inputs': [
            {'id': 'value', 'label': 'Value', 'type': 'string', 'required': True}
        ],
        'outputs': [
            {'id': 'value', 'label': 'Value', 'type': 'value'}
        ]
    }
}

def blocks_to_ast(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert blocks to AST nodes"""
    ast_nodes = []
    for block in blocks:
        definition_id = block['definitionId']
        definition = BLOCK_DEFINITIONS.get(definition_id)
        if not definition:
            raise ValueError(f"Unknown block definition: {definition_id}")
        
        # Create AST node based on block type
        inputs = block.get('inputs', {})
        if definition_id == 'say':
            ast_nodes.append({'type': 'SayNode', 'expr': inputs.get('expr', '')})
        elif definition_id == 'let':
            ast_nodes.append({'type': 'LetNode', 'name': inputs.get('name', ''), 'expr': inputs.get('expr', '')})
        elif definition_id == 'repeat':
            ast_nodes.append({'type': 'RepeatNode', 'count': inputs.get('count', 1), 'body': []})
        elif definition_id == 'define':
            ast_nodes.append({'type': 'FuncDefNode', 'name': inputs.get('name', ''), 'params': inputs.get('params', '').split(',') if inputs.get('params') else [], 'body': []})
        elif definition_id == 'call':
            ast_nodes.append({'type': 'FuncCallNode', 'name': inputs.get('name', ''), 'args': inputs.get('args', '').split(',') if inputs.get('args') else []})
        elif definition_id == 'import':
            ast_nodes.append({'type': 'ImportNode', 'path': inputs.get('path', '')})
        elif definition_id == 'string':
            ast_nodes.append({'type': 'StringNode', 'value': inputs.get('value', '')})
    
    return ast_nodes

def ast_to_blocks(ast_nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert AST nodes to blocks"""
    blocks = []
    for i, node in enumerate(ast_nodes):
        node_type = node['type']
        
        # Find the block definition that matches this AST node type
        definition = None
        for def_id, def_info in BLOCK_DEFINITIONS.items():
            if def_info['astType'] == node_type:
                definition = def_info
                definition_id = def_id
                break
        
        if not definition:
            raise ValueError(f"Unknown AST node type: {node_type}")
        
        # Extract inputs from the AST node
        inputs = {}
        if node_type == 'SayNode':
            inputs['expr'] = node.get('expr', '')
        elif node_type == 'LetNode':
            inputs['name'] = node.get('name', '')
            inputs['expr'] = node.get('expr', '')
        elif node_type == 'RepeatNode':
            inputs['count'] = node.get('count', 1)
        elif node_type == 'FuncDefNode':
            inputs['name'] = node.get('name', '')
            inputs['params'] = ','.join(node.get('params', []))
        elif node_type == 'FuncCallNode':
            inputs['name'] = node.get('name', '')
            inputs['args'] = ','.join(node.get('args', []))
        elif node_type == 'ImportNode':
            inputs['path'] = node.get('path', '')
        elif node_type == 'StringNode':
            inputs['value'] = node.get('value', '')
        
        blocks.append({
            'id': f"{definition_id}-{i}",
            'definitionId': definition_id,
            'position': {'x': i * 200, 'y': i * 100},
            'inputs': inputs,
            'outputs': {}
        })
    
    return blocks

def blocks_to_code(blocks: List[Dict[str, Any]]) -> str:
    """Generate Origin code from blocks"""
    ast_nodes = blocks_to_ast(blocks)
    code_lines = []
    
    for node in ast_nodes:
        node_type = node['type']
        if node_type == 'SayNode':
            code_lines.append(f"say {node['expr']}")
        elif node_type == 'LetNode':
            code_lines.append(f"let {node['name']} = {node['expr']}")
        elif node_type == 'RepeatNode':
            code_lines.append(f"repeat {node['count']} times:")
            # Handle body if present
            body = node.get('body', [])
            for stmt in body:
                if stmt['type'] == 'SayNode':
                    code_lines.append(f"  say {stmt['expr']}")
                elif stmt['type'] == 'LetNode':
                    code_lines.append(f"  let {stmt['name']} = {stmt['expr']}")
        elif node_type == 'FuncDefNode':
            params = ','.join(node.get('params', []))
            code_lines.append(f"define {node['name']}({params}):")
            # Handle body if present
            body = node.get('body', [])
            for stmt in body:
                if stmt['type'] == 'SayNode':
                    code_lines.append(f"  say {stmt['expr']}")
                elif stmt['type'] == 'LetNode':
                    code_lines.append(f"  let {stmt['name']} = {stmt['expr']}")
        elif node_type == 'FuncCallNode':
            args = ','.join(node.get('args', []))
            code_lines.append(f"{node['name']}({args})")
        elif node_type == 'ImportNode':
            code_lines.append(f"import {node['path']}")
        elif node_type == 'StringNode':
            code_lines.append(f'"{node["value"]}"')
    
    return '\n'.join(code_lines)

def code_to_blocks(code: str) -> List[Dict[str, Any]]:
    """Parse Origin code to blocks"""
    try:
        tokens = tokenize(code)
        parser = Parser(tokens)
        ast_nodes = parser.parse()
        
        # Convert AST nodes to a format we can work with
        serialized_nodes = []
        for node in ast_nodes:
            if isinstance(node, SayNode):
                serialized_nodes.append({'type': 'SayNode', 'expr': node.expr})
            elif isinstance(node, LetNode):
                serialized_nodes.append({'type': 'LetNode', 'name': node.name, 'expr': node.expr})
            elif isinstance(node, RepeatNode):
                serialized_nodes.append({'type': 'RepeatNode', 'count': node.count, 'body': []})
            elif isinstance(node, FuncDefNode):
                serialized_nodes.append({'type': 'FuncDefNode', 'name': node.name, 'params': node.params, 'body': []})
            elif isinstance(node, FuncCallNode):
                serialized_nodes.append({'type': 'FuncCallNode', 'name': node.name, 'args': node.args})
            elif isinstance(node, ImportNode):
                serialized_nodes.append({'type': 'ImportNode', 'path': node.path})
            elif isinstance(node, StringNode):
                serialized_nodes.append({'type': 'StringNode', 'value': node.value})
        
        return ast_to_blocks(serialized_nodes)
    except Exception as e:
        raise ValueError(f"Error parsing code: {e}")

def main():
    """CLI interface for the transform functions"""
    if len(sys.argv) < 3:
        print("Usage: python blocks_to_ast.py <command> <input_file> [output_file]")
        print("Commands: import, export")
        sys.exit(1)
    
    command = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    try:
        if command == 'import':
            # Import .origin file to JSON blocks
            with open(input_file, 'r') as f:
                code = f.read()
            
            blocks = code_to_blocks(code)
            output = json.dumps(blocks, indent=2)
            
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(output)
            else:
                print(output)
                
        elif command == 'export':
            # Export JSON blocks to .origin file
            with open(input_file, 'r') as f:
                blocks = json.load(f)
            
            code = blocks_to_code(blocks)
            
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(code)
            else:
                print(code)
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 