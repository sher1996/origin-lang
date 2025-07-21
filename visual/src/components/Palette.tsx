import React from 'react';
import { useDraggable } from '@dnd-kit/core';
import { BLOCKS, type BlockDefinition } from '../blocks/definitions';

interface DraggableBlockProps {
  block: BlockDefinition;
  isReplayMode?: boolean;
}

const DraggableBlock: React.FC<DraggableBlockProps> = ({ block, isReplayMode = false }) => {
  const { attributes, listeners, setNodeRef, transform } = useDraggable({
    id: block.id,
    data: block,
    disabled: isReplayMode, // Disable dragging in replay mode
  });

  const style = transform ? {
    transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
  } : undefined;

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...(isReplayMode ? {} : listeners)}
      {...(isReplayMode ? {} : attributes)}
      className={`bg-white border border-gray-300 rounded-lg p-3 mb-2 transition-colors ${
        isReplayMode 
          ? 'cursor-not-allowed opacity-50' 
          : 'cursor-move hover:bg-gray-50'
      }`}
    >
      <div className="font-medium text-gray-800">{block.label}</div>
      <div className="text-xs text-gray-500 mt-1">
        {block.inputs.length} input{block.inputs.length !== 1 ? 's' : ''}, {block.outputs.length} output{block.outputs.length !== 1 ? 's' : ''}
      </div>
    </div>
  );
};

interface PaletteProps {
  isReplayMode?: boolean;
}

const Palette: React.FC<PaletteProps> = ({ isReplayMode = false }) => {
  return (
    <div className="w-60 bg-gray-100 p-4 border-r border-gray-300">
      <h2 className="text-lg font-semibold mb-4 text-gray-800">
        {isReplayMode ? 'Blocks (Read-only)' : 'Blocks'}
      </h2>
      <div className="space-y-2">
        {BLOCKS.map((block) => (
          <DraggableBlock key={block.id} block={block} isReplayMode={isReplayMode} />
        ))}
      </div>
    </div>
  );
};

export default Palette; 