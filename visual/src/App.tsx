import { DndContext, type DragEndEvent } from '@dnd-kit/core';
import Palette from './components/Palette';
import Canvas from './components/Canvas';
import Toolbar from './components/Toolbar';
import { useDrag } from './hooks/useDrag';

function App() {
  const { 
    blocks, 
    setBlocks, 
    handleDragEnd, 
    updateBlockInput, 
    removeBlock,
    importBlocks 
  } = useDrag();

  const onDragEnd = (event: DragEndEvent) => {
    handleDragEnd(event);
  };

  const handleBlocksChange = (newBlocks: any[]) => {
    importBlocks(newBlocks);
  };

  return (
    <DndContext onDragEnd={onDragEnd}>
      <div className="flex flex-col h-screen bg-gray-50">
        <Toolbar blocks={blocks} onBlocksChange={handleBlocksChange} />
        <div className="flex flex-1">
          <Palette />
          <Canvas 
            blocks={blocks} 
            onInputChange={updateBlockInput}
            onBlockRemove={removeBlock}
          />
        </div>
      </div>
    </DndContext>
  );
}

export default App;
