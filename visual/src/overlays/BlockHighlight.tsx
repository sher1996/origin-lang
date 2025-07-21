import React from 'react';
import type { BlockInstance } from '../blocks/definitions';
import type { RecordingFrame } from '../hooks/usePlayer';

interface BlockHighlightProps {
  blocks: BlockInstance[];
  currentFrame: RecordingFrame | null;
  isVisible: boolean;
}

const BlockHighlight: React.FC<BlockHighlightProps> = ({ blocks, currentFrame, isVisible }) => {
  if (!isVisible || !currentFrame) return null;

  // Find the block that matches the current frame's blockId
  const activeBlock = blocks.find(block => {
    // Extract the block type from the blockId (e.g., "LetNode:i" -> "LetNode")
    const blockType = currentFrame.blockId.split(':')[0];
    return block.definitionId === blockType.toLowerCase();
  });

  if (!activeBlock) return null;

  const { position, inputs: _inputs } = activeBlock;
  
  // Format local variables for display
  const formatVariables = (locals: Record<string, any>) => {
    return Object.entries(locals)
      .map(([name, value]) => `${name} = ${JSON.stringify(value)}`)
      .join(', ');
  };

  return (
    <>
      {/* Highlight Ring */}
      <div
        className="absolute pointer-events-none z-10"
        style={{
          left: position.x - 8,
          top: position.y - 8,
          width: 200, // Approximate block width
          height: 80,  // Approximate block height
        }}
        data-testid="block-highlight"
      >
        <div className="w-full h-full border-2 border-blue-500 rounded-lg bg-blue-500 bg-opacity-10 animate-pulse" />
      </div>

      {/* Tooltip */}
      <div
        className="absolute z-20 bg-gray-900 text-white px-3 py-2 rounded shadow-lg text-sm max-w-xs"
        style={{
          left: position.x + 220,
          top: position.y,
        }}
      >
        <div className="font-semibold mb-1">Active Block</div>
        <div className="text-gray-300 mb-2">{currentFrame.blockId}</div>
        {Object.keys(currentFrame.locals).length > 0 && (
          <>
            <div className="font-semibold text-xs text-gray-400 mb-1">Local Variables:</div>
            <div className="text-xs text-gray-300">
              {formatVariables(currentFrame.locals)}
            </div>
          </>
        )}
        {Object.keys(currentFrame.globals).length > 0 && (
          <>
            <div className="font-semibold text-xs text-gray-400 mb-1 mt-2">Global Variables:</div>
            <div className="text-xs text-gray-300">
              {formatVariables(currentFrame.globals)}
            </div>
          </>
        )}
      </div>
    </>
  );
};

export default BlockHighlight; 