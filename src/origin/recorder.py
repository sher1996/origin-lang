import json
import pathlib
import time
import uuid
from typing import Any, Dict, Optional

class Recorder:
    """Records execution events to a JSONL file for debugging and replay."""
    
    def __init__(self, out_path: pathlib.Path):
        """Initialize recorder with output file path."""
        self.out_path = out_path
        self.fp = out_path.open("w", encoding="utf-8")
        self.event_count = 0
    
    def record(self, node_id: str, env: Dict[str, Any]) -> None:
        """Record an execution event with node ID and environment snapshot."""
        from .snapshot import safe_snapshot
        
        # Extract variables and functions from the environment
        variables = env.get("variables", {})
        functions = env.get("functions", [])
        
        # Create v2 format event
        event = {
            "version": "v2",
            "ts": time.time(),
            "blockId": node_id,
            "locals": safe_snapshot(variables),
            "globals": safe_snapshot({"functions": functions})
        }
        
        self.fp.write(json.dumps(event) + "\n")
        self.fp.flush()  # Ensure immediate write
        self.event_count += 1
    
    def close(self) -> None:
        """Close the recorder and flush any remaining data."""
        if hasattr(self, 'fp') and not self.fp.closed:
            self.fp.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 