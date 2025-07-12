"""
Project ZIP utilities for .originproj files
Handles saving/loading project files with blocks, connections, and metadata
"""

import zipfile
import json
import os
import pathlib
from typing import Dict, Any, List
from datetime import datetime

def create_project_zip(
    blocks: List[Dict[str, Any]],
    connections: List[Dict[str, Any]],
    metadata: Dict[str, Any],
    output_path: str
) -> None:
    """Create a .originproj file containing project data"""
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add blocks.json
        zip_file.writestr('blocks.json', json.dumps(blocks, indent=2))
        
        # Add connections.json
        zip_file.writestr('connections.json', json.dumps(connections, indent=2))
        
        # Add main.origin (generated from blocks)
        from .blocks_to_ast import blocks_to_code
        code = blocks_to_code(blocks)
        zip_file.writestr('main.origin', code)
        
        # Add README.md
        readme = generate_readme(metadata)
        zip_file.writestr('README.md', readme)
        
        # Add metadata.json
        zip_file.writestr('metadata.json', json.dumps(metadata, indent=2))

def extract_project_zip(zip_path: str, extract_dir: str) -> Dict[str, Any]:
    """Extract a .originproj file and return project data"""
    
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"Project file not found: {zip_path}")
    
    # Create extraction directory
    os.makedirs(extract_dir, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        # Extract all files
        zip_file.extractall(extract_dir)
        
        # Read project data
        blocks_path = os.path.join(extract_dir, 'blocks.json')
        connections_path = os.path.join(extract_dir, 'connections.json')
        metadata_path = os.path.join(extract_dir, 'metadata.json')
        
        if not os.path.exists(blocks_path):
            raise ValueError("Invalid project file: missing blocks.json")
        
        with open(blocks_path, 'r') as f:
            blocks = json.load(f)
        
        connections = []
        if os.path.exists(connections_path):
            with open(connections_path, 'r') as f:
                connections = json.load(f)
        
        metadata = {}
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        else:
            # Generate default metadata
            project_name = os.path.basename(zip_path).replace('.originproj', '')
            metadata = {
                'name': project_name,
                'version': '1.0.0',
                'created': datetime.now().isoformat(),
                'modified': datetime.now().isoformat()
            }
        
        return {
            'blocks': blocks,
            'connections': connections,
            'metadata': metadata
        }

def save_current_project(output_path: str) -> None:
    """Save current directory as a project file"""
    
    # Check for pkg.json
    pkg_path = 'pkg.json'
    if not os.path.exists(pkg_path):
        raise FileNotFoundError("No pkg.json found in current directory")
    
    # Read pkg.json
    with open(pkg_path, 'r') as f:
        pkg_data = json.load(f)
    
    # Find all .origin files
    origin_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.origin'):
                origin_files.append(os.path.join(root, file))
    
    # Read main.origin (or first .origin file)
    main_origin = 'main.origin'
    if not os.path.exists(main_origin) and origin_files:
        main_origin = origin_files[0]
    
    if not os.path.exists(main_origin):
        raise FileNotFoundError("No main.origin file found")
    
    with open(main_origin, 'r') as f:
        code = f.read()
    
    # Convert code to blocks
    from .blocks_to_ast import code_to_blocks
    blocks = code_to_blocks(code)
    
    # Generate metadata
    metadata = {
        'name': pkg_data.get('name', 'My Project'),
        'description': pkg_data.get('description', 'An Origin language project'),
        'version': pkg_data.get('version', '1.0.0'),
        'created': datetime.now().isoformat(),
        'modified': datetime.now().isoformat()
    }
    
    # Create project zip
    create_project_zip(blocks, [], metadata, output_path)

def generate_readme(metadata: Dict[str, Any]) -> str:
    """Generate README.md content for the project"""
    
    return f"""# {metadata.get('name', 'My Project')}

{metadata.get('description', 'An Origin language project created with the visual editor.')}

## Files

- `main.origin` - The main Origin source code
- `blocks.json` - Visual editor block definitions
- `connections.json` - Block connection data
- `metadata.json` - Project metadata

## Usage

To run this project:

```bash
origin run main.origin
```

To open in the visual editor:

```bash
origin viz open {metadata.get('name', 'project')}.originproj
```

## Project Info

- **Created**: {datetime.fromisoformat(metadata.get('created', datetime.now().isoformat())).strftime('%Y-%m-%d %H:%M:%S')}
- **Modified**: {datetime.fromisoformat(metadata.get('modified', datetime.now().isoformat())).strftime('%Y-%m-%d %H:%M:%S')}
- **Version**: {metadata.get('version', '1.0.0')}
""" 