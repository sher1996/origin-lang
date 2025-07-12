import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock iframe functionality
Object.defineProperty(window, 'postMessage', {
  value: vi.fn(),
  writable: true,
});

// Mock URL.createObjectURL
Object.defineProperty(URL, 'createObjectURL', {
  value: vi.fn(() => 'blob:mock-url'),
  writable: true,
});

Object.defineProperty(URL, 'revokeObjectURL', {
  value: vi.fn(),
  writable: true,
}); 