import React, { forwardRef, useMemo, useCallback, useRef } from 'react';
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
  isReplayMode?: boolean;
  currentFrameData?: any;
  isStreaming?: boolean;
}

// Virtual rendering configuration
const VISIBLE_AREA_PADDING = 200; // Extra pixels to render outside viewport
const BLOCK_HEIGHT = 120; // Approximate block height for calculations

const Canvas = forwardRef<HTMLDivElement, CanvasProps>(({ 
  blocks, 
  connections = [], 
  draggingConnection = null,
  isReplayMode = false,
  currentFrameData = null,
  isStreaming = false
}, ref) => {
  const { setNodeRef } = useDroppable({
    id: 'canvas',
    disabled: isReplayMode, // Disable drag-and-drop in replay mode
  });

  const canvasRef = useRef<HTMLDivElement>(null);
  const [viewport, setViewport] = React.useState({ top: 0, left: 0, width: 0, height: 0 });

  // Update viewport on scroll/resize
  React.useEffect(() => {
    const updateViewport = () => {
      if (canvasRef.current) {
        const rect = canvasRef.current.getBoundingClientRect();
        setViewport({
          top: rect.top - VISIBLE_AREA_PADDING,
          left: rect.left - VISIBLE_AREA_PADDING,
          width: rect.width + VISIBLE_AREA_PADDING * 2,
          height: rect.height + VISIBLE_AREA_PADDING * 2
        });
      }
    };

    updateViewport();
    window.addEventListener('scroll', updateViewport);
    window.addEventListener('resize', updateViewport);

    return () => {
      window.removeEventListener('scroll', updateViewport);
      window.removeEventListener('resize', updateViewport);
    };
  }, []);

  // Calculate visible blocks for virtual rendering
  const visibleBlocks = useMemo(() => {
    if (!isStreaming) {
      // For small recordings, render all blocks
      return blocks;
    }

    // For large recordings, only render blocks that are visible or near visible area
    return blocks.filter(block => {
      const blockTop = block.position.y;
      const blockBottom = block.position.y + BLOCK_HEIGHT;
      const blockLeft = block.position.x;
      const blockRight = block.position.x + 200; // Approximate block width

      return (
        blockBottom >= viewport.top &&
        blockTop <= viewport.top + viewport.height &&
        blockRight >= viewport.left &&
        blockLeft <= viewport.left + viewport.width
      );
    });
  }, [blocks, isStreaming, viewport]);

  // Memoized block renderer with DOM recycling
  const renderBlock = useCallback((blockInstance: BlockInstance) => {
    const definition = BLOCK_DEFINITIONS[blockInstance.definitionId];
    if (!definition) return null;

    // Check if this block is active in the current frame (for replay mode)
    const isActive = isReplayMode && currentFrameData 
      ? currentFrameData.blockId === blockInstance.id
      : false;

    return (
      <div
        key={blockInstance.id}
        className={`absolute bg-blue-100 border border-blue-300 rounded-lg p-3 transition-all duration-200 ${
          isReplayMode 
            ? 'cursor-default opacity-75' 
            : 'cursor-move hover:shadow-md'
        } ${
          isActive 
            ? 'ring-2 ring-green-500 bg-green-50 border-green-400' 
            : ''
        }`}
        style={{
          left: blockInstance.position.x,
          top: blockInstance.position.y,
          transform: isActive ? 'scale(1.05)' : 'scale(1)',
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
  }, [isReplayMode, currentFrameData]);

  return (
    <div
      ref={(node) => {
        setNodeRef(node);
        if (typeof ref === 'function') ref(node);
        else if (ref) (ref as React.MutableRefObject<HTMLDivElement | null>).current = node;
        canvasRef.current = node;
      }}
      id="blocks-root"
      className={`flex-1 bg-white border-2 border-dashed border-gray-300 p-4 relative min-h-screen overflow-auto ${
        isReplayMode ? 'pointer-events-none' : ''
      }`}
      style={{
        backgroundImage: `
          linear-gradient(to right, #f0f0f0 1px, transparent 1px),
          linear-gradient(to bottom, #f0f0f0 1px, transparent 1px)
        `,
        backgroundSize: '10px 10px'
      }}
    >
      <div className="text-gray-500 text-center mb-4">
        {isReplayMode ? (
          <div className="flex items-center justify-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
            <span>Replay Mode - Canvas is read-only</span>
            {isStreaming && (
              <span className="text-xs text-orange-600 ml-2">
                (Streaming mode - showing {visibleBlocks.length} of {blocks.length} blocks)
              </span>
            )}
          </div>
        ) : (
          "Drop blocks here to build your program"
        )}
      </div>
      
      {/* Connection lines rendered behind blocks */}
      <ConnectionLines 
        connections={connections}
        blocks={blocks}
        draggingConnection={draggingConnection}
      />
      
      {/* Render only visible blocks for performance */}
      {visibleBlocks.map(renderBlock)}
    </div>
  );
});

export default Canvas; 