import React from 'react';
import { usePlayerContext } from '../hooks/usePlayer';

const PlayerInfoOverlay: React.FC = () => {
  const { state, currentFrameData } = usePlayerContext();

  if (!currentFrameData) return null;

  return (
    <div className="fixed top-4 right-4 bg-white border border-gray-300 rounded-lg shadow-lg p-4 z-30">
      <div className="text-sm font-semibold mb-2">Player Info</div>
      <div className="text-xs space-y-1">
        <div>Frame: {state.currentFrame + 1} / {state.totalFrames}</div>
        <div>Time: {state.currentTime.toFixed(2)}s</div>
        <div>Speed: {state.speed}x</div>
        <div>Status: {state.isPlaying ? 'Playing' : 'Paused'}</div>
        <div className="mt-2 pt-2 border-t border-gray-200">
          <div className="font-semibold">Current Block:</div>
          <div>{currentFrameData.blockId}</div>
          {Object.keys(currentFrameData.locals).length > 0 && (
            <div className="mt-1">
              <div className="font-semibold">Locals:</div>
              <div className="text-gray-600">
                {Object.entries(currentFrameData.locals)
                  .map(([key, value]) => `${key}: ${JSON.stringify(value)}`)
                  .join(', ')}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PlayerInfoOverlay; 