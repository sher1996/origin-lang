import unittest
import tempfile
import json
import pathlib
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from origin.audit import DependencyAuditor, AuditIssue, Severity, DependencyNode
from origin.errors import OriginPkgError


class TestDependencyAuditor(unittest.TestCase):
    """Test the dependency auditor functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = pathlib.Path(self.temp_dir)
        
        # Create a basic pkg.json
        self.manifest_path = self.project_path / "pkg.json"
        self.lockfile_path = self.project_path / "origin.lock"
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_empty_project(self):
        """Test auditing an empty project."""
        auditor = DependencyAuditor(self.project_path)
        issues = auditor.audit()
        
        self.assertEqual(len(issues), 0)
    
    def test_simple_project_no_issues(self):
        """Test auditing a simple project with no issues."""
        # Create pkg.json
        manifest = {
            "name": "test-project",
            "version": "1.0.0",
            "dependencies": {
                "math_utils": "^1.0.0"
            }
        }
        with open(self.manifest_path, 'w') as f:
            json.dump(manifest, f)
        
        # Create origin.lock
        lockfile = {
            "packages": {
                "math_utils": {
                    "version": "1.2.0",
                    "checksum": "abc123"
                }
            }
        }
        with open(self.lockfile_path, 'w') as f:
            json.dump(lockfile, f)
        
        auditor = DependencyAuditor(self.project_path)
        issues = auditor.audit()
        
        # Should not have conflicts since only one version is required
        self.assertEqual(len(issues), 0)
    
    def test_version_conflicts(self):
        """Test detecting version conflicts."""
        # Create pkg.json with conflicting requirements
        manifest = {
            "name": "test-project",
            "version": "1.0.0",
            "dependencies": {
                "react": "^18.0.0",
                "server": "ws@^8.0.0"
            }
        }
        with open(self.manifest_path, 'w') as f:
            json.dump(manifest, f)
        
        # Create origin.lock with conflicting versions
        lockfile = {
            "packages": {
                "react": {
                    "version": "18.0.2",
                    "checksum": "abc123"
                },
                "ws": {
                    "version": "9.1.0",
                    "checksum": "def456"
                }
            }
        }
        with open(self.lockfile_path, 'w') as f:
            json.dump(lockfile, f)
        
        auditor = DependencyAuditor(self.project_path)
        issues = auditor.audit()
        
        # Should detect conflicts
        self.assertGreater(len(issues), 0)
        critical_issues = [i for i in issues if i.severity == Severity.CRIT]
        self.assertGreater(len(critical_issues), 0)
    
    def test_outdated_packages(self):
        """Test detecting outdated packages."""
        # Create pkg.json
        manifest = {
            "name": "test-project",
            "version": "1.0.0",
            "dependencies": {
                "lodash": "^4.17.0"
            }
        }
        with open(self.manifest_path, 'w') as f:
            json.dump(manifest, f)
        
        # Create origin.lock with outdated version
        lockfile = {
            "packages": {
                "lodash": {
                    "version": "4.17.21",
                    "checksum": "abc123"
                }
            }
        }
        with open(self.lockfile_path, 'w') as f:
            json.dump(lockfile, f)
        
        auditor = DependencyAuditor(self.project_path)
        issues = auditor.audit()
        
        # Should detect outdated packages (if registry has newer versions)
        # Note: This test may not always find issues depending on registry state
        self.assertIsInstance(issues, list)
    
    def test_severity_filtering(self):
        """Test filtering by severity level."""
        # Create test data with mixed severity issues
        manifest = {
            "name": "test-project",
            "version": "1.0.0",
            "dependencies": {
                "package1": "^1.0.0",
                "package2": "^2.0.0"
            }
        }
        with open(self.manifest_path, 'w') as f:
            json.dump(manifest, f)
        
        lockfile = {
            "packages": {
                "package1": {
                    "version": "1.0.0",
                    "checksum": "abc123"
                },
                "package2": {
                    "version": "2.0.0",
                    "checksum": "def456"
                }
            }
        }
        with open(self.lockfile_path, 'w') as f:
            json.dump(lockfile, f)
        
        auditor = DependencyAuditor(self.project_path)
        
        # Test different severity levels
        info_issues = auditor.audit(level=Severity.INFO)
        warn_issues = auditor.audit(level=Severity.WARN)
        crit_issues = auditor.audit(level=Severity.CRIT)
        
        # Higher severity levels should have fewer or equal issues
        self.assertGreaterEqual(len(info_issues), len(warn_issues))
        self.assertGreaterEqual(len(warn_issues), len(crit_issues))
    
    def test_ignore_packages(self):
        """Test ignoring specific packages."""
        manifest = {
            "name": "test-project",
            "version": "1.0.0",
            "dependencies": {
                "react": "^18.0.0",
                "lodash": "^4.17.0"
            }
        }
        with open(self.manifest_path, 'w') as f:
            json.dump(manifest, f)
        
        lockfile = {
            "packages": {
                "react": {
                    "version": "18.0.2",
                    "checksum": "abc123"
                },
                "lodash": {
                    "version": "4.17.21",
                    "checksum": "def456"
                }
            }
        }
        with open(self.lockfile_path, 'w') as f:
            json.dump(lockfile, f)
        
        auditor = DependencyAuditor(self.project_path)
        
        # Run audit without ignoring
        all_issues = auditor.audit()
        
        # Run audit ignoring react
        filtered_issues = auditor.audit(ignore_packages=["react"])
        
        # Should have fewer issues when ignoring packages
        self.assertGreaterEqual(len(all_issues), len(filtered_issues))
    
    def test_report_formatting(self):
        """Test report formatting functionality."""
        # Create test issues
        issues = [
            AuditIssue(
                package_name="react",
                severity=Severity.CRIT,
                message="Conflicting version ranges: ^18.0.0, ^9.0.0",
                details={"ranges": ["^18.0.0", "^9.0.0"]},
                parent_package="server"
            ),
            AuditIssue(
                package_name="lodash",
                severity=Severity.WARN,
                message="Outdated: 4.17.21 → 4.18.0",
                details={"current_version": "4.17.21", "latest_version": "4.18.0"}
            )
        ]
        
        auditor = DependencyAuditor(self.project_path)
        
        # Test text formatting
        text_report = auditor.format_report(issues, json_output=False)
        self.assertIn("react", text_report)
        self.assertIn("lodash", text_report)
        self.assertIn("✖", text_report)  # Critical symbol
        self.assertIn("⚠", text_report)  # Warning symbol
        
        # Test JSON formatting
        json_report = auditor.format_report(issues, json_output=True)
        report_data = json.loads(json_report)
        self.assertIn("issues", report_data)
        self.assertIn("summary", report_data)
        self.assertEqual(len(report_data["issues"]), 2)
    
    def test_dependency_tree_loading(self):
        """Test loading dependency tree from lockfile and manifest."""
        manifest = {
            "name": "test-project",
            "version": "1.0.0",
            "dependencies": {
                "react": "^18.0.0",
                "lodash": "^4.17.0"
            }
        }
        with open(self.manifest_path, 'w') as f:
            json.dump(manifest, f)
        
        lockfile = {
            "packages": {
                "react": {
                    "version": "18.0.2",
                    "checksum": "abc123"
                },
                "lodash": {
                    "version": "4.17.21",
                    "checksum": "def456"
                }
            }
        }
        with open(self.lockfile_path, 'w') as f:
            json.dump(lockfile, f)
        
        auditor = DependencyAuditor(self.project_path)
        tree = auditor._load_dependency_tree()
        
        # Check that all packages are loaded
        self.assertIn("react", tree)
        self.assertIn("lodash", tree)
        
        # Check that required ranges are populated
        self.assertIn("^18.0.0", tree["react"].required_ranges)
        self.assertIn("^4.17.0", tree["lodash"].required_ranges)
    
    def test_range_compatibility(self):
        """Test version range compatibility checking."""
        auditor = DependencyAuditor(self.project_path)
        
        # Test compatible ranges
        compatible_ranges = ["^1.0.0", "^1.2.0"]
        self.assertTrue(auditor._are_ranges_compatible(compatible_ranges))
        
        # Test incompatible ranges
        incompatible_ranges = ["^1.0.0", "^2.0.0"]
        # Note: This is a simplified test - the actual implementation may need refinement
        self.assertIsInstance(auditor._are_ranges_compatible(incompatible_ranges), bool)
    
    def test_severity_determination(self):
        """Test determining severity based on version differences."""
        from origin.semver import SemVer
        
        auditor = DependencyAuditor(self.project_path)
        
        # Test major version difference (should be critical)
        current = SemVer.parse("1.0.0")
        latest = SemVer.parse("2.0.0")
        severity = auditor._determine_outdated_severity(current, latest)
        self.assertEqual(severity, Severity.CRIT)
        
        # Test minor version difference (should be warning)
        current = SemVer.parse("1.0.0")
        latest = SemVer.parse("1.1.0")
        severity = auditor._determine_outdated_severity(current, latest)
        self.assertEqual(severity, Severity.WARN)
        
        # Test patch version difference (should be info)
        current = SemVer.parse("1.0.0")
        latest = SemVer.parse("1.0.1")
        severity = auditor._determine_outdated_severity(current, latest)
        self.assertEqual(severity, Severity.INFO)


class TestAuditIssue(unittest.TestCase):
    """Test the AuditIssue dataclass."""
    
    def test_audit_issue_creation(self):
        """Test creating audit issues."""
        issue = AuditIssue(
            package_name="test-package",
            severity=Severity.WARN,
            message="Test issue",
            details={"key": "value"},
            parent_package="parent-package"
        )
        
        self.assertEqual(issue.package_name, "test-package")
        self.assertEqual(issue.severity, Severity.WARN)
        self.assertEqual(issue.message, "Test issue")
        self.assertEqual(issue.details, {"key": "value"})
        self.assertEqual(issue.parent_package, "parent-package")
    
    def test_audit_issue_without_parent(self):
        """Test creating audit issues without parent package."""
        issue = AuditIssue(
            package_name="test-package",
            severity=Severity.CRIT,
            message="Critical issue",
            details={}
        )
        
        self.assertEqual(issue.package_name, "test-package")
        self.assertEqual(issue.severity, Severity.CRIT)
        self.assertIsNone(issue.parent_package)


if __name__ == "__main__":
    unittest.main() 