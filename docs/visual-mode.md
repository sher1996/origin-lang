# Visual Editor

The Origin Language now includes a visual editor for building programs using a drag-and-drop interface.

## Quick Start

### Development Mode

Start the visual editor development server:

```bash
# From the project root
make dev

# Or directly
cd visual && npm run dev
```

The visual editor will be available at http://localhost:5173/

### Production Build

Build the visual editor for production:

```bash
# From the project root
make build

# Or directly
cd visual && npm run build
```

### Preview Production Build

Preview the built visual editor:

```bash
# From the project root
make preview

# Or directly
cd visual && npm run preview
```

## Features

### Blocks Palette

The left sidebar contains draggable blocks:
- **Variable** - For creating variables
- **Add** - For addition operations
- **Print** - For output statements

### Canvas

The main area is a canvas where you can:
- Drop blocks from the palette
- Position blocks (basic positioning supported)
- Build your Origin program visually

### Drag and Drop

1. Click and drag a block from the palette
2. Drop it onto the canvas
3. The block will appear at the drop location

## Architecture

- **React + TypeScript** - Modern frontend framework
- **Vite** - Fast development server and build tool
- **Tailwind CSS** - Utility-first CSS framework
- **@dnd-kit/core** - Lightweight drag-and-drop library

## Development

The visual editor is located in the `/visual` directory:

```
visual/
├── src/
│   ├── components/
│   │   ├── Palette.tsx    # Block palette
│   │   └── Canvas.tsx     # Main canvas
│   ├── hooks/
│   │   └── useDrag.ts     # Drag-and-drop logic
│   ├── blocks.ts          # Block definitions
│   └── App.tsx           # Main app component
├── tailwind.config.ts     # Tailwind configuration
└── postcss.config.cjs     # PostCSS configuration
```

## Future Enhancements

- Block snapping and grid alignment
- Connection lines between blocks
- Block configuration panels
- Code generation from visual blocks
- Undo/redo functionality 