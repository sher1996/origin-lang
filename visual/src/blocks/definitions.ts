// Block definitions for AST ↔ blocks mapping
export interface BlockDefinition {
  id: string;
  label: string;
  astType: string;
  inputs: BlockInput[];
  outputs: BlockOutput[];
  serialize: (data: any) => any;
  deserialize: (data: any) => any;
}

export interface BlockInput {
  id: string;
  label: string;
  type: 'string' | 'number' | 'expression';
  required: boolean;
}

export interface BlockOutput {
  id: string;
  label: string;
  type: 'value' | 'statement';
}

export interface BlockInstance {
  id: string;
  definitionId: string;
  position: { x: number; y: number };
  inputs: Record<string, any>;
  outputs: Record<string, any>;
}

// AST node types
export interface ASTNode {
  type: string;
  [key: string]: any;
}

// Block registry
export const BLOCK_DEFINITIONS: Record<string, BlockDefinition> = {
  say: {
    id: 'say',
    label: 'Say',
    astType: 'SayNode',
    inputs: [
      { id: 'expr', label: 'Expression', type: 'expression', required: true }
    ],
    outputs: [
      { id: 'statement', label: 'Statement', type: 'statement' }
    ],
    serialize: (data) => ({ type: 'SayNode', expr: data.expr }),
    deserialize: (data) => ({ expr: data.expr })
  },
  
  let: {
    id: 'let',
    label: 'Let',
    astType: 'LetNode',
    inputs: [
      { id: 'name', label: 'Variable Name', type: 'string', required: true },
      { id: 'expr', label: 'Expression', type: 'expression', required: true }
    ],
    outputs: [
      { id: 'statement', label: 'Statement', type: 'statement' }
    ],
    serialize: (data) => ({ type: 'LetNode', name: data.name, expr: data.expr }),
    deserialize: (data) => ({ name: data.name, expr: data.expr })
  },
  
  repeat: {
    id: 'repeat',
    label: 'Repeat',
    astType: 'RepeatNode',
    inputs: [
      { id: 'count', label: 'Count', type: 'number', required: true }
    ],
    outputs: [
      { id: 'statement', label: 'Statement', type: 'statement' }
    ],
    serialize: (data) => ({ type: 'RepeatNode', count: data.count, body: data.body }),
    deserialize: (data) => ({ count: data.count, body: data.body })
  },
  
  define: {
    id: 'define',
    label: 'Define Function',
    astType: 'FuncDefNode',
    inputs: [
      { id: 'name', label: 'Function Name', type: 'string', required: true },
      { id: 'params', label: 'Parameters', type: 'string', required: false }
    ],
    outputs: [
      { id: 'statement', label: 'Statement', type: 'statement' }
    ],
    serialize: (data) => ({ type: 'FuncDefNode', name: data.name, params: data.params, body: data.body }),
    deserialize: (data) => ({ name: data.name, params: data.params, body: data.body })
  },
  
  call: {
    id: 'call',
    label: 'Call Function',
    astType: 'FuncCallNode',
    inputs: [
      { id: 'name', label: 'Function Name', type: 'string', required: true },
      { id: 'args', label: 'Arguments', type: 'string', required: false }
    ],
    outputs: [
      { id: 'expression', label: 'Expression', type: 'value' }
    ],
    serialize: (data) => ({ type: 'FuncCallNode', name: data.name, args: data.args }),
    deserialize: (data) => ({ name: data.name, args: data.args })
  },
  
  import: {
    id: 'import',
    label: 'Import',
    astType: 'ImportNode',
    inputs: [
      { id: 'path', label: 'Path', type: 'string', required: true }
    ],
    outputs: [
      { id: 'statement', label: 'Statement', type: 'statement' }
    ],
    serialize: (data) => ({ type: 'ImportNode', path: data.path }),
    deserialize: (data) => ({ path: data.path })
  },
  
  string: {
    id: 'string',
    label: 'String',
    astType: 'StringNode',
    inputs: [
      { id: 'value', label: 'Value', type: 'string', required: true }
    ],
    outputs: [
      { id: 'value', label: 'Value', type: 'value' }
    ],
    serialize: (data) => ({ type: 'StringNode', value: data.value }),
    deserialize: (data) => ({ value: data.value })
  },
  
  constant: {
    id: 'constant',
    label: 'Constant',
    astType: 'ConstantNode',
    inputs: [
      { id: 'value', label: 'Value', type: 'number', required: true }
    ],
    outputs: [
      { id: 'value', label: 'Value', type: 'value' }
    ],
    serialize: (data) => ({ type: 'ConstantNode', value: data.value }),
    deserialize: (data) => ({ value: data.value })
  }
};

export const BLOCKS = Object.values(BLOCK_DEFINITIONS); 