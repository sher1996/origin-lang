# Visual Mode

The Origin visual editor provides a drag-and-drop interface for building Origin programs using visual blocks.

## Features

### Three-Column Layout
- **Palette**: Drag blocks from the left sidebar
- **Canvas**: Build your program in the center area
- **Live Preview**: See real-time execution results on the right

### Block Palette
- **Say Block**: Output text to console
- **Let Block**: Define variables
- **Repeat Block**: Loop execution
- **Define Block**: Create functions
- **Call Block**: Call functions
- **Import Block**: Import modules
- **String Block**: String literals
- **Constant Block**: Numeric constants

### Import/Export Workflow

#### Import
1. **File Import**: Click "Import File" and select a `.origin` file
2. **Paste Code**: Click "Paste Code" and paste Origin code directly
3. **Auto-layout**: Imported blocks are automatically positioned in a vertical flow

#### Export
1. **Export Code**: Click "Export Code" to download the current canvas as a `.origin` file
2. **Round-trip**: Import → edit → export maintains semantic equivalence

### Live Preview
- **Real-time Execution**: Code updates automatically with 300ms debouncing
- **Sandboxed Environment**: Safe execution in iframe with console capture
- **Error Handling**: Syntax and runtime errors display with red overlay
- **Output Display**: Console.log results appear in the preview pane

### Connection System
- **Data Flow**: Connect block outputs to inputs with visual lines
- **Grid Snapping**: 10px grid for precise block positioning
- **Drag Connections**: Drag from output dots to create connections

### CLI Integration

```bash
# Import .origin file to JSON blocks
origin viz import examples/mapper_demo/hello.origin --out hello.json

# Export JSON blocks to .origin file
origin viz export hello.json --out hello_roundtrip.origin

# Verify round-trip (should be identical)
diff examples/mapper_demo/hello.origin hello_roundtrip.origin
```

### Development

```bash
# Start the visual editor
cd visual
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

## Architecture

### Block Definitions
- `visual/src/blocks/definitions.ts`: Block registry with serialize/deserialize functions
- Each block maps to an AST node type with inputs/outputs

### Transform Functions
- `visual/src/lib/transform.ts`: Frontend AST ↔ blocks conversion
- `src/transform/blocks_to_ast.py`: Backend CLI integration

### Auto-layout
- `visual/src/lib/autoLayout.ts`: Simple vertical flow positioning
- Imported blocks are automatically arranged

## Examples

### Hello World
```origin
say "Hello, Origin."
```

### Arithmetic
```origin
let x = 5
let y = x * 3 - 4
say y          # → 11
say x + y      # → 16
```

## Testing

### Backend Tests
```bash
python -m pytest tests/test_transform_roundtrip.py
```

### Frontend Tests
```bash
cd visual
npm test
```

## Future Enhancements

- [x] Connection lines between blocks
- [x] Real-time preview
- [x] Error overlay
- [x] Grid snapping
- [ ] Block parameter editing
- [ ] Syntax highlighting
- [ ] Block validation
- [ ] Undo/redo functionality
- [ ] Canvas panning and zooming 