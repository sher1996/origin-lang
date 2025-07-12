// Auto-layout utility for positioning blocks
import type { BlockInstance } from '../blocks/definitions';

export function autoLayoutBlocks(blocks: BlockInstance[]): BlockInstance[] {
  const BLOCK_WIDTH = 200;
  const BLOCK_HEIGHT = 100;
  const VERTICAL_SPACING = 50;
  const HORIZONTAL_SPACING = 30;
  
  return blocks.map((block, index) => {
    const row = Math.floor(index / 3); // 3 blocks per row
    const col = index % 3;
    
    return {
      ...block,
      position: {
        x: col * (BLOCK_WIDTH + HORIZONTAL_SPACING) + 50,
        y: row * (BLOCK_HEIGHT + VERTICAL_SPACING) + 50,
      },
    };
  });
}

// Alternative layout: simple vertical stack
export function verticalLayoutBlocks(blocks: BlockInstance[]): BlockInstance[] {
  const BLOCK_HEIGHT = 80;
  const VERTICAL_SPACING = 20;
  
  return blocks.map((block, index) => ({
    ...block,
    position: {
      x: 50,
      y: index * (BLOCK_HEIGHT + VERTICAL_SPACING) + 50,
    },
  }));
} 