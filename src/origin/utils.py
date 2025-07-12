import pathlib
import time
from typing import Optional

def generate_recording_filename(base_name: str, extension: str = ".orirec") -> str:
    """
    Generate a timestamped filename for recording files.
    
    Args:
        base_name: Base name of the file (without extension)
        extension: File extension (default: .orirec)
        
    Returns:
        Timestamped filename like "main-20241201-143022.orirec"
    """
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    return f"{base_name}-{timestamp}{extension}"

def get_recording_path(script_path: pathlib.Path, output_dir: Optional[pathlib.Path] = None) -> pathlib.Path:
    """
    Generate the full path for a recording file.
    
    Args:
        script_path: Path to the script being executed
        output_dir: Optional output directory (defaults to script directory)
        
    Returns:
        Full path for the recording file
    """
    if output_dir is None:
        output_dir = script_path.parent
    
    base_name = script_path.stem
    filename = generate_recording_filename(base_name)
    return output_dir / filename 