import JSZip from 'jszip';
import type { BlockInstance } from '../blocks/definitions';
import type { Connection } from '../hooks/useConnections';
import { blocksToCode } from './transform';

export interface ProjectData {
  blocks: BlockInstance[];
  connections: Connection[];
  metadata: {
    name: string;
    description?: string;
    version: string;
    created: string;
    modified: string;
  };
}

export class ProjectExporter {
  static async saveProject(projectData: ProjectData, filename: string = 'project.originproj'): Promise<void> {
    const zip = new JSZip();
    
    // Add blocks.json
    zip.file('blocks.json', JSON.stringify(projectData.blocks, null, 2));
    
    // Add connections.json
    zip.file('connections.json', JSON.stringify(projectData.connections, null, 2));
    
    // Add main.origin (generated from blocks)
    const code = blocksToCode(projectData.blocks);
    zip.file('main.origin', code);
    
    // Add README.md
    const readme = this.generateReadme(projectData);
    zip.file('README.md', readme);
    
    // Add metadata.json
    zip.file('metadata.json', JSON.stringify(projectData.metadata, null, 2));
    
    // Generate and download the zip file
    const blob = await zip.generateAsync({ type: 'blob' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
  
  static async loadProject(file: File): Promise<ProjectData> {
    const zip = new JSZip();
    const zipContent = await zip.loadAsync(file);
    
    // Read blocks.json
    const blocksFile = zipContent.file('blocks.json');
    if (!blocksFile) {
      throw new Error('Invalid project file: missing blocks.json');
    }
    const blocks = JSON.parse(await blocksFile.async('string'));
    
    // Read connections.json
    const connectionsFile = zipContent.file('connections.json');
    const connections = connectionsFile 
      ? JSON.parse(await connectionsFile.async('string'))
      : [];
    
    // Read metadata.json
    const metadataFile = zipContent.file('metadata.json');
    const metadata = metadataFile 
      ? JSON.parse(await metadataFile.async('string'))
      : {
          name: file.name.replace('.originproj', ''),
          version: '1.0.0',
          created: new Date().toISOString(),
          modified: new Date().toISOString()
        };
    
    return {
      blocks,
      connections,
      metadata
    };
  }
  
  private static generateReadme(projectData: ProjectData): string {
    return `# ${projectData.metadata.name}

${projectData.metadata.description || 'An Origin language project created with the visual editor.'}

## Files

- \`main.origin\` - The main Origin source code
- \`blocks.json\` - Visual editor block definitions
- \`connections.json\` - Block connection data
- \`metadata.json\` - Project metadata

## Usage

To run this project:

\`\`\`bash
origin run main.origin
\`\`\`

To open in the visual editor:

\`\`\`bash
origin viz open ${projectData.metadata.name}.originproj
\`\`\`

## Project Info

- **Created**: ${new Date(projectData.metadata.created).toLocaleDateString()}
- **Modified**: ${new Date(projectData.metadata.modified).toLocaleDateString()}
- **Version**: ${projectData.metadata.version}
`;
  }
} 