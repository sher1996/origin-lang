"""
Transform library for blocks ↔ AST conversion
Mirrors the TypeScript implementation in visual/src/lib/transform.ts
"""

from typing import List, Dict, Any, Optional
import json
import sys
import os

# Add the parent directory to the path to import parser and runtime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import parser modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import parser

class ASTNode:
    """Generic AST node for transformation"""
    def __init__(self, node_type: str, **kwargs):
        self.type = node_type
        for key, value in kwargs.items():
            setattr(self, key, value)

class ASTProgram:
    """AST program container"""
    def __init__(self, statements: List[ASTNode]):
        self.statements = statements

class BlockInstance:
    """Visual block instance with data"""
    def __init__(self, block_id: str, definition: Dict[str, Any], inputs: Dict[str, Any], position: Dict[str, int]):
        self.id = block_id
        self.definition = definition
        self.inputs = inputs
        self.position = position

class BlockRegistry:
    """Block registry for managing block definitions"""
    def __init__(self):
        self.definitions = {}
        self.ast_type_map = {}
        self._register_default_blocks()
    
    def _register_default_blocks(self):
        """Register all default block definitions"""
        blocks = [
            {
                'id': 'say',
                'label': 'Say',
                'astType': 'SayNode',
                'inputs': [{'id': 'expr', 'label': 'Expression', 'type': 'expression', 'required': True}],
                'outputs': [],
                'serialize': lambda inputs: ASTNode('SayNode', expr=inputs['expr']),
                'deserialize': lambda ast_node: {'expr': ast_node.expr},
                'color': 'blue',
            },
            {
                'id': 'let',
                'label': 'Let',
                'astType': 'LetNode',
                'inputs': [
                    {'id': 'name', 'label': 'Variable Name', 'type': 'identifier', 'required': True},
                    {'id': 'expr', 'label': 'Expression', 'type': 'expression', 'required': True}
                ],
                'outputs': [{'id': 'name', 'label': 'Variable', 'type': 'identifier'}],
                'serialize': lambda inputs: ASTNode('LetNode', name=inputs['name'], expr=inputs['expr']),
                'deserialize': lambda ast_node: {'name': ast_node.name, 'expr': ast_node.expr},
                'color': 'green',
            },
            {
                'id': 'string',
                'label': 'String',
                'astType': 'StringNode',
                'inputs': [{'id': 'value', 'label': 'Value', 'type': 'string', 'required': True, 'defaultValue': ''}],
                'outputs': [{'id': 'value', 'label': 'String', 'type': 'string'}],
                'serialize': lambda inputs: ASTNode('StringNode', value=inputs['value']),
                'deserialize': lambda ast_node: {'value': ast_node.value},
                'color': 'orange',
            },
            {
                'id': 'number',
                'label': 'Number',
                'astType': 'NumberNode',
                'inputs': [{'id': 'value', 'label': 'Value', 'type': 'number', 'required': True, 'defaultValue': 0}],
                'outputs': [{'id': 'value', 'label': 'Number', 'type': 'number'}],
                'serialize': lambda inputs: ASTNode('NumberNode', value=inputs['value']),
                'deserialize': lambda ast_node: {'value': ast_node.value},
                'color': 'purple',
            },
            {
                'id': 'import',
                'label': 'Import',
                'astType': 'ImportNode',
                'inputs': [{'id': 'path', 'label': 'Path', 'type': 'string', 'required': True, 'defaultValue': ''}],
                'outputs': [],
                'serialize': lambda inputs: ASTNode('ImportNode', path=inputs['path']),
                'deserialize': lambda ast_node: {'path': ast_node.path},
                'color': 'gray',
            },
            {
                'id': 'repeat',
                'label': 'Repeat',
                'astType': 'RepeatNode',
                'inputs': [
                    {'id': 'count', 'label': 'Count', 'type': 'number', 'required': True, 'defaultValue': 1},
                    {'id': 'body', 'label': 'Body', 'type': 'expression', 'required': True}
                ],
                'outputs': [],
                'serialize': lambda inputs: ASTNode('RepeatNode', count=inputs['count'], body=inputs['body']),
                'deserialize': lambda ast_node: {'count': ast_node.count, 'body': ast_node.body},
                'color': 'indigo',
            },
            {
                'id': 'if',
                'label': 'If',
                'astType': 'IfNode',
                'inputs': [
                    {'id': 'condition', 'label': 'Condition', 'type': 'expression', 'required': True},
                    {'id': 'thenBody', 'label': 'Then', 'type': 'expression', 'required': True},
                    {'id': 'elseBody', 'label': 'Else', 'type': 'expression', 'required': False}
                ],
                'outputs': [],
                'serialize': lambda inputs: ASTNode('IfNode', condition=inputs['condition'], thenBody=inputs['thenBody'], elseBody=inputs.get('elseBody')),
                'deserialize': lambda ast_node: {'condition': ast_node.condition, 'thenBody': ast_node.thenBody, 'elseBody': getattr(ast_node, 'elseBody', None)},
                'color': 'yellow',
            },
            {
                'id': 'function',
                'label': 'Function',
                'astType': 'FunctionNode',
                'inputs': [
                    {'id': 'name', 'label': 'Name', 'type': 'identifier', 'required': True},
                    {'id': 'params', 'label': 'Parameters', 'type': 'string', 'required': False, 'defaultValue': ''},
                    {'id': 'body', 'label': 'Body', 'type': 'expression', 'required': True}
                ],
                'outputs': [{'id': 'name', 'label': 'Function', 'type': 'identifier'}],
                'serialize': lambda inputs: ASTNode('FunctionNode', name=inputs['name'], params=inputs['params'].split(',') if inputs['params'] else [], body=inputs['body']),
                'deserialize': lambda ast_node: {'name': ast_node.name, 'params': ', '.join(ast_node.params) if hasattr(ast_node, 'params') else '', 'body': ast_node.body},
                'color': 'teal',
            },
        ]
        
        for block in blocks:
            self.register(block)
    
    def register(self, definition: Dict[str, Any]):
        """Register a block definition"""
        self.definitions[definition['id']] = definition
        self.ast_type_map[definition['astType']] = definition
    
    def get(self, block_id: str) -> Optional[Dict[str, Any]]:
        """Get block definition by ID"""
        return self.definitions.get(block_id)
    
    def get_by_ast_type(self, ast_type: str) -> Optional[Dict[str, Any]]:
        """Get block definition by AST type"""
        return self.ast_type_map.get(ast_type)
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all block definitions"""
        return list(self.definitions.values())

# Global block registry instance
block_registry = BlockRegistry()

def blocks_to_ast(blocks: List[BlockInstance]) -> ASTProgram:
    """Convert blocks to AST with improved ordering"""
    statements = []
    
    # Sort blocks by position (top to bottom, left to right)
    sorted_blocks = sorted(blocks, key=lambda b: (b.position['y'], b.position['x']))
    
    for block in sorted_blocks:
        try:
            # Use the serialize function from the block definition
            if 'serialize' in block.definition:
                ast_node = block.definition['serialize'](block.inputs)
                statements.append(ast_node)
        except Exception as e:
            print(f"Error serializing block {block.id}: {e}")
            # Add a placeholder node to maintain structure
            statements.append(ASTNode('ErrorNode', message=f"Failed to serialize block {block.id}"))
    
    return ASTProgram(statements)

def ast_to_blocks(ast: ASTProgram) -> List[BlockInstance]:
    """Convert AST to blocks with improved error handling"""
    blocks = []
    
    for i, ast_node in enumerate(ast.statements):
        block_def = block_registry.get_by_ast_type(ast_node.type)
        
        if block_def:
            try:
                inputs = block_def['deserialize'](ast_node)
                block_instance = BlockInstance(
                    block_id=f"{block_def['id']}-{i}",
                    definition=block_def,
                    inputs=inputs,
                    position={'x': 50, 'y': 50 + (i * 100)}  # Simple vertical layout
                )
                blocks.append(block_instance)
            except Exception as e:
                print(f"Error deserializing AST node {ast_node.type}: {e}")
                # Skip this node but continue processing
        else:
            print(f"Unknown AST node type: {ast_node.type}")
    
    return blocks

def ast_to_code(ast: ASTProgram) -> str:
    """Enhanced code generation from AST"""
    lines = []
    
    for node in ast.statements:
        if node.type == 'SayNode':
            lines.append(f"say {getattr(node, 'expr', '')}")
        elif node.type == 'LetNode':
            lines.append(f"let {getattr(node, 'name', '')} = {getattr(node, 'expr', '')}")
        elif node.type == 'StringNode':
            lines.append(f'"{getattr(node, "value", "")}"')
        elif node.type == 'NumberNode':
            lines.append(f"{getattr(node, 'value', '')}")
        elif node.type == 'ImportNode':
            lines.append(f"import {getattr(node, 'path', '')}")
        elif node.type == 'RepeatNode':
            lines.append(f"repeat {getattr(node, 'count', '')} times:")
            body = getattr(node, 'body', None)
            if body:
                for body_node in body:
                    if body_node.type == 'SayNode':
                        lines.append(f"  say {getattr(body_node, 'expr', '')}")
                    elif body_node.type == 'LetNode':
                        lines.append(f"  let {getattr(body_node, 'name', '')} = {getattr(body_node, 'expr', '')}")
        elif node.type == 'IfNode':
            lines.append(f"if {getattr(node, 'condition', '')}:")
            then_body = getattr(node, 'thenBody', None)
            if then_body:
                for then_node in then_body:
                    if then_node.type == 'SayNode':
                        lines.append(f"  say {getattr(then_node, 'expr', '')}")
                    elif then_node.type == 'LetNode':
                        lines.append(f"  let {getattr(then_node, 'name', '')} = {getattr(then_node, 'expr', '')}")
            else_body = getattr(node, 'elseBody', None)
            if else_body is not None:
                lines.append("else:")
                if len(else_body) > 0:
                    for else_node in else_body:
                        if else_node.type == 'SayNode':
                            lines.append(f"  say {getattr(else_node, 'expr', '')}")
                        elif else_node.type == 'LetNode':
                            lines.append(f"  let {getattr(else_node, 'name', '')} = {getattr(else_node, 'expr', '')}")
        elif node.type == 'FunctionNode':
            params = getattr(node, 'params', [])
            # Ensure params are joined with a single comma and space
            param_str = ', '.join([p.strip() for p in params]) if params else ''
            lines.append(f"function {getattr(node, 'name', '')}({param_str}):")
            body = getattr(node, 'body', None)
            if body:
                for body_node in body:
                    if body_node.type == 'SayNode':
                        lines.append(f"  say {getattr(body_node, 'expr', '')}")
                    elif body_node.type == 'LetNode':
                        lines.append(f"  let {getattr(body_node, 'name', '')} = {getattr(body_node, 'expr', '')}")
        elif node.type == 'ErrorNode':
            lines.append(f"# Error: {getattr(node, 'message', '')}")
        else:
            lines.append(f"# Unknown node type: {node.type}")
    
    return '\n'.join(lines)

def code_to_ast(code: str) -> ASTProgram:
    """Enhanced code parsing to AST with correct if/else branch association and param trimming"""
    lines = [line.rstrip() for line in code.split('\n') if line.strip()]
    statements = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.startswith('say '):
            expr = line[4:].strip()
            statements.append(ASTNode('SayNode', expr=expr))
            i += 1
        elif line.startswith('let '):
            parts = line[4:].split('=', 1)
            if len(parts) == 2:
                name = parts[0].strip()
                expr = parts[1].strip()
                statements.append(ASTNode('LetNode', name=name, expr=expr))
            i += 1
        elif line.startswith('import '):
            path = line[7:].strip()
            statements.append(ASTNode('ImportNode', path=path))
            i += 1
        elif line.startswith('"') and line.endswith('"'):
            value = line[1:-1]
            statements.append(ASTNode('StringNode', value=value))
            i += 1
        elif line.replace('.', '').replace('-', '').isdigit():
            value = float(line)
            statements.append(ASTNode('NumberNode', value=value))
            i += 1
        elif line.startswith('repeat ') and ' times:' in line:
            count_part = line[7:].split(' times:')[0]
            try:
                count = int(count_part)
                body = []
                i += 1
                while i < n and lines[i].startswith('  '):
                    inner_line = lines[i][2:]
                    if inner_line.startswith('say '):
                        expr = inner_line[4:].strip()
                        body.append(ASTNode('SayNode', expr=expr))
                    elif inner_line.startswith('let '):
                        parts = inner_line[4:].split('=', 1)
                        if len(parts) == 2:
                            name = parts[0].strip()
                            expr = parts[1].strip()
                            body.append(ASTNode('LetNode', name=name, expr=expr))
                    i += 1
                statements.append(ASTNode('RepeatNode', count=count, body=body))
            except ValueError:
                i += 1
        elif line.startswith('if ') and line.endswith(':'):
            condition = line[3:-1].strip()
            thenBody = []
            elseBody = None
            i += 1
            while i < n and lines[i].startswith('  '):
                inner_line = lines[i][2:]
                if inner_line.startswith('say '):
                    expr = inner_line[4:].strip()
                    thenBody.append(ASTNode('SayNode', expr=expr))
                elif inner_line.startswith('let '):
                    parts = inner_line[4:].split('=', 1)
                    if len(parts) == 2:
                        name = parts[0].strip()
                        expr = parts[1].strip()
                        thenBody.append(ASTNode('LetNode', name=name, expr=expr))
                i += 1
            if i < n and lines[i].strip() == 'else:':
                elseBody = []
                i += 1
                while i < n and lines[i].startswith('  '):
                    inner_line = lines[i][2:]
                    if inner_line.startswith('say '):
                        expr = inner_line[4:].strip()
                        elseBody.append(ASTNode('SayNode', expr=expr))
                    elif inner_line.startswith('let '):
                        parts = inner_line[4:].split('=', 1)
                        if len(parts) == 2:
                            name = parts[0].strip()
                            expr = parts[1].strip()
                            elseBody.append(ASTNode('LetNode', name=name, expr=expr))
                    i += 1
            statements.append(ASTNode('IfNode', condition=condition, thenBody=thenBody, elseBody=elseBody))
        elif line.startswith('function ') and line.endswith(':'):
            func_part = line[9:-1]
            if '(' in func_part and ')' in func_part:
                name_part = func_part.split('(')[0].strip()
                params_part = func_part.split('(')[1].split(')')[0].strip()
                params = [p.strip() for p in params_part.split(',')] if params_part else []
                body = []
                i += 1
                while i < n and lines[i].startswith('  '):
                    inner_line = lines[i][2:]
                    if inner_line.startswith('say '):
                        expr = inner_line[4:].strip()
                        body.append(ASTNode('SayNode', expr=expr))
                    elif inner_line.startswith('let '):
                        parts = inner_line[4:].split('=', 1)
                        if len(parts) == 2:
                            name = parts[0].strip()
                            expr = parts[1].strip()
                            body.append(ASTNode('LetNode', name=name, expr=expr))
                    i += 1
                statements.append(ASTNode('FunctionNode', name=name_part, params=params, body=body))
        elif line.startswith('#'):
            i += 1
        else:
            i += 1
    return ASTProgram(statements)

def auto_layout_blocks(blocks: List[BlockInstance], start_x: int = 50, start_y: int = 50, spacing_y: int = 100) -> List[BlockInstance]:
    """Apply simple vertical layout to blocks"""
    for i, block in enumerate(blocks):
        block.position = {'x': start_x, 'y': start_y + (i * spacing_y)}
    return blocks

def validate_round_trip(original_code: str) -> Dict[str, Any]:
    """Validate round-trip conversion"""
    try:
        ast1 = code_to_ast(original_code)
        blocks = ast_to_blocks(ast1)
        ast2 = blocks_to_ast(blocks)
        result = ast_to_code(ast2)
        
        return {
            'success': True,
            'original': original_code,
            'result': result
        }
    except Exception as e:
        return {
            'success': False,
            'original': original_code,
            'result': '',
            'error': str(e)
        }

def blocks_to_json(blocks: List[BlockInstance]) -> str:
    """Convert blocks to JSON format"""
    serializable_blocks = []
    for block in blocks:
        block_data = {
            'id': block.id,
            'definitionId': block.definition['id'],
            'inputs': block.inputs,
            'position': block.position
        }
        serializable_blocks.append(block_data)
    
    return json.dumps(serializable_blocks, indent=2)

def json_to_blocks(json_data: str) -> List[BlockInstance]:
    """Convert JSON to blocks"""
    data = json.loads(json_data)
    blocks = []
    
    for block_data in data:
        definition = block_registry.get(block_data['definitionId'])
        if definition:
            block_instance = BlockInstance(
                block_id=block_data['id'],
                definition=definition,
                inputs=block_data['inputs'],
                position=block_data['position']
            )
            blocks.append(block_instance)
    
    return blocks

def main():
    """CLI interface for testing"""
    if len(sys.argv) < 3:
        print("Usage: python blocks_to_ast.py <command> <input_file> [output_file]")
        print("Commands: import, export, validate")
        return
    
    command = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    if command == 'import':
        # Import .origin file and export as JSON blocks
        with open(input_file, 'r') as f:
            code = f.read()
        
        ast = code_to_ast(code)
        blocks = ast_to_blocks(ast)
        blocks = auto_layout_blocks(blocks)
        
        # Convert to JSON-serializable format
        blocks_data = []
        for block in blocks:
            block_data = {
                'id': block.id,
                'definition': block.definition,
                'inputs': block.inputs,
                'position': block.position
            }
            blocks_data.append(block_data)
        
        output = output_file or input_file.replace('.origin', '.json')
        with open(output, 'w') as f:
            json.dump(blocks_data, f, indent=2)
        
        print(f"Imported {input_file} -> {output}")
        
    elif command == 'export':
        # Import JSON blocks and export as .origin file
        with open(input_file, 'r') as f:
            blocks_data = json.load(f)
        
        # Convert back to BlockInstance objects
        blocks = []
        for block_data in blocks_data:
            block = BlockInstance(
                block_id=block_data['id'],
                definition=block_data['definition'],
                inputs=block_data['inputs'],
                position=block_data['position']
            )
            blocks.append(block)
        
        ast = blocks_to_ast(blocks)
        code = ast_to_code(ast)
        
        output = output_file or input_file.replace('.json', '.origin')
        with open(output, 'w') as f:
            f.write(code)
        
        print(f"Exported {input_file} -> {output}")
    
    elif command == 'validate':
        # Validate round-trip conversion
        with open(input_file, 'r') as f:
            code = f.read()
        
        result = validate_round_trip(code)
        if result['success']:
            print("✅ Round-trip validation passed!")
            print(f"Original: {result['original']}")
            print(f"Result: {result['result']}")
        else:
            print("❌ Round-trip validation failed!")
            print(f"Error: {result['error']}")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == '__main__':
    main() 