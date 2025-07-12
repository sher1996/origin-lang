import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import type { Block } from '../blocks';

interface CanvasBlock {
  id: string;
  block: Block;
  position: { x: number; y: number };
}

interface CanvasProps {
  blocks: CanvasBlock[];
}

const Canvas: React.FC<CanvasProps> = ({ blocks }) => {
  const { setNodeRef } = useDroppable({
    id: 'canvas',
  });

  return (
    <div
      ref={setNodeRef}
      className="flex-1 bg-white border-2 border-dashed border-gray-300 p-4 relative min-h-screen"
    >
      <div className="text-gray-500 text-center mb-4">
        Drop blocks here to build your program
      </div>
      
      {blocks.map((canvasBlock) => (
        <div
          key={canvasBlock.id}
          className="absolute bg-blue-100 border border-blue-300 rounded-lg p-3 cursor-move"
          style={{
            left: canvasBlock.position.x,
            top: canvasBlock.position.y,
          }}
        >
          {canvasBlock.block.label}
        </div>
      ))}
    </div>
  );
};

export default Canvas; 