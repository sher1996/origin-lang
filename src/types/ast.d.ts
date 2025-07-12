// Shared AST types for Origin language
export interface ASTNode {
  id: string;
  type: string;
  label: string;
  position?: { x: number; y: number };
}

export interface Block {
  id: string;
  label: string;
  type: 'variable' | 'add' | 'print';
}

export interface CanvasBlock {
  id: string;
  block: Block;
  position: { x: number; y: number };
}

// AST node types from parser.py
export type ASTType = 
  | 'SayNode'
  | 'LetNode'
  | 'RepeatNode'
  | 'FuncDefNode'
  | 'FuncCallNode'
  | 'ExprStmtNode'
  | 'ExprNode'
  | 'ImportNode'
  | 'StringNode';

// Block definition interfaces
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
  astType: string;
  inputs: BlockInput[];
  outputs: BlockOutput[];
  serialize: (inputs: Record<string, any>) => any;
  deserialize: (astNode: any) => Record<string, any>;
  color?: string;
  icon?: string;
}

// Visual block instance with data
export interface BlockInstance {
  id: string;
  definition: BlockDefinition;
  inputs: Record<string, any>;
  position: { x: number; y: number };
} 