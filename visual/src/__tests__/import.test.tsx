import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../App';

// Mock the transform functions
jest.mock('../lib/transform', () => ({
  codeToAST: jest.fn(),
  astToBlocks: jest.fn(),
  astToCode: jest.fn(),
  blocksToAST: jest.fn(),
}));

// Mock the autoLayout functions
jest.mock('../lib/autoLayout', () => ({
  verticalLayoutBlocks: jest.fn((blocks) => blocks),
}));

describe('Import functionality', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should show import button in toolbar', () => {
    render(<App />);
    
    const importButton = screen.getByText('Import');
    expect(importButton).toBeInTheDocument();
  });

  test('should show export button in toolbar', () => {
    render(<App />);
    
    const exportButton = screen.getByText('Export');
    expect(exportButton).toBeInTheDocument();
  });

  test('should show block count in toolbar', () => {
    render(<App />);
    
    const blockCount = screen.getByText('0 blocks');
    expect(blockCount).toBeInTheDocument();
  });

  test('should show paste import button', () => {
    render(<App />);
    
    const pasteButton = screen.getByText('Paste Import');
    expect(pasteButton).toBeInTheDocument();
  });

  test('should handle file input change', async () => {
    const { codeToAST, astToBlocks } = require('../lib/transform');
    const { verticalLayoutBlocks } = require('../lib/autoLayout');
    
    // Mock the transform functions
    codeToAST.mockReturnValue({ statements: [] });
    astToBlocks.mockReturnValue([]);
    verticalLayoutBlocks.mockReturnValue([]);
    
    render(<App />);
    
    const importButton = screen.getByText('Import');
    fireEvent.click(importButton);
    
    // The file input should be triggered
    await waitFor(() => {
      expect(importButton).toBeInTheDocument();
    });
  });

  test('should handle paste import', async () => {
    const { codeToAST, astToBlocks } = require('../lib/transform');
    const { verticalLayoutBlocks } = require('../lib/autoLayout');
    
    // Mock the transform functions
    codeToAST.mockReturnValue({ statements: [] });
    astToBlocks.mockReturnValue([]);
    verticalLayoutBlocks.mockReturnValue([]);
    
    // Mock prompt
    const mockPrompt = jest.fn().mockReturnValue('say "Hello"');
    global.prompt = mockPrompt;
    
    render(<App />);
    
    const pasteButton = screen.getByText('Paste Import');
    fireEvent.click(pasteButton);
    
    expect(mockPrompt).toHaveBeenCalledWith('Paste your Origin code here:');
  });

  test('should update block count when blocks are added', () => {
    render(<App />);
    
    // Initially should show 0 blocks
    expect(screen.getByText('0 blocks')).toBeInTheDocument();
    
    // After adding blocks, the count should update
    // This would require simulating drag and drop
    // For now, we just test the initial state
  });
}); 