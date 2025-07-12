import { useState } from 'react';
import type { BlockDefinition, BlockInstance } from '../blocks/definitions';

export const useDrag = () => {
  const [blocks, setBlocks] = useState<BlockInstance[]>([]);

  const handleDragEnd = (event: any) => {
    const { active, over } = event;
    
    if (over && over.id === 'canvas' && active.data.current) {
      const droppedBlock = active.data.current as BlockDefinition;
      const newBlock: BlockInstance = {
        id: `${droppedBlock.id}-${Date.now()}`,
        definitionId: droppedBlock.id,
        position: { x: 0, y: 0 }, // Simple positioning for now
        inputs: {},
        outputs: {},
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