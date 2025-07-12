import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import type { BlockInstance } from '../blocks/definitions';

interface CanvasProps {
  blocks: BlockInstance[];
  onInputChange?: (blockId: string, inputId: string, value: any) => void;
  onBlockRemove?: (blockId: string) => void;
}

const Canvas: React.FC<CanvasProps> = ({ blocks, onInputChange, onBlockRemove }) => {
  const { setNodeRef } = useDroppable({
    id: 'canvas',
  });

  const getColorClass = (color?: string) => {
    switch (color) {
      case 'blue': return 'bg-blue-100 border-blue-300 hover:bg-blue-200';
      case 'green': return 'bg-green-100 border-green-300 hover:bg-green-200';
      case 'purple': return 'bg-purple-100 border-purple-300 hover:bg-purple-200';
      case 'orange': return 'bg-orange-100 border-orange-300 hover:bg-orange-200';
      case 'gray': return 'bg-gray-100 border-gray-300 hover:bg-gray-200';
      case 'indigo': return 'bg-indigo-100 border-indigo-300 hover:bg-indigo-200';
      case 'yellow': return 'bg-yellow-100 border-yellow-300 hover:bg-yellow-200';
      case 'teal': return 'bg-teal-100 border-teal-300 hover:bg-teal-200';
      default: return 'bg-white border-gray-300 hover:bg-gray-50';
    }
  };

  const getInputType = (type: string) => {
    switch (type) {
      case 'number':
        return 'number';
      case 'string':
        return 'text';
      default:
        return 'text';
    }
  };

  return (
    <div
      ref={setNodeRef}
      className="flex-1 bg-white border-2 border-dashed border-gray-300 p-4 relative min-h-screen overflow-auto"
    >
      <div className="text-gray-500 text-center mb-4">
        Drop blocks here to build your program
      </div>
      {blocks.map((blockInstance) => (
        <div
          key={blockInstance.id}
          className={`absolute border rounded-lg p-3 cursor-move shadow-sm transition-all duration-200 ${getColorClass(blockInstance.definition.color)}`}
          style={{
            left: blockInstance.position.x,
            top: blockInstance.position.y,
            minWidth: '150px',
            maxWidth: '300px',
          }}
        >
          <div className="flex items-center justify-between mb-2">
            <div className="font-medium text-sm">{blockInstance.definition.label}</div>
            {onBlockRemove && (
              <button
                onClick={() => onBlockRemove(blockInstance.id)}
                className="text-red-500 hover:text-red-700 text-xs px-1 py-0.5 rounded"
                title="Remove block"
              >
                ×
              </button>
            )}
          </div>
          {blockInstance.definition.inputs.map((input) => (
            <div key={input.id} className="mb-2">
              <label className="text-xs text-gray-600 block mb-1">
                {input.label}:
              </label>
              <input
                type={getInputType(input.type)}
                className="w-full text-xs px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder={input.defaultValue?.toString() || ''}
                value={blockInstance.inputs[input.id] || ''}
                onChange={(e) => {
                  const value = input.type === 'number' ? parseFloat(e.target.value) || 0 : e.target.value;
                  onInputChange?.(blockInstance.id, input.id, value);
                }}
              />
            </div>
          ))}
          {blockInstance.definition.outputs.length > 0 && (
            <div className="mt-2 pt-2 border-t border-gray-200">
              <div className="text-xs text-gray-500">
                Outputs: {blockInstance.definition.outputs.map(o => o.label).join(', ')}
              </div>
            </div>
          )}
        </div>
      ))}
      {blocks.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center text-gray-400">
          <div className="text-center">
            <div className="text-4xl mb-2">📦</div>
            <div className="text-lg font-medium">No blocks yet</div>
            <div className="text-sm">Drag blocks from the palette to get started</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Canvas; 