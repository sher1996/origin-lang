import { useState, useEffect, useRef, useCallback, createContext, useContext, useMemo } from 'react';
import type { ReactNode } from 'react';

export interface RecordingFrame {
  version: string;
  ts: number;
  blockId: string;
  locals: Record<string, any>;
  globals: Record<string, any>;
}

export interface PlayerState {
  currentFrame: number;
  isPlaying: boolean;
  speed: number;
  totalFrames: number;
  currentTime: number;
  duration: number;
  isStreaming: boolean;
  frameWindow: {
    start: number;
    end: number;
    frames: RecordingFrame[];
  };
}

export interface PlayerControls {
  play: () => void;
  pause: () => void;
  seek: (time: number) => void;
  stepForward: () => void;
  stepBackward: () => void;
  setSpeed: (speed: number) => void;
  jumpToStart: () => void;
  jumpToEnd: () => void;
  loadFrameWindow: (centerFrame: number) => void;
}

// Streaming configuration
const FRAME_WINDOW_SIZE = 250; // ±250 frames around current position
const LARGE_RECORDING_THRESHOLD = 10000; // 10k frames threshold

// Create context for player state
interface PlayerContextType {
  state: PlayerState;
  controls: PlayerControls;
  currentFrameData: RecordingFrame | null;
}

const PlayerContext = createContext<PlayerContextType | null>(null);

// Provider component
interface PlayerProviderProps {
  children: ReactNode;
  recording: RecordingFrame[] | null;
}

export function PlayerProvider({ children, recording }: PlayerProviderProps) {
  const [currentFrame, setCurrentFrame] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [currentTime, setCurrentTime] = useState(0);
  const [frameWindow, setFrameWindow] = useState<{
    start: number;
    end: number;
    frames: RecordingFrame[];
  }>({ start: 0, end: 0, frames: [] });
  
  const animationRef = useRef<number | undefined>(undefined);
  const lastFrameTime = useRef<number>(0);
  const fullRecordingRef = useRef<RecordingFrame[] | null>(null);

  // Update full recording ref when recording changes
  useEffect(() => {
    fullRecordingRef.current = recording;
  }, [recording]);

  const totalFrames = recording?.length || 0;
  const duration = recording?.length ? recording[recording.length - 1].ts : 0;
  const isStreaming = totalFrames >= LARGE_RECORDING_THRESHOLD;

  // Initialize frame window
  useEffect(() => {
    if (!recording) {
      setFrameWindow({ start: 0, end: 0, frames: [] });
      return;
    }

    if (isStreaming) {
      // For large recordings, start with first window
      const end = Math.min(FRAME_WINDOW_SIZE, totalFrames - 1);
      setFrameWindow({
        start: 0,
        end,
        frames: recording.slice(0, end + 1)
      });
    } else {
      // For small recordings, load everything
      setFrameWindow({
        start: 0,
        end: totalFrames - 1,
        frames: recording
      });
    }
  }, [recording, isStreaming, totalFrames]);

  // Get current frame data from window or full recording
  const currentFrameData = useMemo(() => {
    if (!recording) return null;
    
    if (isStreaming) {
      // For streaming, get from frame window
      const windowIndex = currentFrame - frameWindow.start;
      return windowIndex >= 0 && windowIndex < frameWindow.frames.length 
        ? frameWindow.frames[windowIndex] 
        : null;
    } else {
      // For small recordings, get directly
      return recording[currentFrame] || null;
    }
  }, [recording, currentFrame, isStreaming, frameWindow]);

  // Load frame window around a specific frame
  const loadFrameWindow = useCallback((centerFrame: number) => {
    if (!recording || !isStreaming) return;

    const halfWindow = Math.floor(FRAME_WINDOW_SIZE / 2);
    const start = Math.max(0, centerFrame - halfWindow);
    const end = Math.min(totalFrames - 1, centerFrame + halfWindow);
    
    setFrameWindow({
      start,
      end,
      frames: recording.slice(start, end + 1)
    });
  }, [recording, isStreaming, totalFrames]);

  // Check if we need to load a new frame window
  const checkAndLoadFrameWindow = useCallback((newFrame: number) => {
    if (!isStreaming) return;
    
    const windowCenter = frameWindow.start + Math.floor(frameWindow.frames.length / 2);
    const distanceFromCenter = Math.abs(newFrame - windowCenter);
    
    // If we're getting close to the edge, load a new window
    if (distanceFromCenter > FRAME_WINDOW_SIZE / 3) {
      loadFrameWindow(newFrame);
    }
  }, [isStreaming, frameWindow, loadFrameWindow]);

  const play = useCallback(() => {
    if (!recording || currentFrame >= totalFrames - 1) return;
    setIsPlaying(true);
  }, [recording, currentFrame, totalFrames]);

  const pause = useCallback(() => {
    setIsPlaying(false);
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
  }, []);

  const seek = useCallback((time: number) => {
    if (!recording) return;
    
    // Find the frame closest to the target time
    const targetFrame = recording.findIndex(frame => frame.ts >= time);
    const frameIndex = targetFrame >= 0 ? targetFrame : recording.length - 1;
    const newFrame = Math.max(0, Math.min(frameIndex, totalFrames - 1));
    
    setCurrentFrame(newFrame);
    setCurrentTime(recording[frameIndex]?.ts || 0);
    
    // Check if we need to load a new frame window
    checkAndLoadFrameWindow(newFrame);
  }, [recording, totalFrames, checkAndLoadFrameWindow]);

  const stepForward = useCallback(() => {
    if (!recording || currentFrame >= totalFrames - 1) return;
    const newFrame = currentFrame + 1;
    setCurrentFrame(newFrame);
    setCurrentTime(recording[newFrame]?.ts || 0);
    checkAndLoadFrameWindow(newFrame);
  }, [recording, currentFrame, totalFrames, checkAndLoadFrameWindow]);

  const stepBackward = useCallback(() => {
    if (!recording || currentFrame <= 0) return;
    const newFrame = currentFrame - 1;
    setCurrentFrame(newFrame);
    setCurrentTime(recording[newFrame]?.ts || 0);
    checkAndLoadFrameWindow(newFrame);
  }, [recording, currentFrame, checkAndLoadFrameWindow]);

  const jumpToStart = useCallback(() => {
    setCurrentFrame(0);
    setCurrentTime(0);
    if (isStreaming) {
      loadFrameWindow(0);
    }
  }, [isStreaming, loadFrameWindow]);

  const jumpToEnd = useCallback(() => {
    if (!recording) return;
    const endFrame = totalFrames - 1;
    setCurrentFrame(endFrame);
    setCurrentTime(duration);
    if (isStreaming) {
      loadFrameWindow(endFrame);
    }
  }, [recording, totalFrames, duration, isStreaming, loadFrameWindow]);

  const updateSpeed = useCallback((newSpeed: number) => {
    setSpeed(Math.max(0.1, Math.min(4, newSpeed)));
  }, []);

  // Animation loop for playback
  useEffect(() => {
    if (!isPlaying || !recording || currentFrame >= totalFrames - 1) {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      return;
    }

    const animate = (timestamp: number) => {
      if (!lastFrameTime.current) {
        lastFrameTime.current = timestamp;
      }

      const deltaTime = (timestamp - lastFrameTime.current) * speed / 1000;
      const currentFrameTime = recording[currentFrame]?.ts || 0;
      const nextFrameTime = recording[currentFrame + 1]?.ts || currentFrameTime;

      if (currentTime + deltaTime >= nextFrameTime) {
        // Move to next frame
        const newFrame = currentFrame + 1;
        setCurrentFrame(newFrame);
        setCurrentTime(recording[newFrame]?.ts || 0);
        checkAndLoadFrameWindow(newFrame);
        
        if (newFrame >= totalFrames - 1) {
          setIsPlaying(false);
          return;
        }
      } else {
        setCurrentTime(currentTime + deltaTime);
      }

      lastFrameTime.current = timestamp;
      animationRef.current = requestAnimationFrame(animate);
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isPlaying, recording, currentFrame, currentTime, speed, totalFrames, checkAndLoadFrameWindow]);

  // Reset when recording changes
  useEffect(() => {
    setCurrentFrame(0);
    setCurrentTime(0);
    setIsPlaying(false);
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
  }, [recording]);

  const state: PlayerState = {
    currentFrame,
    isPlaying,
    speed,
    totalFrames,
    currentTime,
    duration,
    isStreaming,
    frameWindow
  };

  const controls: PlayerControls = {
    play,
    pause,
    seek,
    stepForward,
    stepBackward,
    setSpeed: updateSpeed,
    jumpToStart,
    jumpToEnd,
    loadFrameWindow
  };

  const contextValue: PlayerContextType = {
    state,
    controls,
    currentFrameData
  };

  return (
    <PlayerContext.Provider value={contextValue}>
      {children}
    </PlayerContext.Provider>
  );
}

// Hook to use player context
export function usePlayerContext(): PlayerContextType {
  const context = useContext(PlayerContext);
  if (!context) {
    throw new Error('usePlayerContext must be used within a PlayerProvider');
  }
  return context;
}

// Original usePlayer hook (for backward compatibility)
export function usePlayer(recording: RecordingFrame[] | null): [PlayerState, PlayerControls] {
  const [currentFrame, setCurrentFrame] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [currentTime, setCurrentTime] = useState(0);
  const animationRef = useRef<number | undefined>(undefined);
  const lastFrameTime = useRef<number>(0);

  const totalFrames = recording?.length || 0;
  const duration = recording?.length ? recording[recording.length - 1].ts : 0;

  const play = useCallback(() => {
    if (!recording || currentFrame >= totalFrames - 1) return;
    setIsPlaying(true);
  }, [recording, currentFrame, totalFrames]);

  const pause = useCallback(() => {
    setIsPlaying(false);
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
  }, []);

  const seek = useCallback((time: number) => {
    if (!recording) return;
    
    // Find the frame closest to the target time
    const targetFrame = recording.findIndex(frame => frame.ts >= time);
    const frameIndex = targetFrame >= 0 ? targetFrame : recording.length - 1;
    
    setCurrentFrame(Math.max(0, Math.min(frameIndex, totalFrames - 1)));
    setCurrentTime(recording[frameIndex]?.ts || 0);
  }, [recording, totalFrames]);

  const stepForward = useCallback(() => {
    if (!recording || currentFrame >= totalFrames - 1) return;
    const newFrame = currentFrame + 1;
    setCurrentFrame(newFrame);
    setCurrentTime(recording[newFrame]?.ts || 0);
  }, [recording, currentFrame, totalFrames]);

  const stepBackward = useCallback(() => {
    if (!recording || currentFrame <= 0) return;
    const newFrame = currentFrame - 1;
    setCurrentFrame(newFrame);
    setCurrentTime(recording[newFrame]?.ts || 0);
  }, [recording, currentFrame]);

  const jumpToStart = useCallback(() => {
    setCurrentFrame(0);
    setCurrentTime(0);
  }, []);

  const jumpToEnd = useCallback(() => {
    if (!recording) return;
    setCurrentFrame(totalFrames - 1);
    setCurrentTime(duration);
  }, [recording, totalFrames, duration]);

  const updateSpeed = useCallback((newSpeed: number) => {
    setSpeed(Math.max(0.1, Math.min(4, newSpeed)));
  }, []);

  // Animation loop for playback
  useEffect(() => {
    if (!isPlaying || !recording || currentFrame >= totalFrames - 1) {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      return;
    }

    const animate = (timestamp: number) => {
      if (!lastFrameTime.current) {
        lastFrameTime.current = timestamp;
      }

      const deltaTime = (timestamp - lastFrameTime.current) * speed / 1000;
      const currentFrameTime = recording[currentFrame]?.ts || 0;
      const nextFrameTime = recording[currentFrame + 1]?.ts || currentFrameTime;

      if (currentTime + deltaTime >= nextFrameTime) {
        // Move to next frame
        const newFrame = currentFrame + 1;
        setCurrentFrame(newFrame);
        setCurrentTime(recording[newFrame]?.ts || 0);
        
        if (newFrame >= totalFrames - 1) {
          setIsPlaying(false);
          return;
        }
      } else {
        setCurrentTime(currentTime + deltaTime);
      }

      lastFrameTime.current = timestamp;
      animationRef.current = requestAnimationFrame(animate);
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isPlaying, recording, currentFrame, currentTime, speed, totalFrames]);

  // Reset when recording changes
  useEffect(() => {
    setCurrentFrame(0);
    setCurrentTime(0);
    setIsPlaying(false);
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
  }, [recording]);

  const state: PlayerState = {
    currentFrame,
    isPlaying,
    speed,
    totalFrames,
    currentTime,
    duration,
    isStreaming: false,
    frameWindow: { start: 0, end: 0, frames: [] }
  };

  const controls: PlayerControls = {
    play,
    pause,
    seek,
    stepForward,
    stepBackward,
    setSpeed: updateSpeed,
    jumpToStart,
    jumpToEnd,
    loadFrameWindow: (_centerFrame: number) => {}
  };

  return [state, controls];
} 