import React from 'react';
import type { BlockInstance } from '../blocks/definitions';
import { codeToBlocks, blocksToCode } from '../lib/transform';
import { verticalLayoutBlocks } from '../lib/autoLayout';
import { ProjectExporter, type ProjectData } from '../lib/project';
import type { Connection } from '../hooks/useConnections';

interface ToolbarProps {
  blocks: BlockInstance[];
  setBlocks: (blocks: BlockInstance[]) => void;
  connections: Connection[];
  setConnections: (connections: Connection[]) => void;
}

const Toolbar: React.FC<ToolbarProps> = ({ blocks, setBlocks, connections, setConnections }) => {
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

  const handleSaveProject = async () => {
    try {
      const projectData: ProjectData = {
        blocks,
        connections,
        metadata: {
          name: 'My Project',
          description: 'An Origin language project created with the visual editor',
          version: '1.0.0',
          created: new Date().toISOString(),
          modified: new Date().toISOString()
        }
      };
      
      await ProjectExporter.saveProject(projectData, 'myproject.originproj');
    } catch (error) {
      console.error('Error saving project:', error);
      alert('Error saving project. Please try again.');
    }
  };

  const handleOpenProject = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    ProjectExporter.loadProject(file)
      .then((projectData) => {
        setBlocks(projectData.blocks);
        setConnections(projectData.connections);
      })
      .catch((error) => {
        console.error('Error loading project:', error);
        alert('Error loading project. Please check the file format.');
      });
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
        
        <button
          onClick={handleSaveProject}
          disabled={blocks.length === 0}
          className="bg-orange-500 hover:bg-orange-600 disabled:bg-gray-400 text-white px-4 py-2 rounded transition-colors"
        >
          Save Project
        </button>
        
        <label className="bg-indigo-500 hover:bg-indigo-600 text-white px-4 py-2 rounded cursor-pointer transition-colors">
          Open Project
          <input
            type="file"
            accept=".originproj"
            onChange={handleOpenProject}
            className="hidden"
          />
        </label>
      </div>
      
      <div className="text-sm text-gray-600 flex items-center">
        {blocks.length} block{blocks.length !== 1 ? 's' : ''} on canvas
      </div>
    </div>
  );
};

export default Toolbar; 