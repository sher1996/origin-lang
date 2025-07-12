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