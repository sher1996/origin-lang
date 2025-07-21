import { DndContext, type DragEndEvent } from '@dnd-kit/core';
import Palette from './components/Palette';
import Canvas from './components/Canvas';
import Toolbar from './components/Toolbar';
import PreviewPane from './components/PreviewPane';
import ErrorOverlay from './components/ErrorOverlay';
import TimelineBar from './components/TimelineBar';
import BlockHighlight from './overlays/BlockHighlight';
import PlayerInfoOverlay from './overlays/PlayerInfoOverlay';
import { useDrag } from './hooks/useDrag';
import { useConnections } from './hooks/useConnections';
import { useDebounce } from './hooks/useDebounce';
import { useAutosave } from './hooks/useAutosave';
import { PlayerProvider, usePlayerContext } from './hooks/usePlayer';
import { blocksToCodeWithErrorHandling } from './lib/transform';
import { useState, useEffect, useRef } from 'react';
import type { BlockInstance } from './blocks/definitions';
import type { Connection } from './hooks/useConnections';
import type { RecordingFrame } from './hooks/usePlayer';

function AppContent({ recording, setRecording }: { 
  recording: RecordingFrame[] | null; 
  setRecording: (recording: RecordingFrame[] | null) => void;
}) {
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
  const canvasRef = useRef<HTMLDivElement | null>(null);
  
  // Visual debugger state
  const [isReplayMode, setIsReplayMode] = useState(false);
  const { state: playerState, controls: playerControls, currentFrameData } = usePlayerContext();

  // Auto-save functionality
  const handleRestoreSession = (data: { blocks: BlockInstance[]; connections: Connection[] }) => {
    setBlocks(data.blocks);
    setConnections(data.connections);
  };

  useAutosave(blocks, connections, handleRestoreSession);

  // Handle recording loading
  const handleOpenRecording = (recordingData: RecordingFrame[]) => {
    setRecording(recordingData);
    setIsReplayMode(true);
  };

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
          canvasRef={canvasRef}
          onOpenRecording={handleOpenRecording}
          isReplayMode={isReplayMode}
        />
        <div className="flex flex-1">
          <Palette isReplayMode={isReplayMode} />
          <Canvas 
            blocks={blocks} 
            connections={connections}
            draggingConnection={draggingConnection}
            ref={canvasRef}
            isReplayMode={isReplayMode}
            currentFrameData={currentFrameData}
            isStreaming={playerState.isStreaming}
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
        
        {/* Visual Debugger Components */}
        <TimelineBar 
          state={playerState}
          controls={playerControls}
          isVisible={isReplayMode}
        />
        
        {isReplayMode && (
          <>
            <BlockHighlight
              blocks={blocks}
              currentFrame={currentFrameData}
              isVisible={isReplayMode}
            />
            <PlayerInfoOverlay />
          </>
        )}
      </div>
    </DndContext>
  );
}

function App() {
  const [recording, setRecording] = useState<RecordingFrame[] | null>(null);
  
  return (
    <PlayerProvider recording={recording}>
      <AppContent recording={recording} setRecording={setRecording} />
    </PlayerProvider>
  );
}

export default App;
