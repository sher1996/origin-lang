export interface Block {
  id: string;
  label: string;
}

export const BLOCKS: Block[] = [
  { id: "var", label: "Variable" },
  { id: "add", label: "Add" },
  { id: "print", label: "Print" }
]; 