import { useState } from 'react';
import type { Block } from '../blocks';

interface CanvasBlock {
  id: string;
  block: Block;
  position: { x: number; y: number };
}

export const useDrag = () => {
  const [blocks, setBlocks] = useState<CanvasBlock[]>([]);

  const handleDragEnd = (event: any) => {
    const { active, over } = event;
    
    if (over && over.id === 'canvas' && active.data.current) {
      const droppedBlock = active.data.current as Block;
      const newBlock: CanvasBlock = {
        id: `${droppedBlock.id}-${Date.now()}`,
        block: droppedBlock,
        position: { x: 0, y: 0 }, // Simple positioning for now
      };
      
      setBlocks(prev => [...prev, newBlock]);
    }
  };

  return {
    blocks,
    setBlocks,
    handleDragEnd,
  };
}; 