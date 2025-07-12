import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lexer
import parser
from src.origin.recorder import Recorder
from src.origin.evaluator import Evaluator
from src.origin.snapshot import safe_snapshot


class TestRecorder(unittest.TestCase):
    """Test the execution recorder functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.recording_path = pathlib.Path(self.temp_dir) / "test.orirec"
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_recorder_creates_file(self):
        """Test that recorder creates the output file."""
        with Recorder(self.recording_path) as recorder:
            recorder.record("test_node", {"x": 1, "y": 2})
        
        self.assertTrue(self.recording_path.exists())
    
    def test_recorder_writes_jsonl(self):
        """Test that recorder writes valid JSONL format."""
        with Recorder(self.recording_path) as recorder:
            recorder.record("LetNode:x", {"variables": {"x": 10}, "functions": [], "node_type": "LetNode"})
            recorder.record("SayNode:hello", {"variables": {"x": 10, "y": 20}, "functions": [], "node_type": "SayNode"})
        
        with open(self.recording_path, 'r') as f:
            lines = f.readlines()
        
        self.assertEqual(len(lines), 2)
        
        # Parse first line
        event1 = json.loads(lines[0])
        self.assertEqual(event1["id"], "LetNode:x")
        self.assertEqual(event1["env"]["variables"]["x"], 10)
        self.assertEqual(event1["event_num"], 0)
        
        # Parse second line
        event2 = json.loads(lines[1])
        self.assertEqual(event2["id"], "SayNode:hello")
        self.assertEqual(event2["env"]["variables"]["x"], 10)
        self.assertEqual(event2["env"]["variables"]["y"], 20)
        self.assertEqual(event2["event_num"], 1)
    
    def test_safe_snapshot_truncates_large_values(self):
        """Test that snapshot helper truncates large values."""
        large_string = "x" * 100000  # 100KB string
        env = {"large_var": large_string, "small_var": "hello"}
        
        snapshot = safe_snapshot(env)
        
        self.assertEqual(snapshot["small_var"], "hello")
        self.assertEqual(snapshot["large_var"], "<truncated>")
    
    def test_evaluator_records_execution(self):
        """Test that evaluator records execution steps."""
        source = """
        let x = 5
        say x
        """
        
        tokens = lexer.tokenize(source)
        ast = parser.parse(tokens)
        
        with Recorder(self.recording_path) as recorder:
            evaluator = Evaluator(recorder)
            evaluator.execute(ast)
        
        # Check that events were recorded
        with open(self.recording_path, 'r') as f:
            lines = f.readlines()
        
        self.assertGreater(len(lines), 0)
        
        # Parse events
        events = [json.loads(line) for line in lines]
        
        # Should have at least 2 events (LetNode and SayNode)
        self.assertGreaterEqual(len(events), 2)
        
        # Check that variables are tracked
        let_event = next(e for e in events if "LetNode" in e["id"])
        say_event = next(e for e in events if "SayNode" in e["id"])
        
        self.assertIn("variables", let_event["env"])
        self.assertIn("variables", say_event["env"])
    
    def test_recorder_with_simple_script(self):
        """Test recorder with a simple script that has known behavior."""
        source = """
        let a = 1
        let b = 2
        say a + b
        """
        
        tokens = lexer.tokenize(source)
        ast = parser.parse(tokens)
        
        with Recorder(self.recording_path) as recorder:
            evaluator = Evaluator(recorder)
            evaluator.execute(ast)
        
        # Check events
        with open(self.recording_path, 'r') as f:
            lines = f.readlines()
        
        events = [json.loads(line) for line in lines]
        
        # Should have 3 events: 2 LetNode + 1 SayNode
        self.assertEqual(len(events), 3)
        
        # Check variable progression
        let_events = [e for e in events if "LetNode" in e["id"]]
        say_events = [e for e in events if "SayNode" in e["id"]]
        
        self.assertEqual(len(let_events), 2)
        self.assertEqual(len(say_events), 1)
        
        # Check that variables are properly tracked
        final_event = events[-1]
        self.assertIn("variables", final_event["env"])
        variables = final_event["env"]["variables"]
        self.assertEqual(variables["a"], 1)
        self.assertEqual(variables["b"], 2)


if __name__ == "__main__":
    unittest.main() 