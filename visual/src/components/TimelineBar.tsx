import React from 'react';
import { Play, Pause, SkipForward, SkipBack, Home, ArrowRight } from 'lucide-react';
import type { PlayerState, PlayerControls } from '../hooks/usePlayer';
import { Slider } from './ui/slider';

interface TimelineBarProps {
  state: PlayerState;
  controls: PlayerControls;
  isVisible: boolean;
}

const TimelineBar: React.FC<TimelineBarProps> = ({ state, controls, isVisible }) => {
  if (!isVisible) return null;

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleSliderChange = (value: number[]) => {
    controls.seek(value[0]);
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    switch (event.key) {
      case ' ':
        event.preventDefault();
        if (state.isPlaying) {
          controls.pause();
        } else {
          controls.play();
        }
        break;
      case 'ArrowLeft':
        event.preventDefault();
        controls.stepBackward();
        break;
      case 'ArrowRight':
        event.preventDefault();
        controls.stepForward();
        break;
      case 'Home':
        event.preventDefault();
        controls.jumpToStart();
        break;
      case 'End':
        event.preventDefault();
        controls.jumpToEnd();
        break;
    }
  };

  return (
    <div 
      className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-300 p-4 shadow-lg"
      onKeyDown={handleKeyDown}
      tabIndex={0}
      data-testid="timeline-bar"
    >
      <div className="flex items-center gap-4 max-w-4xl mx-auto">
        {/* Playback Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={controls.jumpToStart}
            disabled={state.currentFrame === 0}
            className="p-2 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Jump to start (Home)"
          >
            <Home size={16} />
          </button>
          
          <button
            onClick={controls.stepBackward}
            disabled={state.currentFrame === 0}
            className="p-2 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Step backward (←)"
          >
            <SkipBack size={16} />
          </button>
          
          <button
            onClick={state.isPlaying ? controls.pause : controls.play}
            disabled={state.totalFrames === 0}
            className="p-2 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            title={`${state.isPlaying ? 'Pause' : 'Play'} (Space)`}
          >
            {state.isPlaying ? <Pause size={16} /> : <Play size={16} />}
          </button>
          
          <button
            onClick={controls.stepForward}
            disabled={state.currentFrame >= state.totalFrames - 1}
            className="p-2 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Step forward (→)"
          >
            <SkipForward size={16} />
          </button>
          
          <button
            onClick={controls.jumpToEnd}
            disabled={state.currentFrame >= state.totalFrames - 1}
            className="p-2 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Jump to end (End)"
          >
            <ArrowRight size={16} />
          </button>
        </div>

        {/* Timeline Slider */}
        <div className="flex-1 flex items-center gap-4">
          <div className="text-sm text-gray-600 min-w-[60px]">
            {formatTime(state.currentTime)}
          </div>
          
          <div className="flex-1">
            <Slider
              value={[state.currentTime]}
              onValueChange={handleSliderChange}
              max={state.duration}
              step={0.1}
              disabled={state.totalFrames === 0}
              className="w-full"
              data-testid="timeline-slider"
            />
          </div>
          
          <div className="text-sm text-gray-600 min-w-[60px]">
            {formatTime(state.duration)}
          </div>
        </div>

        {/* Speed Control */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">Speed:</span>
          <select
            value={state.speed}
            onChange={(e) => controls.setSpeed(parseFloat(e.target.value))}
            className="text-sm border border-gray-300 rounded px-2 py-1"
            disabled={state.totalFrames === 0}
          >
            <option value={0.5}>0.5x</option>
            <option value={1}>1x</option>
            <option value={2}>2x</option>
          </select>
        </div>

        {/* Frame Info */}
        <div className="text-sm text-gray-600" data-testid="current-frame">
          Frame {state.currentFrame + 1} of {state.totalFrames}
          {state.isStreaming && (
            <span className="text-orange-600 ml-2">
              (Streaming: {state.frameWindow.frames.length} frames loaded)
            </span>
          )}
        </div>
      </div>

      {/* Keyboard Shortcuts Tooltip */}
      <div className="text-xs text-gray-500 mt-2 text-center">
        Space: Play/Pause • ←/→: Step • Home/End: Jump • Click timeline to seek
      </div>
    </div>
  );
};

export default TimelineBar; 