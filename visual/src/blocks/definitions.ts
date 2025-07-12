// Block definitions for AST ↔ blocks mapping
export interface BlockInput {
  id: string;
  label: string;
  type: 'string' | 'number' | 'expression' | 'identifier';
  required: boolean;
  defaultValue?: any;
}

export interface BlockOutput {
  id: string;
  label: string;
  type: 'string' | 'number' | 'expression' | 'identifier';
}

export interface BlockDefinition {
  id: string;
  label: string;
  astType: string; // Maps to AST node type (e.g., 'SayNode', 'LetNode')
  inputs: BlockInput[];
  outputs: BlockOutput[];
  serialize: (inputs: Record<string, any>) => any; // AST node
  deserialize: (astNode: any) => Record<string, any>; // Block inputs
  color?: string;
  icon?: string;
}

// Enhanced block registry with all block types
export class BlockRegistry {
  private static instance: BlockRegistry;
  private definitions: Map<string, BlockDefinition> = new Map();
  private astTypeMap: Map<string, BlockDefinition> = new Map();

  private constructor() {
    this.registerDefaultBlocks();
  }

  static getInstance(): BlockRegistry {
    if (!BlockRegistry.instance) {
      BlockRegistry.instance = new BlockRegistry();
    }
    return BlockRegistry.instance;
  }

  private registerDefaultBlocks() {
    const blocks: BlockDefinition[] = [
      {
        id: 'say',
        label: 'Say',
        astType: 'SayNode',
        inputs: [
          { id: 'expr', label: 'Expression', type: 'expression', required: true }
        ],
        outputs: [],
        serialize: (inputs) => ({ type: 'SayNode', expr: inputs.expr }),
        deserialize: (astNode) => ({ expr: astNode.expr }),
        color: 'blue',
      },
      {
        id: 'let',
        label: 'Let',
        astType: 'LetNode',
        inputs: [
          { id: 'name', label: 'Variable Name', type: 'identifier', required: true },
          { id: 'expr', label: 'Expression', type: 'expression', required: true }
        ],
        outputs: [
          { id: 'name', label: 'Variable', type: 'identifier' }
        ],
        serialize: (inputs) => ({ type: 'LetNode', name: inputs.name, expr: inputs.expr }),
        deserialize: (astNode) => ({ name: astNode.name, expr: astNode.expr }),
        color: 'green',
      },
      {
        id: 'string',
        label: 'String',
        astType: 'StringNode',
        inputs: [
          { id: 'value', label: 'Value', type: 'string', required: true, defaultValue: '' }
        ],
        outputs: [
          { id: 'value', label: 'String', type: 'string' }
        ],
        serialize: (inputs) => ({ type: 'StringNode', value: inputs.value }),
        deserialize: (astNode) => ({ value: astNode.value }),
        color: 'orange',
      },
      {
        id: 'number',
        label: 'Number',
        astType: 'NumberNode',
        inputs: [
          { id: 'value', label: 'Value', type: 'number', required: true, defaultValue: 0 }
        ],
        outputs: [
          { id: 'value', label: 'Number', type: 'number' }
        ],
        serialize: (inputs) => ({ type: 'NumberNode', value: inputs.value }),
        deserialize: (astNode) => ({ value: astNode.value }),
        color: 'purple',
      },
      {
        id: 'import',
        label: 'Import',
        astType: 'ImportNode',
        inputs: [
          { id: 'path', label: 'Path', type: 'string', required: true, defaultValue: '' }
        ],
        outputs: [],
        serialize: (inputs) => ({ type: 'ImportNode', path: inputs.path }),
        deserialize: (astNode) => ({ path: astNode.path }),
        color: 'gray',
      },
      {
        id: 'repeat',
        label: 'Repeat',
        astType: 'RepeatNode',
        inputs: [
          { id: 'count', label: 'Count', type: 'number', required: true, defaultValue: 1 },
          { id: 'body', label: 'Body', type: 'expression', required: true }
        ],
        outputs: [],
        serialize: (inputs) => ({ type: 'RepeatNode', count: inputs.count, body: inputs.body }),
        deserialize: (astNode) => ({ count: astNode.count, body: astNode.body }),
        color: 'indigo',
      },
      {
        id: 'if',
        label: 'If',
        astType: 'IfNode',
        inputs: [
          { id: 'condition', label: 'Condition', type: 'expression', required: true },
          { id: 'thenBody', label: 'Then', type: 'expression', required: true },
          { id: 'elseBody', label: 'Else', type: 'expression', required: false }
        ],
        outputs: [],
        serialize: (inputs) => ({ 
          type: 'IfNode', 
          condition: inputs.condition, 
          thenBody: inputs.thenBody,
          elseBody: inputs.elseBody 
        }),
        deserialize: (astNode) => ({ 
          condition: astNode.condition, 
          thenBody: astNode.thenBody,
          elseBody: astNode.elseBody 
        }),
        color: 'yellow',
      },
      {
        id: 'function',
        label: 'Function',
        astType: 'FunctionNode',
        inputs: [
          { id: 'name', label: 'Name', type: 'identifier', required: true },
          { id: 'params', label: 'Parameters', type: 'string', required: false, defaultValue: '' },
          { id: 'body', label: 'Body', type: 'expression', required: true }
        ],
        outputs: [
          { id: 'name', label: 'Function', type: 'identifier' }
        ],
        serialize: (inputs) => ({ 
          type: 'FunctionNode', 
          name: inputs.name, 
          params: inputs.params ? inputs.params.split(',').map((p: string) => p.trim()) : [],
          body: inputs.body 
        }),
        deserialize: (astNode) => ({ 
          name: astNode.name, 
          params: astNode.params ? astNode.params.join(', ') : '',
          body: astNode.body 
        }),
        color: 'teal',
      },
    ];

    blocks.forEach(block => this.register(block));
  }

  register(definition: BlockDefinition) {
    this.definitions.set(definition.id, definition);
    this.astTypeMap.set(definition.astType, definition);
  }

  get(id: string): BlockDefinition | undefined {
    return this.definitions.get(id);
  }

  getByAstType(astType: string): BlockDefinition | undefined {
    return this.astTypeMap.get(astType);
  }

  getAll(): BlockDefinition[] {
    return Array.from(this.definitions.values());
  }

  serialize(blockId: string, inputs: Record<string, any>): any {
    const definition = this.get(blockId);
    if (!definition) {
      throw new Error(`Unknown block type: ${blockId}`);
    }
    return definition.serialize(inputs);
  }

  deserialize(astType: string, astNode: any): Record<string, any> {
    const definition = this.getByAstType(astType);
    if (!definition) {
      throw new Error(`Unknown AST type: ${astType}`);
    }
    return definition.deserialize(astNode);
  }
}

// Export singleton instance
export const blockRegistry = BlockRegistry.getInstance();

// Legacy exports for backward compatibility
export const BLOCK_DEFINITIONS = blockRegistry.getAll();

export const getBlockDefinition = (id: string): BlockDefinition | undefined => {
  return blockRegistry.get(id);
};

export const getBlockDefinitionByAstType = (astType: string): BlockDefinition | undefined => {
  return blockRegistry.getByAstType(astType);
};

export interface BlockInstance {
  id: string;
  definition: BlockDefinition;
  inputs: Record<string, any>;
  position: { x: number; y: number };
} 