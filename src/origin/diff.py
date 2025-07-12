import json
from typing import Any, Dict, Tuple

MAX_VALUE_SIZE = 64 * 1024  # 64 KiB
TRUNCATED_MARKER = "<truncated>"

def truncate_value(value: Any, max_size: int = MAX_VALUE_SIZE) -> Any:
    """Truncate a value if it's too large for display."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        try:
            json_str = json.dumps(value)
            if len(json_str.encode('utf-8')) > max_size:
                return TRUNCATED_MARKER
            return value
        except (TypeError, ValueError):
            return TRUNCATED_MARKER
    elif isinstance(value, dict):
        result = {}
        for k, v in value.items():
            result[k] = truncate_value(v, max_size // 2)
        return result
    elif isinstance(value, list):
        result = []
        for item in value:
            result.append(truncate_value(item, max_size // 2))
        return result
    else:
        try:
            str_repr = str(value)
            if len(str_repr.encode('utf-8')) > max_size:
                return TRUNCATED_MARKER
            return str_repr
        except:
            return TRUNCATED_MARKER

def compute_diff(old_env: Dict[str, Any], new_env: Dict[str, Any]) -> Dict[str, Tuple[Any, Any]]:
    """
    Compute differences between two environment snapshots.
    
    Args:
        old_env: Previous environment snapshot
        new_env: Current environment snapshot
        
    Returns:
        Dictionary mapping keys to (old_value, new_value) tuples for changed values
    """
    changes = {}
    
    # Check for changes in variables
    old_vars = old_env.get('variables', {})
    new_vars = new_env.get('variables', {})
    
    # Find all keys that exist in either environment
    all_keys = set(old_vars.keys()) | set(new_vars.keys())
    
    for key in all_keys:
        old_value = old_vars.get(key)
        new_value = new_vars.get(key)
        
        # Check if value changed
        if old_value != new_value:
            # Truncate values for display
            old_display = truncate_value(old_value)
            new_display = truncate_value(new_value)
            changes[key] = (old_display, new_display)
    
    return changes

def format_diff(changes: Dict[str, Tuple[Any, Any]]) -> str:
    """
    Format diff changes for display.
    
    Args:
        changes: Dictionary of changes from compute_diff
        
    Returns:
        Formatted string showing changes
    """
    if not changes:
        return "No changes"
    
    lines = []
    for key, (old_val, new_val) in changes.items():
        old_str = json.dumps(old_val) if old_val is not None else "None"
        new_str = json.dumps(new_val) if new_val is not None else "None"
        lines.append(f"  {key}: {old_str} → {new_str}")
    
    return "\n".join(lines) 