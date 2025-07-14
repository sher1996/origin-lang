# Standard Library: std/http

## http_get(url: String, headers: Map = {}) -> String

Performs an HTTP GET request to the specified URL with optional headers. Returns the response body as a string.

### Usage
```ori
import std/http
let raw = http.http_get("https://api.example.com/data")
```

### Arguments
- `url` (String): The URL to fetch. Must use `http://` or `https://`.
- `headers` (Map, optional): HTTP headers to send with the request.

### Returns
- (String): The response body as a string.

### Errors
- Raises `OriginError` if:
  - Network access is not permitted (run with `--allow-net`)
  - The response status is not 2xx
  - The response is too large (default 5 MB, configurable via `ORIGIN_MAX_FETCH_BYTES`)
  - The URL scheme is not allowed (only `http` and `https`)
  - The `requests` library is not installed

### Security
- Network access is **disabled by default**. Use `origin run --allow-net ...` to enable.
- Disallowed schemes: `file://`, `ftp://`, `data:`
- Max payload: 5 MB (set `ORIGIN_MAX_FETCH_BYTES` to override)
- User-Agent: `Origin-Language/1.0` by default 