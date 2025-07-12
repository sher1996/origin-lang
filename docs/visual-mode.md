# Visual Mode

The Origin visual editor provides a block-based interface for creating Origin programs. It features a drag-and-drop canvas, live preview, and comprehensive save/load functionality.

## Features

### Block-Based Programming
- **Drag & Drop**: Drag blocks from the palette to the canvas
- **Visual Connections**: Connect blocks with data flow lines
- **Grid Layout**: Snap blocks to a 10px grid for precise positioning
- **Live Preview**: Real-time code execution with error display

### Import/Export
- **File Import**: Load `.origin` files directly into the editor
- **Paste Code**: Paste Origin code to create blocks
- **Export Code**: Download generated code as `.origin` files
- **Save Projects**: Save complete projects as `.originproj` files
- **Open Projects**: Load saved projects with full state restoration

### Auto-Save
- **Session Persistence**: Automatic save every 10 seconds
- **Browser Storage**: Uses localStorage for session recovery
- **Restore Prompt**: "Restore last session?" on page load
- **One-Hour Expiry**: Auto-saved sessions expire after 1 hour

## Project Files (.originproj)

Origin projects are saved as `.originproj` files, which are ZIP archives containing:

- `blocks.json` - Visual editor block definitions and positions
- `connections.json` - Block connection data
- `main.origin` - Generated Origin source code
- `README.md` - Auto-generated project documentation
- `metadata.json` - Project metadata (name, version, timestamps)

### Saving Projects

1. **Visual Editor**: Click "Save Project" button in toolbar
2. **CLI**: `origin viz save myproject.originproj` (from project directory)

### Opening Projects

1. **Visual Editor**: Click "Open Project" button, select `.originproj` file
2. **CLI**: `origin viz open myproject.originproj` (extracts to current directory)

## Usage

### Getting Started

1. **Open the Editor**: Navigate to the visual editor
2. **Add Blocks**: Drag blocks from the palette to the canvas
3. **Connect Blocks**: Click and drag from output dots to input dots
4. **Preview Code**: Generated code appears in the preview pane
5. **Save Project**: Click "Save Project" to download `.originproj` file

### Import/Export Workflow

#### Importing Code
1. **File Import**: Click "Import File" and select a `.origin` file
2. **Paste Code**: Click "Paste Code" and paste Origin code
3. **Auto-layout**: Blocks are automatically positioned vertically

#### Exporting Code
1. **Export Code**: Click "Export Code" to download as `.origin` file
2. **Save Project**: Click "Save Project" to save complete project state

### CLI Integration

The visual editor integrates with the Origin CLI:

```bash
# Import .origin file to JSON blocks
origin viz import program.origin --out blocks.json

# Export JSON blocks to .origin file  
origin viz export blocks.json --out program.origin

# Save current project as .originproj
origin viz save myproject.originproj

# Open .originproj file
origin viz open myproject.originproj
```

## Block Types

The visual editor supports these block types:

- **Say**: Output text or expressions
- **Let**: Variable assignment
- **Repeat**: Loops with count
- **Define**: Function definitions
- **Call**: Function calls
- **Import**: Package imports
- **String**: String literals
- **Constant**: Numeric constants

## Architecture

### Frontend Components
- `Palette.tsx` - Block palette with drag sources
- `Canvas.tsx` - Drop zone with grid and connections
- `Toolbar.tsx` - Import/export and save/load controls
- `PreviewPane.tsx` - Live code execution and output
- `ConnectionLines.tsx` - SVG connection rendering
- `ErrorOverlay.tsx` - Error display overlay

### Backend Integration
- `blocks_to_ast.py` - AST ↔ blocks transformation
- `project_zip.py` - Project file ZIP handling
- `cli.py` - Command-line interface

### Data Flow
1. **Blocks** → **AST** → **Code** (for preview/export)
2. **Code** → **AST** → **Blocks** (for import)
3. **Project Data** → **ZIP** → **File** (for save)
4. **File** → **ZIP** → **Project Data** (for load)

## Testing

### Frontend Tests
- `save.test.tsx` - Project save/load functionality
- `preview.test.tsx` - Live preview functionality
- `import.test.tsx` - Import/export round-trip

### Backend Tests
- `test_project_zip.py` - Project ZIP functionality
- `test_transform_roundtrip.py` - AST ↔ blocks transformation

## Examples

See the `examples/` directory for sample projects:

- `mapper_demo/` - Basic import/export examples
- `pkg_demo/` - Package management examples

## Development

### Running the Editor
```bash
cd visual
npm install
npm run dev
```

### Running Tests
```bash
# Frontend tests
npm run test

# Backend tests
python -m pytest tests/
```

### Building for Production
```bash
npm run build
``` 