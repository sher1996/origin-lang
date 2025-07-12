import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

from src.origin.replayer import Replayer
from src.origin.diff import compute_diff, format_diff, truncate_value

class TestReplayer(unittest.TestCase):
    """Test cases for the Replayer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_events = [
            {
                "id": "LetNode:n",
                "ts": 1752280195.3326955,
                "env": {"variables": {}, "functions": [], "node_type": "LetNode"},
                "event_num": 0
            },
            {
                "id": "LetNode:result", 
                "ts": 1752280195.3326955,
                "env": {"variables": {"n": 5}, "functions": [], "node_type": "LetNode"},
                "event_num": 1
            },
            {
                "id": "SayNode:result",
                "ts": 1752280195.333717,
                "env": {"variables": {"n": 5, "result": 10}, "functions": [], "node_type": "SayNode"},
                "event_num": 2
            }
        ]
    
    def test_replayer_initialization(self):
        """Test Replayer initialization with events."""
        replayer = Replayer(self.sample_events)
        self.assertEqual(len(replayer.events), 3)
        self.assertEqual(replayer.current_index, -1)
    
    def test_replayer_from_file(self):
        """Test loading events from a file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.orirec', delete=False) as f:
            for event in self.sample_events:
                f.write(json.dumps(event) + '\n')
            temp_file = f.name
        
        try:
            replayer = Replayer.from_file(pathlib.Path(temp_file))
            self.assertEqual(len(replayer.events), 3)
            self.assertEqual(replayer.current_index, -1)
        finally:
            pathlib.Path(temp_file).unlink()
    
    def test_replayer_from_file_not_found(self):
        """Test error handling for missing file."""
        with self.assertRaises(FileNotFoundError):
            Replayer.from_file(pathlib.Path("nonexistent.orirec"))
    
    def test_replayer_from_file_malformed_json(self):
        """Test error handling for malformed JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.orirec', delete=False) as f:
            f.write('{"id": "test"}\n')  # Missing required fields
            f.write('invalid json\n')
            f.write('{"id": "test2", "ts": 1, "env": {}, "event_num": 0}\n')
            temp_file = f.name
        
        try:
            with self.assertRaises(ValueError):
                Replayer.from_file(pathlib.Path(temp_file))
        finally:
            pathlib.Path(temp_file).unlink()
    
    def test_next_prev_navigation(self):
        """Test next and previous navigation."""
        replayer = Replayer(self.sample_events)
        
        # Start at -1, next should go to 0
        event = replayer.next()
        self.assertIsNotNone(event)
        self.assertEqual(replayer.current_index, 0)
        self.assertEqual(event['id'], "LetNode:n")
        
        # Next should go to 1
        event = replayer.next()
        self.assertIsNotNone(event)
        self.assertEqual(replayer.current_index, 1)
        self.assertEqual(event['id'], "LetNode:result")
        
        # Next should go to 2
        event = replayer.next()
        self.assertIsNotNone(event)
        self.assertEqual(replayer.current_index, 2)
        self.assertEqual(event['id'], "SayNode:result")
        
        # Next should return None (at end)
        event = replayer.next()
        self.assertIsNone(event)
        self.assertEqual(replayer.current_index, 2)
        
        # Prev should go back to 1
        event = replayer.prev()
        self.assertIsNotNone(event)
        self.assertEqual(replayer.current_index, 1)
        self.assertEqual(event['id'], "LetNode:result")
        
        # Prev should go back to 0
        event = replayer.prev()
        self.assertIsNotNone(event)
        self.assertEqual(replayer.current_index, 0)
        self.assertEqual(event['id'], "LetNode:n")
        
        # Prev should return None (at beginning)
        event = replayer.prev()
        self.assertIsNone(event)
        self.assertEqual(replayer.current_index, 0)

    def test_goto_navigation(self):
        """Test goto navigation."""
        replayer = Replayer(self.sample_events)
        
        # Go to specific index
        event = replayer.goto(1)
        self.assertIsNotNone(event)
        self.assertEqual(replayer.current_index, 1)
        self.assertEqual(event['id'], "LetNode:result")
        
        # Go to invalid index
        event = replayer.goto(10)
        self.assertIsNone(event)
        self.assertEqual(replayer.current_index, 1)  # Should not change
        
        # Go to valid index
        event = replayer.goto(0)
        self.assertIsNotNone(event)
        self.assertEqual(replayer.current_index, 0)
        self.assertEqual(event['id'], "LetNode:n")
    
    def test_current_env(self):
        """Test current environment retrieval."""
        replayer = Replayer(self.sample_events)
        
        # No current event
        env = replayer.current_env()
        self.assertIsNone(env)
        
        # Move to first event
        replayer.next()
        env = replayer.current_env()
        self.assertIsNotNone(env)
        self.assertEqual(env['variables'], {})
        
        # Move to second event
        replayer.next()
        env = replayer.current_env()
        self.assertIsNotNone(env)
        self.assertEqual(env['variables'], {"n": 5})
    
    def test_get_info(self):
        """Test info retrieval."""
        replayer = Replayer(self.sample_events)
        
        info = replayer.get_info()
        self.assertEqual(info['current_index'], -1)
        self.assertEqual(info['total_events'], 3)
        self.assertTrue(info['has_next'])
        self.assertFalse(info['has_prev'])
        
        # Move to middle
        replayer.goto(1)
        info = replayer.get_info()
        self.assertEqual(info['current_index'], 1)
        self.assertEqual(info['total_events'], 3)
        self.assertTrue(info['has_next'])
        self.assertTrue(info['has_prev'])
        
        # Move to end
        replayer.goto(2)
        info = replayer.get_info()
        self.assertEqual(info['current_index'], 2)
        self.assertEqual(info['total_events'], 3)
        self.assertFalse(info['has_next'])
        self.assertTrue(info['has_prev'])
    
    def test_run(self):
        """Test running through all events."""
        replayer = Replayer(self.sample_events)
        
        # Should end at last event
        replayer.run()
        self.assertEqual(replayer.current_index, 2)
    
    def test_large_recording_warning(self):
        """Test warning for large recordings."""
        large_events = [{"id": f"Node{i}", "ts": 1.0, "env": {}, "event_num": i} 
                       for i in range(1_000_001)]
        
        with patch('builtins.print') as mock_print:
            replayer = Replayer(large_events)
            mock_print.assert_called_with("Warning: Large recording with 1000001 events. Consider using --slice flag in future.")

class TestDiff(unittest.TestCase):
    """Test cases for diff functionality."""
    
    def test_compute_diff_no_changes(self):
        """Test diff computation with no changes."""
        env1 = {"variables": {"x": 1, "y": 2}}
        env2 = {"variables": {"x": 1, "y": 2}}
        
        changes = compute_diff(env1, env2)
        self.assertEqual(changes, {})
    
    def test_compute_diff_with_changes(self):
        """Test diff computation with changes."""
        env1 = {"variables": {"x": 1, "y": 2}}
        env2 = {"variables": {"x": 3, "y": 2, "z": 4}}
        
        changes = compute_diff(env1, env2)
        self.assertEqual(len(changes), 2)
        self.assertEqual(changes["x"], (1, 3))
        self.assertEqual(changes["z"], (None, 4))
    
    def test_compute_diff_new_variable(self):
        """Test diff computation with new variable."""
        env1 = {"variables": {"x": 1}}
        env2 = {"variables": {"x": 1, "y": 2}}
        
        changes = compute_diff(env1, env2)
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes["y"], (None, 2))
    
    def test_compute_diff_removed_variable(self):
        """Test diff computation with removed variable."""
        env1 = {"variables": {"x": 1, "y": 2}}
        env2 = {"variables": {"x": 1}}
        
        changes = compute_diff(env1, env2)
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes["y"], (2, None))
    
    def test_format_diff(self):
        """Test diff formatting."""
        changes = {"x": (1, 3), "y": (None, 2), "z": (4, None)}
        
        formatted = format_diff(changes)
        self.assertIn("x: 1 → 3", formatted)
        self.assertIn("y: None → 2", formatted)
        self.assertIn("z: 4 → None", formatted)
    
    def test_format_diff_no_changes(self):
        """Test diff formatting with no changes."""
        formatted = format_diff({})
        self.assertEqual(formatted, "No changes")
    
    def test_truncate_value(self):
        """Test value truncation."""
        # Small value should not be truncated
        result = truncate_value("hello")
        self.assertEqual(result, "hello")
        
        # Large string should be truncated
        large_string = "x" * 100000
        result = truncate_value(large_string)
        self.assertEqual(result, "<truncated>")
        
        # Large dict should be truncated
        large_dict = {"key": "x" * 100000}
        result = truncate_value(large_dict)
        self.assertEqual(result["key"], "<truncated>")

if __name__ == '__main__':
    unittest.main() 