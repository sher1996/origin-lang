import React, { useRef, useState } from 'react';
import type { BlockInstance } from '../blocks/definitions';
import { codeToAST, astToBlocks, astToCode, blocksToAST, blocksToJSON, jsonToBlocks, validateRoundTrip } from '../lib/transform';
import { autoChooseLayout } from '../lib/autoLayout';

interface ToolbarProps {
  blocks: BlockInstance[];
  onBlocksChange: (blocks: BlockInstance[]) => void;
}

const Toolbar: React.FC<ToolbarProps> = ({ blocks, onBlocksChange }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const jsonFileInputRef = useRef<HTMLInputElement>(null);
  const [status, setStatus] = useState<string>('');

  const showStatus = (message: string, isError = false) => {
    setStatus(message);
    setTimeout(() => setStatus(''), 3000);
  };

  const handleImport = () => {
    fileInputRef.current?.click();
  };

  const handleJSONImport = () => {
    jsonFileInputRef.current?.click();
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      try {
        // Parse the Origin code to AST
        const ast = codeToAST(content);
        // Convert AST to blocks
        const newBlocks = astToBlocks(ast);
        // Apply auto-layout
        const laidOutBlocks = autoChooseLayout(newBlocks);
        onBlocksChange(laidOutBlocks);
        showStatus(`Imported ${newBlocks.length} blocks from ${file.name}`);
      } catch (error) {
        console.error('Error importing file:', error);
        showStatus(`Error importing file: ${error instanceof Error ? error.message : 'Unknown error'}`, true);
      }
    };
    reader.readAsText(file);
  };

  const handleJSONFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      try {
        // Parse JSON and convert to blocks
        const newBlocks = jsonToBlocks(content);
        // Apply auto-layout
        const laidOutBlocks = autoChooseLayout(newBlocks);
        onBlocksChange(laidOutBlocks);
        showStatus(`Imported ${newBlocks.length} blocks from JSON file`);
      } catch (error) {
        console.error('Error importing JSON file:', error);
        showStatus(`Error importing JSON file: ${error instanceof Error ? error.message : 'Unknown error'}`, true);
      }
    };
    reader.readAsText(file);
  };

  const handleExport = () => {
    try {
      // Convert blocks to AST
      const ast = blocksToAST(blocks);
      // Convert AST to code
      const code = astToCode(ast);
      
      // Create and download file
      const blob = new Blob([code], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'program.origin';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showStatus('Exported program to program.origin');
    } catch (error) {
      console.error('Error exporting file:', error);
      showStatus(`Error exporting file: ${error instanceof Error ? error.message : 'Unknown error'}`, true);
    }
  };

  const handleJSONExport = () => {
    try {
      // Convert blocks to JSON
      const json = blocksToJSON(blocks);
      
      // Create and download file
      const blob = new Blob([json], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'blocks.json';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showStatus('Exported blocks to blocks.json');
    } catch (error) {
      console.error('Error exporting JSON file:', error);
      showStatus(`Error exporting JSON file: ${error instanceof Error ? error.message : 'Unknown error'}`, true);
    }
  };

  const handlePasteImport = () => {
    const code = prompt('Paste your Origin code here:');
    if (!code) return;

    try {
      const ast = codeToAST(code);
      const newBlocks = astToBlocks(ast);
      const laidOutBlocks = autoChooseLayout(newBlocks);
      onBlocksChange(laidOutBlocks);
      showStatus(`Imported ${newBlocks.length} blocks from pasted code`);
    } catch (error) {
      console.error('Error importing pasted code:', error);
      showStatus(`Error importing code: ${error instanceof Error ? error.message : 'Unknown error'}`, true);
    }
  };

  const handleValidateRoundTrip = () => {
    try {
      const ast = blocksToAST(blocks);
      const code = astToCode(ast);
      const result = validateRoundTrip(code);
      
      if (result.success) {
        showStatus('Round-trip validation passed!');
      } else {
        showStatus(`Round-trip validation failed: ${result.error}`, true);
      }
    } catch (error) {
      showStatus(`Validation error: ${error instanceof Error ? error.message : 'Unknown error'}`, true);
    }
  };

  const handleClear = () => {
    if (confirm('Are you sure you want to clear all blocks?')) {
      onBlocksChange([]);
      showStatus('Cleared all blocks');
    }
  };

  return (
    <div className="bg-white border-b border-gray-300 p-4 flex gap-2 items-center">
      <div className="flex gap-2">
        <button
          onClick={handleImport}
          className="px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors text-sm"
          title="Import .origin file"
        >
          Import
        </button>
        
        <button
          onClick={handleJSONImport}
          className="px-3 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors text-sm"
          title="Import JSON blocks file"
        >
          Import JSON
        </button>
        
        <button
          onClick={handlePasteImport}
          className="px-3 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 transition-colors text-sm"
          title="Import from pasted code"
        >
          Paste Import
        </button>
      </div>
      
      <div className="flex gap-2">
        <button
          onClick={handleExport}
          className="px-3 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 transition-colors text-sm"
          disabled={blocks.length === 0}
          title="Export to .origin file"
        >
          Export
        </button>
        
        <button
          onClick={handleJSONExport}
          className="px-3 py-2 bg-indigo-500 text-white rounded hover:bg-indigo-600 transition-colors text-sm"
          disabled={blocks.length === 0}
          title="Export to JSON blocks file"
        >
          Export JSON
        </button>
      </div>
      
      <div className="flex gap-2">
        <button
          onClick={handleValidateRoundTrip}
          className="px-3 py-2 bg-teal-500 text-white rounded hover:bg-teal-600 transition-colors text-sm"
          disabled={blocks.length === 0}
          title="Validate round-trip conversion"
        >
          Validate
        </button>
        
        <button
          onClick={handleClear}
          className="px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors text-sm"
          disabled={blocks.length === 0}
          title="Clear all blocks"
        >
          Clear
        </button>
      </div>
      
      <div className="flex-1"></div>
      
      <div className="text-sm text-gray-600">
        {blocks.length} block{blocks.length !== 1 ? 's' : ''}
      </div>
      
      {status && (
        <div className={`text-sm px-3 py-1 rounded ${status.includes('Error') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
          {status}
        </div>
      )}
      
      <input
        ref={fileInputRef}
        type="file"
        accept=".origin"
        onChange={handleFileSelect}
        style={{ display: 'none' }}
      />
      
      <input
        ref={jsonFileInputRef}
        type="file"
        accept=".json"
        onChange={handleJSONFileSelect}
        style={{ display: 'none' }}
      />
    </div>
  );
};

export default Toolbar; 