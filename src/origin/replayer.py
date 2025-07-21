import json
import pathlib
from typing import Any, Dict, List, Optional, Tuple

class Replayer:
    """Replays execution events from a .orirec file for debugging."""
    
    def __init__(self, events: List[Dict[str, Any]]):
        """Initialize replayer with a list of events."""
        self.events = events
        self.current_index = -1  # Start before first event
        self._validate_events()
        if len(self.events) > 1_000_000:
            print(f"Warning: Large recording with {len(self.events)} events. Consider using --slice flag in future.")
    
    @classmethod
    def from_file(cls, file_path: pathlib.Path) -> 'Replayer':
        """Load events from a .orirec file."""
        events = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                        events.append(event)
                    except json.JSONDecodeError as e:
                        raise ValueError(f"Malformed JSON at line {line_num}: {e}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Recording file not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error reading recording file: {e}")
        
        return cls(events)
    
    def _validate_events(self) -> None:
        """Validate that events have required fields."""
        for i, event in enumerate(self.events):
            if not isinstance(event, dict):
                raise ValueError(f"Event {i} is not a dictionary")
            
            # Check for v2 format
            if "version" in event and event["version"] == "v2":
                required_fields = ['version', 'ts', 'blockId', 'locals', 'globals']
                missing_fields = [field for field in required_fields if field not in event]
                if missing_fields:
                    raise ValueError(f"Event {i} missing required v2 fields: {missing_fields}")
            else:
                # Fallback to old format for backward compatibility
                required_fields = ['id', 'ts', 'env', 'event_num']
                missing_fields = [field for field in required_fields if field not in event]
                if missing_fields:
                    raise ValueError(f"Event {i} missing required fields: {missing_fields}")
    
    def next(self) -> Optional[Dict[str, Any]]:
        """Move to next event and return it."""
        if self.current_index < len(self.events) - 1:
            self.current_index += 1
            return self.events[self.current_index]
        return None
    
    def prev(self) -> Optional[Dict[str, Any]]:
        """Move to previous event and return it."""
        if self.current_index > 0:
            self.current_index -= 1
            return self.events[self.current_index]
        return None
    
    def goto(self, index: int) -> Optional[Dict[str, Any]]:
        """Jump to specific event index."""
        if 0 <= index < len(self.events):
            self.current_index = index
            return self.events[self.current_index]
        return None
    
    def current_env(self) -> Optional[Dict[str, Any]]:
        """Get environment of current event."""
        if 0 <= self.current_index < len(self.events):
            event = self.events[self.current_index]
            # Handle v2 format
            if "version" in event and event["version"] == "v2":
                return {
                    "variables": event.get("locals", {}),
                    "functions": event.get("globals", {}).get("functions", [])
                }
            else:
                # Fallback to old format
                return event.get("env", {})
        return None
    
    def current_event(self) -> Optional[Dict[str, Any]]:
        """Get current event."""
        if 0 <= self.current_index < len(self.events):
            return self.events[self.current_index]
        return None
    
    def get_info(self) -> Dict[str, Any]:
        """Get current position and total count info."""
        return {
            'current_index': self.current_index,
            'total_events': len(self.events),
            'has_next': self.current_index < len(self.events) - 1,
            'has_prev': self.current_index > 0
        }
    
    def run(self) -> None:
        """Run through all remaining events."""
        while self.next():
            pass 