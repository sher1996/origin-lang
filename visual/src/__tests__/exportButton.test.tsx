import { render, fireEvent, screen } from '@testing-library/react';
import Toolbar from '../components/Toolbar';
import React from 'react';
import '@testing-library/jest-dom';
import { describe, it, expect, vi } from 'vitest';
import type html2canvasType from 'html2canvas';

vi.mock('html2canvas', async () => {
  const actual: typeof html2canvasType = await vi.importActual('html2canvas');
  return {
    __esModule: true,
    default: async (node: HTMLElement, opts: any) => {
      return {
        width: 400,
        height: 300,
        toBlob: (cb: (blob: Blob) => void) => {
          cb(new Blob(['fake'], { type: 'image/png' }));
        }
      };
    }
  };
});

const blocks = [{ id: '1', definitionId: 'test', position: { x: 0, y: 0 }, inputs: {}, outputs: {} }];
const connections: any[] = [];

describe('ExportButton', () => {
  it('calls html2canvas with correct node and options', async () => {
    const canvasRef = { current: document.createElement('div') };
    render(
      <Toolbar
        blocks={blocks}
        setBlocks={() => {}}
        connections={connections}
        setConnections={() => {}}
        canvasRef={canvasRef}
      />
    );
    const btn = screen.getByTitle(/export diagram as png/i);
    fireEvent.click(btn);
    // Wait for async
    await new Promise(r => setTimeout(r, 10));
    const html2canvas = (await import('html2canvas')).default;
    expect(html2canvas).toHaveBeenCalledWith(canvasRef.current, expect.objectContaining({ scale: 2 }));
  });

  it('shows warning toast for large diagrams', async () => {
    vi.doMock('html2canvas', async () => ({
      __esModule: true,
      default: async () => ({
        width: 9000,
        height: 9000,
        toBlob: (cb: (blob: Blob) => void) => cb(new Blob(['fake'], { type: 'image/png' }))
      })
    }));
    const canvasRef = { current: document.createElement('div') };
    render(
      <Toolbar
        blocks={blocks}
        setBlocks={() => {}}
        connections={connections}
        setConnections={() => {}}
        canvasRef={canvasRef}
      />
    );
    const btn = screen.getByTitle(/export diagram as png/i);
    fireEvent.click(btn);
    await new Promise(r => setTimeout(r, 10));
    expect(screen.getByText(/too large to export/i)).toBeInTheDocument();
  });

  it('shows download-only toast if clipboard is not available', async () => {
    const origClipboard = window.ClipboardItem;
    // @ts-ignore
    window.ClipboardItem = undefined;
    const canvasRef = { current: document.createElement('div') };
    render(
      <Toolbar
        blocks={blocks}
        setBlocks={() => {}}
        connections={connections}
        setConnections={() => {}}
        canvasRef={canvasRef}
      />
    );
    const btn = screen.getByTitle(/export diagram as png/i);
    fireEvent.click(btn);
    await new Promise(r => setTimeout(r, 10));
    expect(screen.getByText(/PNG exported!/i)).toBeInTheDocument();
    window.ClipboardItem = origClipboard;
  });
}); 