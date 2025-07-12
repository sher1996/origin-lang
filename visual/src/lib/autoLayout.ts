// Auto-layout utility for positioning blocks
import type { BlockInstance } from '../blocks/definitions';

export interface LayoutOptions {
  startX?: number;
  startY?: number;
  spacingX?: number;
  spacingY?: number;
  maxWidth?: number;
  padding?: number;
}

const DEFAULT_OPTIONS: Required<LayoutOptions> = {
  startX: 50,
  startY: 50,
  spacingX: 200,
  spacingY: 100,
  maxWidth: 800,
  padding: 20,
};

export function autoLayoutBlocks(
  blocks: BlockInstance[],
  options: LayoutOptions = {}
): BlockInstance[] {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  
  return blocks.map((block, index) => {
    const row = Math.floor(index * opts.spacingX / opts.maxWidth);
    const col = index % Math.floor(opts.maxWidth / opts.spacingX);
    
    const x = opts.startX + (col * opts.spacingX);
    const y = opts.startY + (row * opts.spacingY);
    
    return {
      ...block,
      position: { x, y },
    };
  });
}

// Alternative layout: simple vertical stack
export function verticalLayoutBlocks(
  blocks: BlockInstance[],
  options: LayoutOptions = {}
): BlockInstance[] {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  
  return blocks.map((block, index) => ({
    ...block,
    position: {
      x: opts.startX,
      y: opts.startY + (index * opts.spacingY),
    },
  }));
}

// Layout blocks in a grid pattern
export function gridLayoutBlocks(
  blocks: BlockInstance[],
  options: LayoutOptions = {}
): BlockInstance[] {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  const colsPerRow = Math.floor(opts.maxWidth / opts.spacingX);
  
  return blocks.map((block, index) => {
    const row = Math.floor(index / colsPerRow);
    const col = index % colsPerRow;
    
    return {
      ...block,
      position: {
        x: opts.startX + (col * opts.spacingX),
        y: opts.startY + (row * opts.spacingY),
      },
    };
  });
}

// Smart layout that groups related blocks
export function smartLayoutBlocks(
  blocks: BlockInstance[],
  options: LayoutOptions = {}
): BlockInstance[] {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  
  // Group blocks by type for better visual organization
  const groups: { [key: string]: BlockInstance[] } = {};
  
  blocks.forEach(block => {
    const type = block.definition.id;
    if (!groups[type]) {
      groups[type] = [];
    }
    groups[type].push(block);
  });
  
  const result: BlockInstance[] = [];
  let currentY = opts.startY;
  
  Object.entries(groups).forEach(([type, typeBlocks]) => {
    // Position blocks of the same type horizontally
    typeBlocks.forEach((block, index) => {
      result.push({
        ...block,
        position: {
          x: opts.startX + (index * opts.spacingX),
          y: currentY,
        },
      });
    });
    
    // Move to next row for next type
    currentY += opts.spacingY;
  });
  
  return result;
}

// Flow layout that positions blocks based on connections
export function flowLayoutBlocks(
  blocks: BlockInstance[],
  options: LayoutOptions = {}
): BlockInstance[] {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  
  // Simple flow: position blocks in execution order
  return blocks.map((block, index) => ({
    ...block,
    position: {
      x: opts.startX + (index * opts.spacingX),
      y: opts.startY + (Math.floor(index / 3) * opts.spacingY),
    },
  }));
}

// Compact layout for dense arrangements
export function compactLayoutBlocks(
  blocks: BlockInstance[],
  options: LayoutOptions = {}
): BlockInstance[] {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  const compactSpacingX = opts.spacingX * 0.7;
  const compactSpacingY = opts.spacingY * 0.7;
  
  return blocks.map((block, index) => {
    const row = Math.floor(index / 4); // 4 blocks per row
    const col = index % 4;
    
    return {
      ...block,
      position: {
        x: opts.startX + (col * compactSpacingX),
        y: opts.startY + (row * compactSpacingY),
      },
    };
  });
}

// Layout function that automatically chooses the best layout based on block count
export function autoChooseLayout(
  blocks: BlockInstance[],
  options: LayoutOptions = {}
): BlockInstance[] {
  if (blocks.length === 0) return blocks;
  
  if (blocks.length <= 3) {
    return verticalLayoutBlocks(blocks, options);
  } else if (blocks.length <= 8) {
    return gridLayoutBlocks(blocks, options);
  } else {
    return smartLayoutBlocks(blocks, options);
  }
}

// Utility to get layout bounds
export function getLayoutBounds(blocks: BlockInstance[]): {
  minX: number;
  minY: number;
  maxX: number;
  maxY: number;
  width: number;
  height: number;
} {
  if (blocks.length === 0) {
    return { minX: 0, minY: 0, maxX: 0, maxY: 0, width: 0, height: 0 };
  }
  
  const xs = blocks.map(b => b.position.x);
  const ys = blocks.map(b => b.position.y);
  
  const minX = Math.min(...xs);
  const minY = Math.min(...ys);
  const maxX = Math.max(...xs);
  const maxY = Math.max(...ys);
  
  return {
    minX,
    minY,
    maxX,
    maxY,
    width: maxX - minX,
    height: maxY - minY,
  };
} 