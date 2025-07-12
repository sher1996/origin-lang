// Transform library for blocks ↔ AST conversion
import type { BlockInstance, BlockDefinition } from '../blocks/definitions';
import { blockRegistry, getBlockDefinitionByAstType } from '../blocks/definitions';

export interface ASTNode {
  type: string;
  [key: string]: any;
}

export interface ASTProgram {
  statements: ASTNode[];
}

// Convert blocks to AST with improved ordering
export function blocksToAST(blocks: BlockInstance[]): ASTProgram {
  const statements: ASTNode[] = [];
  
  // Sort blocks by position (top to bottom, left to right)
  const sortedBlocks = [...blocks].sort((a, b) => {
    if (Math.abs(a.position.y - b.position.y) < 50) {
      // If blocks are roughly at the same height, sort by x position
      return a.position.x - b.position.x;
    }
    return a.position.y - b.position.y;
  });
  
  for (const block of sortedBlocks) {
    try {
      const astNode = block.definition.serialize(block.inputs);
      statements.push(astNode);
    } catch (error) {
      console.error(`Error serializing block ${block.id}:`, error);
      // Add a placeholder node to maintain structure
      statements.push({ type: 'ErrorNode', message: `Failed to serialize block ${block.id}` });
    }
  }
  
  return { statements };
}

// Convert AST to blocks with improved error handling
export function astToBlocks(ast: ASTProgram): BlockInstance[] {
  const blocks: BlockInstance[] = [];
  
  for (let i = 0; i < ast.statements.length; i++) {
    const astNode = ast.statements[i];
    const blockDef = getBlockDefinitionByAstType(astNode.type);
    
    if (blockDef) {
      try {
        const inputs = blockDef.deserialize(astNode);
        const blockInstance: BlockInstance = {
          id: `${blockDef.id}-${Date.now()}-${i}`,
          definition: blockDef,
          inputs,
          position: { x: 50, y: 50 + (i * 100) }, // Simple vertical layout
        };
        blocks.push(blockInstance);
      } catch (error) {
        console.error(`Error deserializing AST node ${astNode.type}:`, error);
        // Skip this node but continue processing
      }
    } else {
      console.warn(`Unknown AST node type: ${astNode.type}`);
    }
  }
  
  return blocks;
}

// Enhanced code generation from AST
export function astToCode(ast: ASTProgram): string {
  const lines: string[] = [];
  
  for (const node of ast.statements) {
    switch (node.type) {
      case 'SayNode':
        lines.push(`say ${node.expr}`);
        break;
      case 'LetNode':
        lines.push(`let ${node.name} = ${node.expr}`);
        break;
      case 'StringNode':
        lines.push(`"${node.value}"`);
        break;
      case 'NumberNode':
        lines.push(`${node.value}`);
        break;
      case 'ImportNode':
        lines.push(`import ${node.path}`);
        break;
      case 'RepeatNode':
        lines.push(`repeat ${node.count} times:`);
        if (node.body && Array.isArray(node.body)) {
          for (const bodyNode of node.body) {
            if (bodyNode.type === 'SayNode') {
              lines.push(`  say ${bodyNode.expr}`);
            } else if (bodyNode.type === 'LetNode') {
              lines.push(`  let ${bodyNode.name} = ${bodyNode.expr}`);
            }
          }
        }
        break;
      case 'IfNode':
        lines.push(`if ${node.condition}:`);
        if (node.thenBody && Array.isArray(node.thenBody)) {
          for (const thenNode of node.thenBody) {
            if (thenNode.type === 'SayNode') {
              lines.push(`  say ${thenNode.expr}`);
            } else if (thenNode.type === 'LetNode') {
              lines.push(`  let ${thenNode.name} = ${thenNode.expr}`);
            }
          }
        }
        if (node.elseBody && Array.isArray(node.elseBody) && node.elseBody.length > 0) {
          lines.push(`else:`);
          for (const elseNode of node.elseBody) {
            if (elseNode.type === 'SayNode') {
              lines.push(`  say ${elseNode.expr}`);
            } else if (elseNode.type === 'LetNode') {
              lines.push(`  let ${elseNode.name} = ${elseNode.expr}`);
            }
          }
        }
        break;
      case 'FunctionNode':
        const params = node.params ? node.params.join(', ') : '';
        lines.push(`function ${node.name}(${params}):`);
        if (node.body && Array.isArray(node.body)) {
          for (const bodyNode of node.body) {
            if (bodyNode.type === 'SayNode') {
              lines.push(`  say ${bodyNode.expr}`);
            } else if (bodyNode.type === 'LetNode') {
              lines.push(`  let ${bodyNode.name} = ${bodyNode.expr}`);
            }
          }
        }
        break;
      case 'ErrorNode':
        lines.push(`# Error: ${node.message}`);
        break;
      default:
        lines.push(`# Unknown node type: ${node.type}`);
    }
  }
  
  return lines.join('\n');
}

// Enhanced code parsing to AST
export function codeToAST(code: string): ASTProgram {
  const lines = code.split('\n').filter(line => line.trim());
  const statements: ASTNode[] = [];
  let indentLevel = 0;
  let currentBlock: any = null;
  
  for (const line of lines) {
    const trimmed = line.trim();
    
    if (trimmed.startsWith('say ')) {
      const expr = trimmed.substring(4).trim();
      statements.push({ type: 'SayNode', expr });
    } else if (trimmed.startsWith('let ')) {
      const match = trimmed.match(/let\s+(\w+)\s*=\s*(.+)/);
      if (match) {
        const [, name, expr] = match;
        statements.push({ type: 'LetNode', name: name.trim(), expr: expr.trim() });
      }
    } else if (trimmed.startsWith('import ')) {
      const path = trimmed.substring(7).trim();
      statements.push({ type: 'ImportNode', path });
    } else if (trimmed.startsWith('"') && trimmed.endsWith('"')) {
      const value = trimmed.slice(1, -1);
      statements.push({ type: 'StringNode', value });
    } else if (/^\d+(\.\d+)?$/.test(trimmed)) {
      const value = parseFloat(trimmed);
      statements.push({ type: 'NumberNode', value });
    } else if (trimmed.startsWith('repeat ') && trimmed.includes(' times:')) {
      const match = trimmed.match(/repeat\s+(\d+)\s+times:/);
      if (match) {
        const count = parseInt(match[1]);
        currentBlock = { type: 'RepeatNode', count, body: [] };
        statements.push(currentBlock);
      }
    } else if (trimmed.startsWith('if ') && trimmed.endsWith(':')) {
      const condition = trimmed.substring(3, trimmed.length - 1).trim();
      currentBlock = { type: 'IfNode', condition, thenBody: [], elseBody: null };
      statements.push(currentBlock);
    } else if (trimmed === 'else:') {
      if (currentBlock && currentBlock.type === 'IfNode') {
        currentBlock.elseBody = [];
      }
    } else if (trimmed.startsWith('function ') && trimmed.endsWith(':')) {
      const match = trimmed.match(/function\s+(\w+)\s*\(([^)]*)\):/);
      if (match) {
        const [, name, params] = match;
        const paramList = params ? params.split(',').map((p: string) => p.trim()) : [];
        currentBlock = { type: 'FunctionNode', name, params: paramList, body: [] };
        statements.push(currentBlock);
      }
    } else if (trimmed.startsWith('  ') && currentBlock) {
      // Handle indented code within blocks
      const innerLine = trimmed.substring(2);
      if (innerLine.startsWith('say ')) {
        const expr = innerLine.substring(4).trim();
        const innerNode = { type: 'SayNode', expr };
        if (currentBlock.body) {
          currentBlock.body.push(innerNode);
        } else if (currentBlock.thenBody) {
          currentBlock.thenBody.push(innerNode);
        } else if (currentBlock.elseBody) {
          currentBlock.elseBody.push(innerNode);
        }
      } else if (innerLine.startsWith('let ')) {
        const match = innerLine.match(/let\s+(\w+)\s*=\s*(.+)/);
        if (match) {
          const [, name, expr] = match;
          const innerNode = { type: 'LetNode', name: name.trim(), expr: expr.trim() };
          if (currentBlock.body) {
            currentBlock.body.push(innerNode);
          } else if (currentBlock.thenBody) {
            currentBlock.thenBody.push(innerNode);
          } else if (currentBlock.elseBody) {
            currentBlock.elseBody.push(innerNode);
          }
        }
      }
    } else if (trimmed.startsWith('#')) {
      // Skip comments
      continue;
    }
  }
  
  return { statements };
}

// Utility function to validate round-trip conversion
export function validateRoundTrip(originalCode: string): { success: boolean; original: string; result: string; error?: string } {
  try {
    const ast1 = codeToAST(originalCode);
    const blocks = astToBlocks(ast1);
    const ast2 = blocksToAST(blocks);
    const result = astToCode(ast2);
    
    return {
      success: true,
      original: originalCode,
      result
    };
  } catch (error) {
    return {
      success: false,
      original: originalCode,
      result: '',
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

// Export/Import utilities for JSON serialization
export function blocksToJSON(blocks: BlockInstance[]): string {
  const serializableBlocks = blocks.map(block => ({
    id: block.id,
    definitionId: block.definition.id,
    inputs: block.inputs,
    position: block.position
  }));
  
  return JSON.stringify(serializableBlocks, null, 2);
}

export function jsonToBlocks(jsonData: string): BlockInstance[] {
  const data = JSON.parse(jsonData);
  const blocks: BlockInstance[] = [];
  
  for (const blockData of data) {
    const definition = blockRegistry.get(blockData.definitionId);
    if (definition) {
      const blockInstance: BlockInstance = {
        id: blockData.id,
        definition,
        inputs: blockData.inputs,
        position: blockData.position
      };
      blocks.push(blockInstance);
    }
  }
  
  return blocks;
} 