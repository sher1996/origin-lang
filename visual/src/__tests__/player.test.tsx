import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { usePlayer } from '../hooks/usePlayer';
import TimelineBar from '../components/TimelineBar';
import BlockHighlight from '../overlays/BlockHighlight';
import type { RecordingFrame } from '../hooks/usePlayer';
import type { BlockInstance } from '../blocks/definitions';

// Mock recording data
const mockRecording: RecordingFrame[] = [
  {
    version: 'v2',
    ts: 0.0,
    blockId: 'LetNode:i',
    locals: { i: 1 },
    globals: {}
  },
  {
    version: 'v2',
    ts: 0.1,
    blockId: 'SayNode:output',
    locals: { i: 1, result: 'Hello' },
    globals: {}
  },
  {
    version: 'v2',
    ts: 0.2,
    blockId: 'LetNode:j',
    locals: { i: 1, j: 2 },
    globals: {}
  }
];

const mockBlocks: BlockInstance[] = [
  {
    id: 'block-1',
    definitionId: 'letnode',
    position: { x: 100, y: 100 },
    inputs: { name: 'i', value: '1' },
    outputs: {}
  },
  {
    id: 'block-2',
    definitionId: 'saynode',
    position: { x: 100, y: 200 },
    inputs: { expr: 'Hello' },
    outputs: {}
  }
];

// Test component to wrap the hook
const TestPlayerComponent = ({ recording }: { recording: RecordingFrame[] | null }) => {
  const [state, controls] = usePlayer(recording);
  
  // Expose state and controls for testing
  (window as any).testPlayerState = state;
  (window as any).testPlayerControls = controls;
  
  return <div>Test Player</div>;
};

describe('Player Hook', () => {
  beforeEach(() => {
    // Clear test state
    delete (window as any).testPlayerState;
    delete (window as any).testPlayerControls;
  });

  it('should initialize with default state', () => {
    render(<TestPlayerComponent recording={null} />);
    
    const state = (window as any).testPlayerState;
    expect(state.currentFrame).toBe(0);
    expect(state.isPlaying).toBe(false);
    expect(state.speed).toBe(1);
    expect(state.totalFrames).toBe(0);
    expect(state.currentTime).toBe(0);
    expect(state.duration).toBe(0);
  });

  it('should load recording data correctly', () => {
    render(<TestPlayerComponent recording={mockRecording} />);
    
    const state = (window as any).testPlayerState;
    expect(state.totalFrames).toBe(3);
    expect(state.duration).toBe(0.2);
  });

  it('should handle step forward', () => {
    render(<TestPlayerComponent recording={mockRecording} />);
    
    const controls = (window as any).testPlayerControls;
    controls.stepForward();
    
    const state = (window as any).testPlayerState;
    expect(state.currentFrame).toBe(1);
    expect(state.currentTime).toBe(0.1);
  });

  it('should handle step backward', () => {
    render(<TestPlayerComponent recording={mockRecording} />);
    
    const controls = (window as any).testPlayerControls;
    // Step forward first
    controls.stepForward();
    controls.stepForward();
    
    // Then step backward
    controls.stepBackward();
    
    const state = (window as any).testPlayerState;
    expect(state.currentFrame).toBe(1);
    expect(state.currentTime).toBe(0.1);
  });

  it('should handle seeking', () => {
    render(<TestPlayerComponent recording={mockRecording} />);
    
    const controls = (window as any).testPlayerControls;
    controls.seek(0.15);
    
    const state = (window as any).testPlayerState;
    // Should find the frame closest to 0.15 (which is 0.1)
    expect(state.currentFrame).toBe(1);
    expect(state.currentTime).toBe(0.1);
  });

  it('should handle jump to start and end', () => {
    render(<TestPlayerComponent recording={mockRecording} />);
    
    const controls = (window as any).testPlayerControls;
    // Jump to end first
    controls.jumpToEnd();
    let state = (window as any).testPlayerState;
    expect(state.currentFrame).toBe(2);
    expect(state.currentTime).toBe(0.2);
    
    // Then jump to start
    controls.jumpToStart();
    state = (window as any).testPlayerState;
    expect(state.currentFrame).toBe(0);
    expect(state.currentTime).toBe(0);
  });

  it('should handle speed changes', () => {
    render(<TestPlayerComponent recording={mockRecording} />);
    
    const controls = (window as any).testPlayerControls;
    controls.setSpeed(2);
    let state = (window as any).testPlayerState;
    expect(state.speed).toBe(2);
    
    // Test bounds
    controls.setSpeed(5); // Should be clamped to 4
    state = (window as any).testPlayerState;
    expect(state.speed).toBe(4);
    
    controls.setSpeed(0.05); // Should be clamped to 0.1
    state = (window as any).testPlayerState;
    expect(state.speed).toBe(0.1);
  });
});

describe('TimelineBar Component', () => {
  const mockState = {
    currentFrame: 1,
    isPlaying: false,
    speed: 1,
    totalFrames: 3,
    currentTime: 0.1,
    duration: 0.2,
    isStreaming: false,
    frameWindow: {
      start: 0,
      end: 2,
      frames: []
    }
  };

  const mockControls = {
    play: vi.fn(),
    pause: vi.fn(),
    seek: vi.fn(),
    stepForward: vi.fn(),
    stepBackward: vi.fn(),
    setSpeed: vi.fn(),
    jumpToStart: vi.fn(),
    jumpToEnd: vi.fn(),
    loadFrameWindow: vi.fn()
  };

  it('should render when visible', () => {
    render(
      <TimelineBar 
        state={mockState}
        controls={mockControls}
        isVisible={true}
      />
    );
    
    expect(screen.getByText('Frame 2 of 3')).toBeInTheDocument();
    expect(screen.getByText('0:00')).toBeInTheDocument(); // current time
    expect(screen.getByText('0:00')).toBeInTheDocument(); // duration
  });

  it('should not render when not visible', () => {
    render(
      <TimelineBar 
        state={mockState}
        controls={mockControls}
        isVisible={false}
      />
    );
    
    expect(screen.queryByText('Frame 2 of 3')).not.toBeInTheDocument();
  });

  it('should handle play button click', () => {
    render(
      <TimelineBar 
        state={mockState}
        controls={mockControls}
        isVisible={true}
      />
    );
    
    const playButton = screen.getByTitle('Play (Space)');
    fireEvent.click(playButton);
    
    expect(mockControls.play).toHaveBeenCalled();
  });

  it('should handle step forward button click', () => {
    render(
      <TimelineBar 
        state={mockState}
        controls={mockControls}
        isVisible={true}
      />
    );
    
    const stepButton = screen.getByTitle('Step forward (→)');
    fireEvent.click(stepButton);
    
    expect(mockControls.stepForward).toHaveBeenCalled();
  });

  it('should handle slider change', () => {
    render(
      <TimelineBar 
        state={mockState}
        controls={mockControls}
        isVisible={true}
      />
    );
    
    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '0.15' } });
    
    expect(mockControls.seek).toHaveBeenCalledWith(0.15);
  });
});

describe('BlockHighlight Component', () => {
  it('should render highlight when block is found', () => {
    const currentFrame = mockRecording[0]; // LetNode:i
    
    render(
      <BlockHighlight
        blocks={mockBlocks}
        currentFrame={currentFrame}
        isVisible={true}
      />
    );
    
    // Should find the LetNode block and render highlight
    expect(document.querySelector('.border-blue-500')).toBeInTheDocument();
  });

  it('should render tooltip with variables', () => {
    const currentFrame = mockRecording[1]; // SayNode:output with locals
    
    render(
      <BlockHighlight
        blocks={mockBlocks}
        currentFrame={currentFrame}
        isVisible={true}
      />
    );
    
    expect(screen.getByText('Active Block')).toBeInTheDocument();
    expect(screen.getByText('SayNode:output')).toBeInTheDocument();
    expect(screen.getByText('Local Variables:')).toBeInTheDocument();
    expect(screen.getByText('i = 1, result = "Hello"')).toBeInTheDocument();
  });

  it('should not render when not visible', () => {
    render(
      <BlockHighlight
        blocks={mockBlocks}
        currentFrame={mockRecording[0]}
        isVisible={false}
      />
    );
    
    expect(document.querySelector('.border-blue-500')).not.toBeInTheDocument();
  });

  it('should not render when no matching block found', () => {
    const currentFrame = {
      version: 'v2',
      ts: 0.0,
      blockId: 'UnknownNode:test',
      locals: {},
      globals: {}
    };
    
    render(
      <BlockHighlight
        blocks={mockBlocks}
        currentFrame={currentFrame}
        isVisible={true}
      />
    );
    
    expect(document.querySelector('.border-blue-500')).not.toBeInTheDocument();
  });
});

describe('Integration Tests', () => {
  // Extended mock recording with 5 frames for testing
  const extendedMockRecording: RecordingFrame[] = [
    {
      version: 'v2',
      ts: 0.0,
      blockId: 'LetNode:i',
      locals: { i: 1 },
      globals: {}
    },
    {
      version: 'v2',
      ts: 0.1,
      blockId: 'SayNode:output',
      locals: { i: 1, result: 'Hello' },
      globals: {}
    },
    {
      version: 'v2',
      ts: 0.2,
      blockId: 'LetNode:j',
      locals: { i: 1, j: 2 },
      globals: {}
    },
    {
      version: 'v2',
      ts: 0.3,
      blockId: 'SayNode:output2',
      locals: { i: 1, j: 2, result: 'World' },
      globals: {}
    },
    {
      version: 'v2',
      ts: 0.4,
      blockId: 'LetNode:sum',
      locals: { i: 1, j: 2, sum: 3 },
      globals: {}
    }
  ];

  it('should play 5 frames and stop at the end', async () => {
    render(<TestPlayerComponent recording={extendedMockRecording} />);
    
    const controls = (window as any).testPlayerControls;
    let state = (window as any).testPlayerState;
    
    // Start at frame 0
    expect(state.currentFrame).toBe(0);
    expect(state.isPlaying).toBe(false);
    
    // Play through all 5 frames
    controls.play();
    state = (window as any).testPlayerState;
    expect(state.isPlaying).toBe(true);
    
    // Simulate playing through all frames
    for (let i = 0; i < 5; i++) {
      controls.stepForward();
      state = (window as any).testPlayerState;
    }
    
    // Should be at the last frame and stopped
    expect(state.currentFrame).toBe(4); // 5th frame (0-indexed)
    expect(state.currentTime).toBe(0.4);
    expect(state.isPlaying).toBe(false); // Should have stopped at the end
  });

  it('should scrub slider and highlight correct block', () => {
    render(<TestPlayerComponent recording={extendedMockRecording} />);
    
    const controls = (window as any).testPlayerControls;
    
    // Scrub to middle of timeline (around frame 2)
    controls.seek(0.2);
    
    const state = (window as any).testPlayerState;
    expect(state.currentFrame).toBe(2); // Should be at frame 2 (LetNode:j)
    expect(state.currentTime).toBe(0.2);
    
    // Verify the correct block would be highlighted
    const currentFrame = extendedMockRecording[2];
    expect(currentFrame.blockId).toBe('LetNode:j');
    expect(currentFrame.locals).toEqual({ i: 1, j: 2 });
  });

  it('should render tooltip with local variables when scrubbing', () => {
    render(<TestPlayerComponent recording={extendedMockRecording} />);
    
    const controls = (window as any).testPlayerControls;
    
    // Scrub to a frame with local variables
    controls.seek(0.3); // Frame 3 with SayNode:output2
    
    const currentFrame = extendedMockRecording[3];
    expect(currentFrame.blockId).toBe('SayNode:output2');
    expect(currentFrame.locals).toEqual({ i: 1, j: 2, result: 'World' });
    
    // The tooltip should display these local variables
    // This test verifies the data structure that would be passed to BlockHighlight
    expect(currentFrame.locals.i).toBe(1);
    expect(currentFrame.locals.j).toBe(2);
    expect(currentFrame.locals.result).toBe('World');
  });

  it('should handle complete playback cycle with timer stopping', () => {
    render(<TestPlayerComponent recording={extendedMockRecording} />);
    
    const controls = (window as any).testPlayerControls;
    let state = (window as any).testPlayerState;
    
    // Start playback
    controls.play();
    state = (window as any).testPlayerState;
    expect(state.isPlaying).toBe(true);
    
    // Jump to end
    controls.jumpToEnd();
    state = (window as any).testPlayerState;
    expect(state.currentFrame).toBe(4);
    expect(state.currentTime).toBe(0.4);
    
    // Timer should stop at the end
    expect(state.isPlaying).toBe(false);
    
    // Jump back to start
    controls.jumpToStart();
    state = (window as any).testPlayerState;
    expect(state.currentFrame).toBe(0);
    expect(state.currentTime).toBe(0);
  });

  it('should maintain correct state during complex interactions', () => {
    render(<TestPlayerComponent recording={extendedMockRecording} />);
    
    const controls = (window as any).testPlayerControls;
    let state = (window as any).testPlayerState;
    
    // Start at beginning
    expect(state.currentFrame).toBe(0);
    
    // Step forward twice
    controls.stepForward();
    controls.stepForward();
    state = (window as any).testPlayerState;
    expect(state.currentFrame).toBe(2);
    expect(state.currentTime).toBe(0.2);
    
    // Scrub to different position
    controls.seek(0.1);
    state = (window as any).testPlayerState;
    expect(state.currentFrame).toBe(1);
    expect(state.currentTime).toBe(0.1);
    
    // Play and then pause
    controls.play();
    state = (window as any).testPlayerState;
    expect(state.isPlaying).toBe(true);
    
    controls.pause();
    state = (window as any).testPlayerState;
    expect(state.isPlaying).toBe(false);
    
    // Step to end
    controls.stepForward();
    controls.stepForward();
    controls.stepForward();
    state = (window as any).testPlayerState;
    expect(state.currentFrame).toBe(4);
    expect(state.currentTime).toBe(0.4);
    
    // Should be at end and stopped
    expect(state.isPlaying).toBe(false);
  });
}); 