# Visual Mode Import/Export

The Origin language now includes a comprehensive visual programming interface with full import/export capabilities.

## Overview

The visual mode allows users to create Origin programs using a drag-and-drop block interface, with seamless conversion between visual blocks and text-based Origin code.

## Features

### Block Registry
- **Centralized Block Management**: All block definitions are managed through a singleton `BlockRegistry`
- **Extensible**: Easy to add new block types with custom serialize/deserialize logic
- **Type Safety**: Full TypeScript support with proper type definitions

### Supported Block Types
- **Output**: `say` - Print expressions
- **Variables**: `let` - Variable assignment
- **Data**: `string`, `number` - Literal values
- **System**: `import` - Module imports
- **Control**: `repeat`, `if` - Flow control
- **Functions**: `function` - Function definitions

### Import/Export Formats
- **Origin Code (.origin)**: Text-based Origin language files
- **JSON Blocks (.json)**: Visual block data in JSON format
- **Paste Import**: Direct code pasting into the interface

## Usage

### Frontend (Visual Interface)

#### Import
1. **File Import**: Click "Import" to load `.origin` files
2. **JSON Import**: Click "Import JSON" to load block data
3. **Paste Import**: Click "Paste Import" to paste code directly

#### Export
1. **Code Export**: Click "Export" to save as `.origin` file
2. **JSON Export**: Click "Export JSON" to save block data
3. **Validation**: Click "Validate" to test round-trip conversion

### Backend (CLI)

```bash
# Import .origin file to JSON blocks
python src/cli.py viz import program.origin

# Export JSON blocks to .origin file
python src/cli.py viz export blocks.json

# Validate round-trip conversion
python src/cli.py viz validate program.origin
```

## Architecture

### Block Registry Pattern
```typescript
// Register new block type
blockRegistry.register({
  id: 'custom',
  label: 'Custom Block',
  astType: 'CustomNode',
  inputs: [...],
  outputs: [...],
  serialize: (inputs) => ({ type: 'CustomNode', ...inputs }),
  deserialize: (astNode) => ({ ...astNode }),
  color: 'blue'
});
```

### Transform Pipeline
```
Code ↔ AST ↔ Blocks ↔ JSON
```

1. **Code to AST**: Parse Origin syntax
2. **AST to Blocks**: Convert to visual representation
3. **Blocks to JSON**: Serialize for storage
4. **JSON to Blocks**: Deserialize from storage
5. **Blocks to AST**: Convert back to program structure
6. **AST to Code**: Generate Origin syntax

### Auto-Layout
Multiple layout algorithms available:
- **Vertical**: Simple stack layout
- **Grid**: Organized grid layout
- **Smart**: Grouped by block type
- **Flow**: Execution order layout
- **Compact**: Dense arrangement

## Testing

### Round-Trip Tests
Comprehensive test suite ensures:
- Code → Blocks → Code conversion preserves semantics
- All block types handle serialization correctly
- Error handling for invalid inputs
- JSON serialization/deserialization

### Test Commands
```bash
# Run visual mode tests
python tests/test_visual_roundtrip.py

# Run all tests
python -m pytest tests/
```

## Error Handling

### Frontend
- Graceful error display with status messages
- Fallback to error nodes for invalid blocks
- Input validation with type checking

### Backend
- Comprehensive exception handling
- Detailed error messages for debugging
- Graceful degradation for unknown block types

## Future Enhancements

### Planned Features
- **Block Connections**: Visual connections between blocks
- **Custom Blocks**: User-defined block types
- **Templates**: Pre-built program templates
- **Collaboration**: Real-time collaborative editing
- **Version Control**: Block-level version history

### Extensibility
- **Plugin System**: Third-party block extensions
- **Custom Themes**: Visual customization
- **Export Formats**: Additional output formats (SVG, PDF)

## API Reference

### BlockDefinition Interface
```typescript
interface BlockDefinition {
  id: string;
  label: string;
  astType: string;
  inputs: BlockInput[];
  outputs: BlockOutput[];
  serialize: (inputs: Record<string, any>) => any;
  deserialize: (astNode: any) => Record<string, any>;
  color?: string;
  icon?: string;
}
```

### Transform Functions
```typescript
// Core transform functions
blocksToAST(blocks: BlockInstance[]): ASTProgram
astToBlocks(ast: ASTProgram): BlockInstance[]
astToCode(ast: ASTProgram): string
codeToAST(code: string): ASTProgram

// JSON utilities
blocksToJSON(blocks: BlockInstance[]): string
jsonToBlocks(jsonData: string): BlockInstance[]

// Validation
validateRoundTrip(originalCode: string): ValidationResult
```

### Layout Functions
```typescript
// Layout algorithms
verticalLayoutBlocks(blocks: BlockInstance[]): BlockInstance[]
gridLayoutBlocks(blocks: BlockInstance[]): BlockInstance[]
smartLayoutBlocks(blocks: BlockInstance[]): BlockInstance[]
autoChooseLayout(blocks: BlockInstance[]): BlockInstance[]
```

## Examples

### Simple Program
```origin
say "Hello, World!"
let x = 42
say x
```

### Complex Program
```origin
import "math_utils"
let x = 10
let y = 20
if x > y:
  say "x is greater"
else:
  say "y is greater"
repeat 3 times:
  say "Loop iteration"
function add(a, b):
  let result = a + b
  say result
```

## Troubleshooting

### Common Issues
1. **Import Fails**: Check file format and syntax
2. **Export Errors**: Verify block data integrity
3. **Layout Issues**: Try different layout algorithms
4. **Validation Fails**: Check for unsupported syntax

### Debug Mode
Enable debug logging for detailed error information:
```typescript
// Frontend
console.log('Block data:', blocks);
console.log('AST:', ast);

// Backend
import logging
logging.basicConfig(level=logging.DEBUG)
``` 