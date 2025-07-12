import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import type { BlockInstance } from '../blocks/definitions';
import { BLOCK_DEFINITIONS } from '../blocks/definitions';

interface CanvasProps {
  blocks: BlockInstance[];
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
      
      {blocks.map((blockInstance) => {
        const definition = BLOCK_DEFINITIONS[blockInstance.definitionId];
        if (!definition) return null;
        
        return (
          <div
            key={blockInstance.id}
            className="absolute bg-blue-100 border border-blue-300 rounded-lg p-3 cursor-move"
            style={{
              left: blockInstance.position.x,
              top: blockInstance.position.y,
            }}
          >
            <div className="font-medium text-blue-800">{definition.label}</div>
            {definition.inputs.length > 0 && (
              <div className="text-xs text-blue-600 mt-1">
                {definition.inputs.map(input => (
                  <div key={input.id}>
                    {input.label}: {blockInstance.inputs[input.id] || '...'}
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default Canvas; 