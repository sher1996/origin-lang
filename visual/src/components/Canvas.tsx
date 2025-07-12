import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import type { BlockInstance } from '../blocks/definitions';
import { BLOCK_DEFINITIONS } from '../blocks/definitions';
import ConnectionLines from './ConnectionLines';
import type { Connection } from '../hooks/useConnections';

interface CanvasProps {
  blocks: BlockInstance[];
  connections?: Connection[];
  draggingConnection?: {
    fromBlockId: string;
    fromOutputId: string;
    position: { x: number; y: number };
  } | null;
}

const Canvas: React.FC<CanvasProps> = ({ 
  blocks, 
  connections = [], 
  draggingConnection = null 
}) => {
  const { setNodeRef } = useDroppable({
    id: 'canvas',
  });

  return (
    <div
      ref={setNodeRef}
      className="flex-1 bg-white border-2 border-dashed border-gray-300 p-4 relative min-h-screen"
      style={{
        backgroundImage: `
          linear-gradient(to right, #f0f0f0 1px, transparent 1px),
          linear-gradient(to bottom, #f0f0f0 1px, transparent 1px)
        `,
        backgroundSize: '10px 10px'
      }}
    >
      <div className="text-gray-500 text-center mb-4">
        Drop blocks here to build your program
      </div>
      
      {/* Connection lines rendered behind blocks */}
      <ConnectionLines 
        connections={connections}
        blocks={blocks}
        draggingConnection={draggingConnection}
      />
      
      {blocks.map((blockInstance) => {
        const definition = BLOCK_DEFINITIONS[blockInstance.definitionId];
        if (!definition) return null;
        
        return (
          <div
            key={blockInstance.id}
            className="absolute bg-blue-100 border border-blue-300 rounded-lg p-3 cursor-move hover:shadow-md transition-shadow"
            style={{
              left: blockInstance.position.x,
              top: blockInstance.position.y,
            }}
          >
            <div className="font-medium text-blue-800">{definition.label}</div>
            {definition.inputs.length > 0 && (
              <div className="text-xs text-blue-600 mt-1">
                {definition.inputs.map(input => (
                  <div key={input.id} className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span>{input.label}: {blockInstance.inputs[input.id] || '...'}</span>
                  </div>
                ))}
              </div>
            )}
            {definition.outputs.length > 0 && (
              <div className="text-xs text-blue-600 mt-1">
                {definition.outputs.map(output => (
                  <div key={output.id} className="flex items-center gap-2">
                    <span>{output.label}</span>
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
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