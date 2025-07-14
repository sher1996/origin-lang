# Standard Library: json.parse

## json.parse(str: String) -> Map | Array | String | Number | Bool | Null

Parses a JSON string and returns the corresponding Origin data structure.

### Usage
```ori
import json
let obj = json.parse('{"foo": 42, "bar": [1, 2, 3]}')
```

### Arguments
- `str` (String): The JSON string to parse.

### Returns
- (Map | Array | String | Number | Bool | Null): The parsed JSON value.

### Supported Types
- JSON objects → Map (dict)
- JSON arrays → Array (list)
- JSON string → String
- JSON number → Number (int/float)
- JSON boolean → Bool
- JSON null → Null

### Errors
- Raises `OriginError` if the input is not valid JSON.

### Security
- Only parses data in memory. No file/network access. 