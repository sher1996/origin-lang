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
        
        snapshot = safe_snapshot(env)
        event = {
            "id": node_id,
            "ts": time.time(),
            "env": snapshot,
            "event_num": self.event_count
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