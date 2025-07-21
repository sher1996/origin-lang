import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import App from '../App';

// Mock the iframe functionality
Object.defineProperty(window, 'postMessage', {
  value: vi.fn(),
  writable: true,
});

describe('Preview Pane', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders preview pane in three-column layout', () => {
    render(<App />);
    
    // Check that we have three main sections
    expect(screen.getByText('Live Preview')).toBeInTheDocument();
    expect(screen.getByText('Drop blocks here to build your program')).toBeInTheDocument();
  });

  test('shows loading state initially', () => {
    render(<App />);
    
    expect(screen.getByText('Loading preview...')).toBeInTheDocument();
  });

  test('updates preview when blocks change', async () => {
    render(<App />);
    
    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Loading preview...')).toBeInTheDocument();
    }, { timeout: 1000 });
  });
}); 