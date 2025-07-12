import React from 'react';
import { useDraggable } from '@dnd-kit/core';
import { blockRegistry, type BlockDefinition } from '../blocks/definitions';

interface DraggableBlockProps {
  block: BlockDefinition;
}

const DraggableBlock: React.FC<DraggableBlockProps> = ({ block }) => {
  const { attributes, listeners, setNodeRef, transform } = useDraggable({
    id: block.id,
    data: block,
  });

  const style = transform ? {
    transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
  } : undefined;

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

  const getCategory = (blockId: string): string => {
    const categories: { [key: string]: string } = {
      'say': 'Output',
      'let': 'Variables',
      'string': 'Data',
      'number': 'Data',
      'import': 'System',
      'repeat': 'Control',
      'if': 'Control',
      'function': 'Functions',
    };
    return categories[blockId] || 'Other';
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      className={`border rounded-lg p-3 mb-2 cursor-move hover:opacity-80 transition-all ${getColorClass(block.color)}`}
    >
      <div className="font-medium text-sm">{block.label}</div>
      {block.inputs.length > 0 && (
        <div className="text-xs text-gray-600 mt-1">
          {block.inputs.length} input{block.inputs.length !== 1 ? 's' : ''}
        </div>
      )}
      {block.outputs.length > 0 && (
        <div className="text-xs text-gray-500 mt-1">
          {block.outputs.length} output{block.outputs.length !== 1 ? 's' : ''}
        </div>
      )}
    </div>
  );
};

const Palette: React.FC = () => {
  const blocks = blockRegistry.getAll();
  
  // Group blocks by category
  const categories: { [key: string]: BlockDefinition[] } = {};
  blocks.forEach(block => {
    const category = getCategory(block.id);
    if (!categories[category]) {
      categories[category] = [];
    }
    categories[category].push(block);
  });

  const getCategory = (blockId: string): string => {
    const categories: { [key: string]: string } = {
      'say': 'Output',
      'let': 'Variables',
      'string': 'Data',
      'number': 'Data',
      'import': 'System',
      'repeat': 'Control',
      'if': 'Control',
      'function': 'Functions',
    };
    return categories[blockId] || 'Other';
  };

  return (
    <div className="w-64 bg-gray-100 p-4 border-r border-gray-300 overflow-y-auto">
      <h2 className="text-lg font-semibold mb-4 text-gray-800">Blocks</h2>
      <div className="space-y-4">
        {Object.entries(categories).map(([category, categoryBlocks]) => (
          <div key={category}>
            <h3 className="text-sm font-medium text-gray-700 mb-2 uppercase tracking-wide">
              {category}
            </h3>
            <div className="space-y-2">
              {categoryBlocks.map((block) => (
                <DraggableBlock key={block.id} block={block} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Palette; 