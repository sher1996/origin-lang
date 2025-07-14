import json
from typing import Any, Union, Dict, List
from ..errors import OriginError


def parse(json_str: str) -> Union[Dict[str, Any], List[Any], str, int, float, bool, None]:
    """
    Parse a JSON string into Origin data structures.
    
    Args:
        json_str: The JSON string to parse
        
    Returns:
        Parsed data as Origin-compatible types:
        - Objects become Maps (dict)
        - Arrays become Lists
        - Strings, numbers, booleans, null remain as-is
        
    Raises:
        OriginError: If the JSON is invalid
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise OriginError(f"Invalid JSON: {e}")
    except Exception as e:
        raise OriginError(f"JSON parsing error: {e}") 