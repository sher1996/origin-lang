import copy
import json
from typing import Any, Dict, List, Union

MAX_SNAPSHOT_SIZE = 64 * 1024  # 64 KiB
TRUNCATED_MARKER = "<truncated>"

def safe_snapshot(env: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a safe snapshot of the environment with size capping.
    
    Args:
        env: Environment dictionary to snapshot
        
    Returns:
        Safe copy of environment with large structures truncated
    """
    def truncate_large_value(value: Any, max_size: int = MAX_SNAPSHOT_SIZE) -> Any:
        """Recursively truncate large values in the environment."""
        if isinstance(value, dict):
            result = {}
            for k, v in value.items():
                result[k] = truncate_large_value(v, max_size // 2)
            return result
        elif isinstance(value, list):
            result = []
            for item in value:
                result.append(truncate_large_value(item, max_size // 2))
            return result
        elif isinstance(value, (str, int, float, bool)) or value is None:
            # For primitive types, check if they're too large
            try:
                json_str = json.dumps(value)
                if len(json_str.encode('utf-8')) > max_size:
                    return TRUNCATED_MARKER
                return value
            except (TypeError, ValueError):
                return TRUNCATED_MARKER
        else:
            # For other types (functions, objects, etc.), try to convert to string
            try:
                str_repr = str(value)
                if len(str_repr.encode('utf-8')) > max_size:
                    return TRUNCATED_MARKER
                return str_repr
            except:
                return TRUNCATED_MARKER
    
    # Create a deep copy and then truncate
    try:
        snapshot = copy.deepcopy(env)
        return truncate_large_value(snapshot)
    except (TypeError, ValueError, RecursionError):
        # If deepcopy fails, create a shallow copy with string representations
        safe_env = {}
        for key, value in env.items():
            try:
                safe_env[key] = truncate_large_value(value)
            except:
                safe_env[key] = TRUNCATED_MARKER
        return safe_env 