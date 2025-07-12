import { DndContext, type DragEndEvent } from '@dnd-kit/core';
import Palette from './components/Palette';
import Canvas from './components/Canvas';
import { useDrag } from './hooks/useDrag';

function App() {
  const { blocks, handleDragEnd } = useDrag();

  const onDragEnd = (event: DragEndEvent) => {
    handleDragEnd(event);
  };

  return (
    <DndContext onDragEnd={onDragEnd}>
      <div className="flex h-screen bg-gray-50">
        <Palette />
        <Canvas blocks={blocks} />
      </div>
    </DndContext>
  );
}

export default App;
