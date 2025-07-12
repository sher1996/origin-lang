import React from 'react';
import type { BlockInstance } from '../blocks/definitions';
import { codeToBlocks, blocksToCode } from '../lib/transform';
import { verticalLayoutBlocks } from '../lib/autoLayout';

interface ToolbarProps {
  blocks: BlockInstance[];
  setBlocks: (blocks: BlockInstance[]) => void;
}

const Toolbar: React.FC<ToolbarProps> = ({ blocks, setBlocks }) => {
  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      try {
        const importedBlocks = codeToBlocks(content);
        const laidOutBlocks = verticalLayoutBlocks(importedBlocks);
        setBlocks(laidOutBlocks);
      } catch (error) {
        console.error('Error importing file:', error);
        alert('Error importing file. Please check the file format.');
      }
    };
    reader.readAsText(file);
  };

  const handleExport = () => {
    try {
      const code = blocksToCode(blocks);
      const blob = new Blob([code], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'program.origin';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting file:', error);
      alert('Error exporting file.');
    }
  };

  const handlePaste = () => {
    const code = prompt('Paste your Origin code here:');
    if (code) {
      try {
        const importedBlocks = codeToBlocks(code);
        const laidOutBlocks = verticalLayoutBlocks(importedBlocks);
        setBlocks(laidOutBlocks);
      } catch (error) {
        console.error('Error importing code:', error);
        alert('Error importing code. Please check the syntax.');
      }
    }
  };

  return (
    <div className="bg-white border-b border-gray-300 p-4 flex gap-4">
      <div className="flex gap-2">
        <label className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded cursor-pointer transition-colors">
          Import File
          <input
            type="file"
            accept=".origin"
            onChange={handleImport}
            className="hidden"
          />
        </label>
        
        <button
          onClick={handlePaste}
          className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded transition-colors"
        >
          Paste Code
        </button>
        
        <button
          onClick={handleExport}
          disabled={blocks.length === 0}
          className="bg-purple-500 hover:bg-purple-600 disabled:bg-gray-400 text-white px-4 py-2 rounded transition-colors"
        >
          Export Code
        </button>
      </div>
      
      <div className="text-sm text-gray-600 flex items-center">
        {blocks.length} block{blocks.length !== 1 ? 's' : ''} on canvas
      </div>
    </div>
  );
};

export default Toolbar; 