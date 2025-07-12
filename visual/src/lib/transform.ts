// Transform functions for AST ↔ blocks mapping
import type { BlockInstance, ASTNode } from '../blocks/definitions';
import { BLOCK_DEFINITIONS } from '../blocks/definitions';

// Convert blocks to AST nodes
export function blocksToAST(blocks: BlockInstance[]): ASTNode[] {
  return blocks.map(block => {
    const definition = BLOCK_DEFINITIONS[block.definitionId];
    if (!definition) {
      throw new Error(`Unknown block definition: ${block.definitionId}`);
    }
    
    return definition.serialize(block.inputs);
  });
}

// Convert AST nodes to blocks
export function astToBlocks(astNodes: ASTNode[]): BlockInstance[] {
  return astNodes.map((node, index) => {
    // Find the block definition that matches this AST node type
    const definition = Object.values(BLOCK_DEFINITIONS).find(def => def.astType === node.type);
    if (!definition) {
      throw new Error(`Unknown AST node type: ${node.type}`);
    }
    
    // Extract inputs from the AST node
    const inputs = definition.deserialize(node);
    
    return {
      id: `${definition.id}-${index}-${Date.now()}`,
      definitionId: definition.id,
      position: { x: index * 200, y: index * 100 }, // Simple layout
      inputs,
      outputs: {},
    };
  });
}

// Generate Origin code from blocks
export function blocksToCode(blocks: BlockInstance[]): string {
  const astNodes = blocksToAST(blocks);
  return astNodes.map(node => {
    switch (node.type) {
      case 'SayNode':
        return `say ${node.expr}`;
      case 'LetNode':
        return `let ${node.name} = ${node.expr}`;
      case 'RepeatNode':
        const body = node.body?.map((stmt: any) => {
          if (stmt.type === 'SayNode') return `  say ${stmt.expr}`;
          if (stmt.type === 'LetNode') return `  let ${stmt.name} = ${stmt.expr}`;
          return `  ${stmt.expr}`;
        }).join('\n') || '';
        return `repeat ${node.count} times:\n${body}`;
      case 'FuncDefNode':
        const funcBody = node.body?.map((stmt: any) => {
          if (stmt.type === 'SayNode') return `  say ${stmt.expr}`;
          if (stmt.type === 'LetNode') return `  let ${stmt.name} = ${stmt.expr}`;
          return `  ${stmt.expr}`;
        }).join('\n') || '';
        const params = node.params?.join(', ') || '';
        return `define ${node.name}(${params}):\n${funcBody}`;
      case 'FuncCallNode':
        const args = node.args?.join(', ') || '';
        return `${node.name}(${args})`;
      case 'ImportNode':
        return `import ${node.path}`;
      case 'StringNode':
        return `"${node.value}"`;
      case 'ConstantNode':
        return `${node.value}`;
      default:
        return `# Unknown node type: ${node.type}`;
    }
  }).join('\n');
}

// Generate Origin code from blocks with error handling
export function blocksToCodeWithErrorHandling(blocks: BlockInstance[]): { code: string; error?: string } {
  try {
    const code = blocksToCode(blocks);
    return { code };
  } catch (error) {
    return { 
      code: '', 
      error: error instanceof Error ? error.message : 'Unknown error occurred' 
    };
  }
}

// Parse Origin code to blocks
export function codeToBlocks(code: string): BlockInstance[] {
  // This is a simplified parser - in a real implementation,
  // you'd use the actual Origin parser
  const lines = code.split('\n').filter(line => line.trim());
  const blocks: BlockInstance[] = [];
  
  lines.forEach((line, index) => {
    const trimmed = line.trim();
    
    if (trimmed.startsWith('say ')) {
      const expr = trimmed.substring(4);
      blocks.push({
        id: `say-${index}-${Date.now()}`,
        definitionId: 'say',
        position: { x: index * 200, y: index * 100 },
        inputs: { expr },
        outputs: {},
      });
    } else if (trimmed.startsWith('let ')) {
      const match = trimmed.match(/let (\w+) = (.+)/);
      if (match) {
        const [, name, expr] = match;
        blocks.push({
          id: `let-${index}-${Date.now()}`,
          definitionId: 'let',
          position: { x: index * 200, y: index * 100 },
          inputs: { name, expr },
          outputs: {},
        });
      }
    } else if (trimmed.startsWith('repeat ')) {
      const match = trimmed.match(/repeat (\d+) times:/);
      if (match) {
        const [, count] = match;
        blocks.push({
          id: `repeat-${index}-${Date.now()}`,
          definitionId: 'repeat',
          position: { x: index * 200, y: index * 100 },
          inputs: { count: parseInt(count) },
          outputs: {},
        });
      }
    } else if (trimmed.startsWith('define ')) {
      const match = trimmed.match(/define (\w+)\(([^)]*)\):/);
      if (match) {
        const [, name, params] = match;
        blocks.push({
          id: `define-${index}-${Date.now()}`,
          definitionId: 'define',
          position: { x: index * 200, y: index * 100 },
          inputs: { name, params },
          outputs: {},
        });
      }
    } else if (trimmed.startsWith('import ')) {
      const path = trimmed.substring(7);
      blocks.push({
        id: `import-${index}-${Date.now()}`,
        definitionId: 'import',
        position: { x: index * 200, y: index * 100 },
        inputs: { path },
        outputs: {},
      });
    }
  });
  
  return blocks;
} 