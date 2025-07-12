import { DndContext, type DragEndEvent } from '@dnd-kit/core';
import Palette from './components/Palette';
import Canvas from './components/Canvas';
import Toolbar from './components/Toolbar';
import PreviewPane from './components/PreviewPane';
import ErrorOverlay from './components/ErrorOverlay';
import { useDrag } from './hooks/useDrag';
import { useConnections } from './hooks/useConnections';
import { useDebounce } from './hooks/useDebounce';
import { useAutosave } from './hooks/useAutosave';
import { blocksToCodeWithErrorHandling } from './lib/transform';
import { useState, useEffect } from 'react';
import type { BlockInstance } from './blocks/definitions';
import type { Connection } from './hooks/useConnections';

function App() {
  const { blocks, setBlocks, handleDragEnd } = useDrag();
  const { 
    connections, 
    setConnections,
    draggingConnection, 
    addConnection, 
    removeConnection, 
    startDraggingConnection, 
    stopDraggingConnection, 
    updateDraggingPosition, 
    canConnect 
  } = useConnections();
  const [code, setCode] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [isError, setIsError] = useState(false);
  const [showErrorOverlay, setShowErrorOverlay] = useState(false);

  // Auto-save functionality
  const handleRestoreSession = (data: { blocks: BlockInstance[]; connections: Connection[] }) => {
    setBlocks(data.blocks);
    setConnections(data.connections);
  };

  useAutosave(blocks, connections, handleRestoreSession);

  // Debounce code generation
  const debouncedBlocks = useDebounce(blocks, 300);

  useEffect(() => {
    const { code: generatedCode, error: generationError } = blocksToCodeWithErrorHandling(debouncedBlocks);
    setCode(generatedCode);
    
    if (generationError) {
      setError(generationError);
      setIsError(true);
      setShowErrorOverlay(true);
    } else {
      setError('');
      setIsError(false);
      setShowErrorOverlay(false);
    }
  }, [debouncedBlocks]);

  const onDragEnd = (event: DragEndEvent) => {
    handleDragEnd(event);
  };

  return (
    <DndContext onDragEnd={onDragEnd}>
      <div className="flex flex-col h-screen bg-gray-50">
        <Toolbar 
          blocks={blocks} 
          setBlocks={setBlocks} 
          connections={connections}
          setConnections={setConnections}
        />
        <div className="flex flex-1">
          <Palette />
          <Canvas 
            blocks={blocks} 
            connections={connections}
            draggingConnection={draggingConnection}
          />
          <div className="w-1/3 border-l border-gray-300">
            <PreviewPane 
              code={code} 
              isError={isError} 
              errorMessage={error} 
            />
          </div>
        </div>
        {showErrorOverlay && (
          <ErrorOverlay 
            error={error} 
            onClose={() => setShowErrorOverlay(false)} 
          />
        )}
      </div>
    </DndContext>
  );
}

export default App;
