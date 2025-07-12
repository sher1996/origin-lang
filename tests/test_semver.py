import unittest
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from origin.semver import SemVer, SemVerRange, parse_version_range, find_highest_compatible_version
from origin.errors import OriginPkgError


class TestSemVer(unittest.TestCase):
    """Test semantic version parsing and comparison."""
    
    def test_parse_valid_versions(self):
        """Test parsing of valid semantic versions."""
        test_cases = [
            ("1.0.0", (1, 0, 0, None, None)),
            ("2.1.3", (2, 1, 3, None, None)),
            ("0.0.1", (0, 0, 1, None, None)),
            ("1.0.0-alpha", (1, 0, 0, "alpha", None)),
            ("1.0.0+build", (1, 0, 0, None, "build")),
            ("1.0.0-alpha+build", (1, 0, 0, "alpha", "build")),
        ]
        
        for version_str, expected in test_cases:
            with self.subTest(version=version_str):
                version = SemVer.parse(version_str)
                self.assertEqual(version.major, expected[0])
                self.assertEqual(version.minor, expected[1])
                self.assertEqual(version.patch, expected[2])
                self.assertEqual(version.prerelease, expected[3])
                self.assertEqual(version.build, expected[4])
    
    def test_parse_invalid_versions(self):
        """Test parsing of invalid semantic versions."""
        invalid_versions = [
            "1.0",  # Missing patch
            "1",  # Missing minor and patch
            "1.0.0.0",  # Too many components
            "1.0.0-",  # Empty prerelease
            "1.0.0+",  # Empty build
            "a.b.c",  # Non-numeric
            "",  # Empty
        ]
        
        for version_str in invalid_versions:
            with self.subTest(version=version_str):
                with self.assertRaises(OriginPkgError):
                    SemVer.parse(version_str)
    
    def test_version_comparison(self):
        """Test version comparison logic."""
        # Test basic ordering
        v1 = SemVer.parse("1.0.0")
        v2 = SemVer.parse("1.0.1")
        v3 = SemVer.parse("1.1.0")
        v4 = SemVer.parse("2.0.0")
        
        self.assertTrue(v1 < v2)
        self.assertTrue(v2 < v3)
        self.assertTrue(v3 < v4)
        self.assertTrue(v4 > v3)
        
        # Test prerelease ordering
        v1_alpha = SemVer.parse("1.0.0-alpha")
        v1_beta = SemVer.parse("1.0.0-beta")
        v1_final = SemVer.parse("1.0.0")
        
        self.assertTrue(v1_alpha < v1_beta)
        self.assertTrue(v1_beta < v1_final)
        self.assertTrue(v1_final > v1_alpha)
    
    def test_version_string_conversion(self):
        """Test converting versions back to strings."""
        test_cases = [
            ("1.0.0", "1.0.0"),
            ("1.0.0-alpha", "1.0.0-alpha"),
            ("1.0.0+build", "1.0.0+build"),
            ("1.0.0-alpha+build", "1.0.0-alpha+build"),
        ]
        
        for input_str, expected in test_cases:
            with self.subTest(version=input_str):
                version = SemVer.parse(input_str)
                self.assertEqual(str(version), expected)


class TestSemVerRange(unittest.TestCase):
    """Test version range parsing and matching."""
    
    def test_exact_version_ranges(self):
        """Test exact version ranges."""
        range_obj = SemVerRange("1.2.3")
        version = SemVer.parse("1.2.3")
        self.assertTrue(range_obj.satisfies(version))
        
        # Should not match other versions
        other_versions = ["1.2.2", "1.2.4", "1.3.0", "2.0.0"]
        for ver_str in other_versions:
            with self.subTest(version=ver_str):
                ver = SemVer.parse(ver_str)
                self.assertFalse(range_obj.satisfies(ver))
    
    def test_caret_ranges(self):
        """Test caret ranges (^1.2.3)."""
        # ^1.2.3 should allow 1.2.3 <= version < 2.0.0
        range_obj = SemVerRange("^1.2.3")
        
        # Should match
        matching_versions = ["1.2.3", "1.2.4", "1.3.0", "1.9.9"]
        for ver_str in matching_versions:
            with self.subTest(version=ver_str):
                ver = SemVer.parse(ver_str)
                self.assertTrue(range_obj.satisfies(ver))
        
        # Should not match
        non_matching_versions = ["1.2.2", "2.0.0", "0.9.0"]
        for ver_str in non_matching_versions:
            with self.subTest(version=ver_str):
                ver = SemVer.parse(ver_str)
                self.assertFalse(range_obj.satisfies(ver))
    
    def test_tilde_ranges(self):
        """Test tilde ranges (~1.2.3)."""
        # ~1.2.3 should allow 1.2.3 <= version < 1.3.0
        range_obj = SemVerRange("~1.2.3")
        
        # Should match
        matching_versions = ["1.2.3", "1.2.4", "1.2.9"]
        for ver_str in matching_versions:
            with self.subTest(version=ver_str):
                ver = SemVer.parse(ver_str)
                self.assertTrue(range_obj.satisfies(ver))
        
        # Should not match
        non_matching_versions = ["1.2.2", "1.3.0", "2.0.0"]
        for ver_str in non_matching_versions:
            with self.subTest(version=ver_str):
                ver = SemVer.parse(ver_str)
                self.assertFalse(range_obj.satisfies(ver))
    
    def test_comparison_operators(self):
        """Test comparison operator ranges."""
        # >=1.2.0
        range_obj = SemVerRange(">=1.2.0")
        self.assertTrue(range_obj.satisfies(SemVer.parse("1.2.0")))
        self.assertTrue(range_obj.satisfies(SemVer.parse("1.3.0")))
        self.assertFalse(range_obj.satisfies(SemVer.parse("1.1.9")))
        
        # <2.0.0
        range_obj = SemVerRange("<2.0.0")
        self.assertTrue(range_obj.satisfies(SemVer.parse("1.9.9")))
        self.assertFalse(range_obj.satisfies(SemVer.parse("2.0.0")))
    
    def test_compound_ranges(self):
        """Test compound ranges (e.g., ">=1.2 <2.0")."""
        range_obj = SemVerRange(">=1.2.0 <2.0.0")
        
        # Should match
        matching_versions = ["1.2.0", "1.5.0", "1.9.9"]
        for ver_str in matching_versions:
            with self.subTest(version=ver_str):
                ver = SemVer.parse(ver_str)
                self.assertTrue(range_obj.satisfies(ver))
        
        # Should not match
        non_matching_versions = ["1.1.9", "2.0.0", "0.9.0"]
        for ver_str in non_matching_versions:
            with self.subTest(version=ver_str):
                ver = SemVer.parse(ver_str)
                self.assertFalse(range_obj.satisfies(ver))
    
    def test_wildcard_ranges(self):
        """Test wildcard ranges (*)."""
        range_obj = SemVerRange("*")
        
        # Should match any version
        test_versions = ["0.0.1", "1.0.0", "2.3.4", "10.20.30"]
        for ver_str in test_versions:
            with self.subTest(version=ver_str):
                ver = SemVer.parse(ver_str)
                self.assertTrue(range_obj.satisfies(ver))
    
    def test_invalid_ranges(self):
        """Test invalid range specifications."""
        invalid_ranges = [
            "^invalid",
            "~1.2.3.4",
            ">=invalid",
            "1.2.3 2.0.0",  # Invalid compound
        ]
        
        for range_str in invalid_ranges:
            with self.subTest(range=range_str):
                with self.assertRaises(OriginPkgError):
                    SemVerRange(range_str)


class TestFindHighestCompatibleVersion(unittest.TestCase):
    """Test finding the highest compatible version."""
    
    def test_find_highest_compatible(self):
        """Test finding highest compatible version."""
        versions = ["1.0.0", "1.1.0", "1.2.0", "2.0.0", "2.1.0"]
        
        # Test caret range
        result = find_highest_compatible_version(versions, "^1.0.0")
        self.assertEqual(result, "1.2.0")
        
        # Test tilde range
        result = find_highest_compatible_version(versions, "~1.1.0")
        self.assertEqual(result, "1.1.0")
        
        # Test exact version
        result = find_highest_compatible_version(versions, "1.2.0")
        self.assertEqual(result, "1.2.0")
    
    def test_no_compatible_version(self):
        """Test when no version satisfies the range."""
        versions = ["1.0.0", "1.1.0", "1.2.0"]
        
        result = find_highest_compatible_version(versions, ">=2.0.0")
        self.assertIsNone(result)
        
        result = find_highest_compatible_version(versions, "^0.9.0")
        self.assertIsNone(result)
    
    def test_empty_versions_list(self):
        """Test with empty versions list."""
        result = find_highest_compatible_version([], "^1.0.0")
        self.assertIsNone(result)
    
    def test_invalid_versions_skipped(self):
        """Test that invalid versions are skipped."""
        versions = ["1.0.0", "invalid", "1.1.0", "also-invalid", "1.2.0"]
        
        result = find_highest_compatible_version(versions, "^1.0.0")
        self.assertEqual(result, "1.2.0")


if __name__ == '__main__':
    unittest.main() 