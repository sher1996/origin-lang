# Live Preview Demo

## Chapter 24 - Live Preview Pane Implementation

This demo shows the new live preview functionality in the Origin visual editor.

### Features Implemented

1. **Three-Column Layout**
   - Palette (left): Drag blocks from here
   - Canvas (center): Build your program
   - Preview (right): See live execution results

2. **Live Preview**
   - Real-time code execution with 300ms debouncing
   - Sandboxed iframe environment
   - Console.log output capture
   - Error display with red overlay

3. **Connection System**
   - Visual connection lines between blocks
   - Input/output connection dots
   - Grid snapping for precise positioning

4. **Error Handling**
   - Syntax error detection
   - Runtime error display
   - Error overlay with dismiss functionality

### Demo Steps

1. **Start the Development Server**
   ```bash
   cd visual
   npm run dev
   ```

2. **Open the Visual Editor**
   - Navigate to `http://localhost:5175`
   - You'll see the three-column layout

3. **Test Live Preview**
   - Drag a "Constant" block from the palette to the canvas
   - Change the constant value to `42`
   - Watch the preview pane update in real-time
   - The preview shows: `42`

4. **Test Error Handling**
   - Drag a "Say" block to the canvas
   - Leave the expression empty or enter invalid syntax
   - See the red error overlay appear
   - Fix the error and watch it disappear

5. **Test Connections**
   - Drag multiple blocks to the canvas
   - Notice the input (green) and output (blue) dots
   - Connection lines will be implemented in future iterations

### Technical Implementation

- **PreviewPane.tsx**: iframe sandbox with Origin interpreter
- **useDebounce.ts**: 300ms debouncing for smooth updates
- **ConnectionLines.tsx**: SVG-based connection rendering
- **ErrorOverlay.tsx**: Modal error display
- **useConnections.ts**: Connection state management

### Files Modified

- `visual/src/App.tsx`: Three-column layout with preview
- `visual/src/components/PreviewPane.tsx`: Live preview component
- `visual/src/components/ConnectionLines.tsx`: Connection visualization
- `visual/src/components/ErrorOverlay.tsx`: Error display
- `visual/src/hooks/useDebounce.ts`: Debouncing hook
- `visual/src/hooks/useConnections.ts`: Connection management
- `visual/src/lib/transform.ts`: Enhanced with error handling
- `visual/src/blocks/definitions.ts`: Added Constant block
- `docs/visual-mode.md`: Updated documentation
- `CHANGELOG.md`: Added version 0.5.0

### Testing

```bash
# Run tests
npm test

# Run tests with UI
npm run test:ui
```

### Next Steps

- Implement canvas panning and zooming
- Add block parameter editing
- Enhance connection drag-and-drop
- Add syntax highlighting
- Implement undo/redo functionality 