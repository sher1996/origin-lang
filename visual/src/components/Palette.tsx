import React from 'react';
import { useDraggable } from '@dnd-kit/core';
import { BLOCKS, type Block } from '../blocks';

interface DraggableBlockProps {
  block: Block;
}

const DraggableBlock: React.FC<DraggableBlockProps> = ({ block }) => {
  const { attributes, listeners, setNodeRef, transform } = useDraggable({
    id: block.id,
    data: block,
  });

  const style = transform ? {
    transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
  } : undefined;

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      className="bg-white border border-gray-300 rounded-lg p-3 mb-2 cursor-move hover:bg-gray-50 transition-colors"
    >
      {block.label}
    </div>
  );
};

const Palette: React.FC = () => {
  return (
    <div className="w-60 bg-gray-100 p-4 border-r border-gray-300">
      <h2 className="text-lg font-semibold mb-4 text-gray-800">Blocks</h2>
      <div className="space-y-2">
        {BLOCKS.map((block) => (
          <DraggableBlock key={block.id} block={block} />
        ))}
      </div>
    </div>
  );
};

export default Palette; 