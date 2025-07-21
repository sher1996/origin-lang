# Visual Debugger Overlay

The Visual Debugger Overlay is a powerful feature that allows you to replay execution recordings visually, stepping through code execution with a timeline interface and block highlighting.

## Overview

The visual debugger transforms the Origin visual editor into a replay environment where you can:

- **Load execution recordings** (`.orirec` files) created by the Origin recorder
- **Step through execution** frame by frame or play at variable speeds
- **See highlighted blocks** that are currently executing
- **View variable values** in real-time tooltips
- **Scrub through time** using an intuitive timeline slider

## Getting Started

### 1. Create a Recording

First, you need to create an execution recording. Run your Origin program with the recorder enabled:

```bash
origin run --record output.orirec your_program.origin
```

This will create a `.orirec` file containing execution frames with timing and variable state information.

### 2. Open the Visual Editor

Start the visual editor:

```bash
origin viz
```

### 3. Load a Recording

In the visual editor toolbar, click **"Open Recording"** and select your `.orirec` file. The editor will automatically switch to replay mode.

## Using the Timeline

Once a recording is loaded, a timeline bar appears at the bottom of the screen with the following controls:

### Playback Controls

- **Play/Pause** (Space): Start or stop automatic playback
- **Step Forward** (→): Move to the next execution frame
- **Step Backward** (←): Move to the previous execution frame
- **Jump to Start** (Home): Return to the beginning of the recording
- **Jump to End** (End): Skip to the end of the recording

### Timeline Slider

The central slider allows you to:
- **Scrub through time** by dragging the slider
- **See current time** and total duration
- **Jump to any point** in the execution

### Speed Control

Adjust playback speed:
- **0.5x**: Slow motion for detailed analysis
- **1x**: Normal speed
- **2x**: Fast forward for quick overview

## Block Highlighting

When a recording is loaded, the visual editor shows:

### Active Block Highlight

- **Blue pulsing ring** around the currently executing block
- **Semi-transparent overlay** to make the active block stand out
- **Real-time updates** as execution progresses

### Variable Tooltip

A tooltip appears next to the highlighted block showing:

- **Block ID**: The specific node being executed
- **Local Variables**: Current values of local variables
- **Global Variables**: Current values of global variables

Example tooltip:
```
Active Block
LetNode:i
Local Variables:
i = 5, result = "Fizz"
```

## Recording Format

The `.orirec` files use a JSONL (JSON Lines) format with the following structure:

```json
{"version": "v2", "ts": 0.0, "blockId": "LetNode:i", "locals": {"i": 1}, "globals": {}}
{"version": "v2", "ts": 0.1, "blockId": "SayNode:output", "locals": {"i": 1, "result": "Hello"}, "globals": {}}
```

Each line represents one execution frame with:
- `version`: Recording format version (currently "v2")
- `ts`: Timestamp in seconds
- `blockId`: Identifier for the executing block
- `locals`: Local variable state
- `globals`: Global variable state

## Example: FizzBuzz Debugging

Let's walk through debugging a FizzBuzz program:

1. **Create the program** in the visual editor
2. **Export the code** and run it with recording enabled
3. **Load the recording** back into the visual editor
4. **Step through execution** to see:
   - Variable `i` incrementing from 1 to 3
   - Conditional logic determining "Fizz" or the number
   - Output statements being executed

The timeline shows the progression through each iteration, and the block highlighting reveals exactly which part of the logic is being executed at each step.

### Demo GIF

![FizzBuzz Visual Debugger Demo](fizzbuzz_debugger_demo.gif)

*The visual debugger stepping through a FizzBuzz program, showing block highlighting and variable state changes in real-time.*

### Try It Yourself

1. **Load the demo recording**:
   ```bash
   # Start the visual editor
   origin viz
   
   # Open the FizzBuzz recording
   # File: examples/recordings/fizzbuzz.orirec
   ```

2. **Step through execution**:
   - Use the timeline slider to scrub through time
   - Press → to step forward frame by frame
   - Watch the blue highlighting show which block is active
   - See variable values change in real-time tooltips

3. **Create your own recording**:
   ```bash
   # Run the FizzBuzz program with recording
   origin run examples/fizzbuzz.origin --record
   ```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Space | Play/Pause |
| ← | Step backward |
| → | Step forward |
| Home | Jump to start |
| End | Jump to end |

## Performance Considerations

For large recordings (10,000+ frames):
- **Streaming playback**: Only ±250 frames are kept in memory
- **DOM recycling**: React efficiently updates only changed elements
- **Frame skipping**: Automatic frame dropping during fast playback

## Troubleshooting

### Recording Won't Load
- Ensure the file has `.orirec` extension
- Check that the recording uses v2 format
- Verify the JSON is valid (no syntax errors)

### No Blocks Highlighted
- Make sure the recording block IDs match your visual blocks
- Check that the block types are compatible
- Verify the recording was created from the same program

### Timeline Not Responding
- Try refreshing the page
- Check browser console for JavaScript errors
- Ensure the recording file is not corrupted

## Advanced Features

### Custom Block Mapping

The debugger automatically maps recording block IDs to visual blocks:
- `LetNode:variable` → `letnode` block type
- `SayNode:expression` → `saynode` block type
- `RepeatNode:loop` → `repeatnode` block type

### Variable State Tracking

The debugger preserves the complete execution state:
- **Variable history**: See how values change over time
- **Scope awareness**: Distinguish local vs global variables
- **Type preservation**: Maintain data types (numbers, strings, etc.)

### Export Debug Sessions

You can export debug sessions for sharing:
- **Screenshot**: Capture the current state
- **Recording**: Save the execution trace
- **Annotations**: Add notes to specific frames

## Integration with Development Workflow

The visual debugger integrates seamlessly with the Origin development workflow:

1. **Design** your program in the visual editor
2. **Export** the code to `.origin` files
3. **Record** execution with the CLI recorder
4. **Debug** visually by loading recordings back
5. **Iterate** on your design based on execution insights

This creates a powerful feedback loop for understanding and improving your Origin programs. 