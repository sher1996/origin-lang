import { useState } from 'react';
import type { BlockDefinition, BlockInstance } from '../blocks/definitions';
import { blockRegistry } from '../blocks/definitions';
import { autoChooseLayout } from '../lib/autoLayout';

export const useDrag = () => {
  const [blocks, setBlocks] = useState<BlockInstance[]>([]);

  const handleDragEnd = (event: any) => {
    const { active, over } = event;
    
    if (over && over.id === 'canvas' && active.data.current) {
      const droppedBlock = active.data.current as BlockDefinition;
      
      // Initialize inputs with default values
      const inputs: Record<string, any> = {};
      droppedBlock.inputs.forEach(input => {
        inputs[input.id] = input.defaultValue || '';
      });
      
      const newBlock: BlockInstance = {
        id: `${droppedBlock.id}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        definition: droppedBlock,
        inputs,
        position: { x: 0, y: 0 }, // Will be positioned by auto-layout
      };
      
      // Add the new block and apply auto-layout
      const updatedBlocks = [...blocks, newBlock];
      const laidOutBlocks = autoChooseLayout(updatedBlocks);
      setBlocks(laidOutBlocks);
    }
  };

  const updateBlockInput = (blockId: string, inputId: string, value: any) => {
    setBlocks(prev => prev.map(block => 
      block.id === blockId 
        ? { ...block, inputs: { ...block.inputs, [inputId]: value } }
        : block
    ));
  };

  const removeBlock = (blockId: string) => {
    setBlocks(prev => {
      const filtered = prev.filter(block => block.id !== blockId);
      // Re-apply auto-layout after removal
      return autoChooseLayout(filtered);
    });
  };

  const updateBlockPosition = (blockId: string, position: { x: number; y: number }) => {
    setBlocks(prev => prev.map(block => 
      block.id === blockId 
        ? { ...block, position }
        : block
    ));
  };

  const duplicateBlock = (blockId: string) => {
    const blockToDuplicate = blocks.find(block => block.id === blockId);
    if (!blockToDuplicate) return;

    const newBlock: BlockInstance = {
      ...blockToDuplicate,
      id: `${blockToDuplicate.definition.id}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      position: { 
        x: blockToDuplicate.position.x + 20, 
        y: blockToDuplicate.position.y + 20 
      }
    };

    const updatedBlocks = [...blocks, newBlock];
    const laidOutBlocks = autoChooseLayout(updatedBlocks);
    setBlocks(laidOutBlocks);
  };

  const clearBlocks = () => {
    setBlocks([]);
  };

  const importBlocks = (newBlocks: BlockInstance[]) => {
    const laidOutBlocks = autoChooseLayout(newBlocks);
    setBlocks(laidOutBlocks);
  };

  return {
    blocks,
    setBlocks,
    handleDragEnd,
    updateBlockInput,
    removeBlock,
    updateBlockPosition,
    duplicateBlock,
    clearBlocks,
    importBlocks,
  };
}; 