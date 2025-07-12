import { DndContext, type DragEndEvent } from '@dnd-kit/core';
import Palette from './components/Palette';
import Canvas from './components/Canvas';
import Toolbar from './components/Toolbar';
import { useDrag } from './hooks/useDrag';

function App() {
  const { blocks, setBlocks, handleDragEnd } = useDrag();

  const onDragEnd = (event: DragEndEvent) => {
    handleDragEnd(event);
  };

  return (
    <DndContext onDragEnd={onDragEnd}>
      <div className="flex flex-col h-screen bg-gray-50">
        <Toolbar blocks={blocks} setBlocks={setBlocks} />
        <div className="flex flex-1">
          <Palette />
          <Canvas blocks={blocks} />
        </div>
      </div>
    </DndContext>
  );
}

export default App;
