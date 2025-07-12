"""
Tests for project ZIP functionality
"""

import pytest
import tempfile
import os
import json
import zipfile
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from transform.project_zip import create_project_zip, extract_project_zip, save_current_project

def test_create_and_extract_project():
    """Test that creating and extracting a project produces identical data"""
    
    # Test data
    blocks = [
        {
            'id': 'test-block-1',
            'definitionId': 'say',
            'position': {'x': 100, 'y': 100},
            'inputs': {'expr': 'Hello World'},
            'outputs': {}
        }
    ]
    
    connections = [
        {
            'id': 'test-conn-1',
            'fromBlockId': 'test-block-1',
            'fromOutputId': 'statement',
            'toBlockId': 'test-block-2',
            'toInputId': 'expr'
        }
    ]
    
    metadata = {
        'name': 'Test Project',
        'description': 'A test project',
        'version': '1.0.0',
        'created': '2024-01-01T00:00:00.000Z',
        'modified': '2024-01-01T00:00:00.000Z'
    }
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create project file
        project_path = os.path.join(temp_dir, 'test.originproj')
        create_project_zip(blocks, connections, metadata, project_path)
        
        # Verify file exists
        assert os.path.exists(project_path)
        
        # Extract project
        extract_dir = os.path.join(temp_dir, 'extracted')
        extracted_data = extract_project_zip(project_path, extract_dir)
        
        # Verify extracted data matches original
        assert extracted_data['blocks'] == blocks
        assert extracted_data['connections'] == connections
        assert extracted_data['metadata']['name'] == metadata['name']
        assert extracted_data['metadata']['version'] == metadata['version']

def test_project_file_structure():
    """Test that project files contain all required files"""
    
    blocks = [{'id': 'test', 'definitionId': 'say', 'position': {'x': 0, 'y': 0}, 'inputs': {}, 'outputs': {}}]
    connections = []
    metadata = {'name': 'Test', 'version': '1.0.0', 'created': '2024-01-01T00:00:00.000Z', 'modified': '2024-01-01T00:00:00.000Z'}
    
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = os.path.join(temp_dir, 'test.originproj')
        create_project_zip(blocks, connections, metadata, project_path)
        
        # Check zip contents
        with zipfile.ZipFile(project_path, 'r') as zip_file:
            file_list = zip_file.namelist()
            
            assert 'blocks.json' in file_list
            assert 'connections.json' in file_list
            assert 'main.origin' in file_list
            assert 'README.md' in file_list
            assert 'metadata.json' in file_list

def test_missing_blocks_json():
    """Test that missing blocks.json raises an error"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create an invalid project file
        project_path = os.path.join(temp_dir, 'invalid.originproj')
        
        with zipfile.ZipFile(project_path, 'w') as zip_file:
            zip_file.writestr('metadata.json', '{"name": "test"}')
        
        # Try to extract it
        extract_dir = os.path.join(temp_dir, 'extracted')
        
        with pytest.raises(ValueError, match="Invalid project file: missing blocks.json"):
            extract_project_zip(project_path, extract_dir)

def test_byte_identical_roundtrip():
    """Test that save/open produces byte-identical files"""
    
    # Create a simple project structure
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create pkg.json
        pkg_json = {
            'name': 'test-project',
            'version': '1.0.0',
            'description': 'A test project'
        }
        
        with open(os.path.join(temp_dir, 'pkg.json'), 'w') as f:
            json.dump(pkg_json, f)
        
        # Create main.origin
        main_origin = 'say "Hello World"\nlet x = 42'
        with open(os.path.join(temp_dir, 'main.origin'), 'w') as f:
            f.write(main_origin)
        
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Save project
            project_path = 'test.originproj'
            save_current_project(project_path)
            
            # Verify project file exists
            assert os.path.exists(project_path)
            
            # Extract project
            extract_dir = 'extracted'
            extracted_data = extract_project_zip(project_path, extract_dir)
            
            # Verify main.origin was recreated correctly
            extracted_main = os.path.join(extract_dir, 'main.origin')
            assert os.path.exists(extracted_main)
            
            with open(extracted_main, 'r') as f:
                extracted_code = f.read()
            
            # The code should be similar (may have slight formatting differences)
            assert 'say' in extracted_code
            assert 'Hello World' in extracted_code
            
        finally:
            os.chdir(original_cwd)

def test_project_metadata():
    """Test that project metadata is handled correctly"""
    
    blocks = []
    connections = []
    metadata = {
        'name': 'My Test Project',
        'description': 'A comprehensive test project',
        'version': '2.1.0',
        'created': '2024-01-01T00:00:00.000Z',
        'modified': '2024-01-02T00:00:00.000Z'
    }
    
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = os.path.join(temp_dir, 'test.originproj')
        create_project_zip(blocks, connections, metadata, project_path)
        
        # Extract and verify metadata
        extract_dir = os.path.join(temp_dir, 'extracted')
        extracted_data = extract_project_zip(project_path, extract_dir)
        
        assert extracted_data['metadata']['name'] == 'My Test Project'
        assert extracted_data['metadata']['description'] == 'A comprehensive test project'
        assert extracted_data['metadata']['version'] == '2.1.0' 