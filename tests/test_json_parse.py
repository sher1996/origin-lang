import pytest
from src.origin.builtins.json import parse
from src.origin.errors import OriginError


class TestJSONParse:
    """Test JSON parsing functionality."""
    
    def test_parse_string(self):
        """Test parsing JSON string."""
        result = parse('"hello world"')
        assert result == "hello world"
    
    def test_parse_number_integer(self):
        """Test parsing JSON integer."""
        result = parse('42')
        assert result == 42
        assert isinstance(result, int)
    
    def test_parse_number_float(self):
        """Test parsing JSON float."""
        result = parse('3.14')
        assert result == 3.14
        assert isinstance(result, float)
    
    def test_parse_boolean_true(self):
        """Test parsing JSON boolean true."""
        result = parse('true')
        assert result is True
        assert isinstance(result, bool)
    
    def test_parse_boolean_false(self):
        """Test parsing JSON boolean false."""
        result = parse('false')
        assert result is False
        assert isinstance(result, bool)
    
    def test_parse_null(self):
        """Test parsing JSON null."""
        result = parse('null')
        assert result is None
    
    def test_parse_array_empty(self):
        """Test parsing empty JSON array."""
        result = parse('[]')
        assert result == []
        assert isinstance(result, list)
    
    def test_parse_array_with_primitives(self):
        """Test parsing JSON array with primitive values."""
        result = parse('[1, "hello", true, null]')
        assert result == [1, "hello", True, None]
        assert isinstance(result, list)
    
    def test_parse_array_nested(self):
        """Test parsing nested JSON arrays."""
        result = parse('[[1, 2], [3, 4]]')
        assert result == [[1, 2], [3, 4]]
        assert isinstance(result, list)
        assert isinstance(result[0], list)
    
    def test_parse_object_empty(self):
        """Test parsing empty JSON object."""
        result = parse('{}')
        assert result == {}
        assert isinstance(result, dict)
    
    def test_parse_object_simple(self):
        """Test parsing simple JSON object."""
        result = parse('{"name": "John", "age": 30}')
        assert result == {"name": "John", "age": 30}
        assert isinstance(result, dict)
    
    def test_parse_object_nested(self):
        """Test parsing nested JSON object."""
        result = parse('{"user": {"name": "John", "settings": {"theme": "dark"}}}')
        expected = {"user": {"name": "John", "settings": {"theme": "dark"}}}
        assert result == expected
        assert isinstance(result, dict)
        assert isinstance(result["user"], dict)
        assert isinstance(result["user"]["settings"], dict)
    
    def test_parse_complex_structure(self):
        """Test parsing complex JSON structure."""
        json_str = '''
        {
            "users": [
                {"name": "Alice", "active": true, "scores": [85, 92, 78]},
                {"name": "Bob", "active": false, "scores": [90, 88]}
            ],
            "metadata": {
                "total": 2,
                "last_updated": null
            }
        }
        '''
        result = parse(json_str)
        
        assert isinstance(result, dict)
        assert "users" in result
        assert "metadata" in result
        assert isinstance(result["users"], list)
        assert len(result["users"]) == 2
        assert result["users"][0]["name"] == "Alice"
        assert result["users"][0]["active"] is True
        assert result["users"][0]["scores"] == [85, 92, 78]
        assert result["metadata"]["total"] == 2
        assert result["metadata"]["last_updated"] is None
    
    def test_parse_whitespace(self):
        """Test parsing JSON with various whitespace."""
        result = parse('  {  "key"  :  "value"  }  ')
        assert result == {"key": "value"}
    
    def test_parse_unicode_strings(self):
        """Test parsing JSON with Unicode strings."""
        result = parse('"Hello, 世界! 🌍"')
        assert result == "Hello, 世界! 🌍"
    
    def test_parse_escaped_strings(self):
        """Test parsing JSON with escaped characters."""
        result = parse('"Hello\\nWorld\\tTab\\"Quote\\"\\\\Backslash"')
        assert result == 'Hello\nWorld\tTab"Quote"\\Backslash'


class TestJSONParseErrors:
    """Test JSON parsing error handling."""
    
    def test_invalid_json_missing_quote(self):
        """Test error on missing quote."""
        with pytest.raises(OriginError, match="Invalid JSON"):
            parse('"unclosed string')
    
    def test_invalid_json_malformed_object(self):
        """Test error on malformed object."""
        with pytest.raises(OriginError, match="Invalid JSON"):
            parse('{"key": "value",}')
    
    def test_invalid_json_malformed_array(self):
        """Test error on malformed array."""
        with pytest.raises(OriginError, match="Invalid JSON"):
            parse('[1, 2, 3,]')
    
    def test_invalid_json_trailing_comma(self):
        """Test error on trailing comma."""
        with pytest.raises(OriginError, match="Invalid JSON"):
            parse('{"a": 1, "b": 2,}')
    
    def test_invalid_json_unexpected_token(self):
        """Test error on unexpected token."""
        with pytest.raises(OriginError, match="Invalid JSON"):
            parse('{"key": }')
    
    def test_invalid_json_empty_input(self):
        """Test error on empty input."""
        with pytest.raises(OriginError, match="Invalid JSON"):
            parse('')
    
    def test_invalid_json_whitespace_only(self):
        """Test error on whitespace-only input."""
        with pytest.raises(OriginError, match="Invalid JSON"):
            parse('   ')
    
    def test_invalid_json_partial_input(self):
        """Test error on partial JSON input."""
        with pytest.raises(OriginError, match="Invalid JSON"):
            parse('{"key": "value"')
    
    def test_invalid_json_extra_content(self):
        """Test error on extra content after valid JSON."""
        with pytest.raises(OriginError, match="Invalid JSON"):
            parse('{"key": "value"} extra content')
    
    def test_invalid_json_control_characters(self):
        """Test error on control characters in strings."""
        with pytest.raises(OriginError, match="Invalid JSON"):
            parse('"string with \x00 null byte"')
    
    def test_invalid_json_invalid_escape(self):
        """Test error on invalid escape sequences."""
        with pytest.raises(OriginError, match="Invalid JSON"):
            parse('"string with \\x invalid escape"') 