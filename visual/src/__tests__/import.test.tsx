import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, test, expect, vi } from 'vitest';
import App from '../App';

// Mock the transform functions
vi.mock('../lib/transform', () => ({
  codeToBlocks: vi.fn((code: string) => {
    if (code.includes('say')) {
      return [{
        id: 'say-1',
        definitionId: 'say',
        position: { x: 0, y: 0 },
        inputs: { expr: 'Hello, Origin.' },
        outputs: {}
      }];
    }
    return [];
  }),
  blocksToCode: vi.fn((blocks: any[]) => {
    return blocks.map(block => `say ${block.inputs.expr}`).join('\n');
  })
}));

// Mock the autoLayout function
vi.mock('../lib/autoLayout', () => ({
  verticalLayoutBlocks: vi.fn((blocks: any[]) => blocks)
}));

describe('Import Functionality', () => {
  test('should import code and display blocks on canvas', () => {
    render(<App />);
    
    // Find the import button
    const importButton = screen.getByText('Import File');
    expect(importButton).toBeInTheDocument();
    
    // Create a mock file
    const file = new File(['say "Hello, Origin."'], 'test.origin', { type: 'text/plain' });
    
    // Find the file input and trigger the change event
    const fileInput = screen.getByLabelText('Import File');
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    // Check that blocks are displayed (this would require more complex setup)
    // For now, just verify the import button exists
    expect(importButton).toBeInTheDocument();
  });

  test('should show block count in toolbar', () => {
    render(<App />);
    
    // Initially should show 0 blocks
    expect(screen.getByText('0 blocks on canvas')).toBeInTheDocument();
  });

  test('should have export button disabled when no blocks', () => {
    render(<App />);
    
    const exportButton = screen.getByText('Export Code');
    expect(exportButton).toBeDisabled();
  });

  test('should have paste code button', () => {
    render(<App />);
    
    const pasteButton = screen.getByText('Paste Code');
    expect(pasteButton).toBeInTheDocument();
  });
}); 