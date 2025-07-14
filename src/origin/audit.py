import json
import pathlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from .errors import OriginPkgError
from .semver import SemVer, SemVerRange
from .lock import Lockfile
from .registry import Registry


class Severity(Enum):
    """Audit issue severity levels."""
    INFO = "info"
    WARN = "warn"
    CRIT = "crit"


@dataclass
class AuditIssue:
    """Represents an audit issue found during dependency analysis."""
    package_name: str
    severity: Severity
    message: str
    details: Dict[str, Any]
    parent_package: Optional[str] = None

@dataclass
class DependencyNode:
    """Represents a package in the dependency tree."""
    name: str
    version: str
    parent: Optional[str] = None
    required_ranges: List[str] = field(default_factory=list)
    checksum: Optional[str] = None


class DependencyAuditor:
    """Audits dependency trees for conflicts and outdated packages."""
    
    def __init__(self, project_path: Optional[pathlib.Path] = None):
        """
        Initialize the auditor.
        
        Args:
            project_path: Path to the project directory. Defaults to current directory.
        """
        if project_path is None:
            project_path = pathlib.Path.cwd()
        
        self.project_path = project_path
        self.lockfile = Lockfile(project_path / "origin.lock")
        self.registry = Registry()
        
        # Load manifest if it exists
        self.manifest_path = project_path / "pkg.json"
        self.manifest = {}
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, 'r') as f:
                    self.manifest = json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                raise OriginPkgError(f"Failed to load pkg.json: {e}")
    
    def audit(self, level: Severity = Severity.WARN, ignore_packages: Optional[List[str]] = None) -> List[AuditIssue]:
        """
        Perform a complete audit of the dependency tree.
        
        Args:
            level: Minimum severity level to report
            ignore_packages: List of package names to ignore
            
        Returns:
            List of audit issues found
        """
        if ignore_packages is None:
            ignore_packages = []
        
        issues = []
        
        # Load dependency tree from lockfile
        dependency_tree = self._load_dependency_tree()
        
        # Check for conflicts
        conflict_issues = self._check_conflicts(dependency_tree, ignore_packages)
        issues.extend(conflict_issues)
        
        # Check for outdated packages
        outdated_issues = self._check_outdated_packages(dependency_tree, ignore_packages)
        issues.extend(outdated_issues)
        
        # Filter by severity level
        filtered_issues = [
            issue for issue in issues 
            if self._get_severity_level(issue.severity) >= self._get_severity_level(level)
        ]
        
        return filtered_issues
    
    def _load_dependency_tree(self) -> Dict[str, DependencyNode]:
        """Load the dependency tree from lockfile and manifest."""
        tree = {}
        
        # Load packages from lockfile
        lockfile_data = self.lockfile.load()
        packages = lockfile_data.get('packages', {})
        
        for name, info in packages.items():
            tree[name] = DependencyNode(
                name=name,
                version=info.get('version', '0.0.0'),
                checksum=info.get('checksum'),
                required_ranges=[]  # Will be populated from manifest
            )
        
        # Add required ranges from manifest dependencies
        if 'dependencies' in self.manifest:
            for dep_name, dep_range in self.manifest['dependencies'].items():
                if dep_name in tree:
                    tree[dep_name].required_ranges.append(dep_range)
                else:
                    # Package in manifest but not in lockfile
                    tree[dep_name] = DependencyNode(
                        name=dep_name,
                        version='0.0.0',  # Placeholder
                        required_ranges=[dep_range]
                    )
        
        return tree
    
    def _check_conflicts(self, tree: Dict[str, DependencyNode], ignore_packages: List[str]) -> List[AuditIssue]:
        """Check for version conflicts in the dependency tree."""
        issues = []
        
        # Group packages by name to find conflicts
        package_groups = {}
        for node in tree.values():
            if node.name in ignore_packages:
                continue
            
            if node.name not in package_groups:
                package_groups[node.name] = []
            package_groups[node.name].append(node)
        
        # Check each package group for conflicts
        for package_name, nodes in package_groups.items():
            if len(nodes) <= 1:
                continue
            
            # Check if all required ranges are compatible
            all_ranges = []
            for node in nodes:
                all_ranges.extend(node.required_ranges)
            
            if not all_ranges:
                continue
            
            # Check if ranges are compatible
            if not self._are_ranges_compatible(all_ranges):
                # Find the installed version
                installed_version = None
                for node in nodes:
                    if node.version != '0.0.0':  # Not a placeholder
                        installed_version = node.version
                        break
                
                ranges_str = ', '.join(all_ranges)
                message = f"Conflicting version ranges: {ranges_str}"
                
                # Determine parent packages
                parent_packages = [node.parent for node in nodes if node.parent]
                parent_info = f" (parents: {', '.join(parent_packages)})" if parent_packages else ""
                
                issues.append(AuditIssue(
                    package_name=package_name,
                    severity=Severity.CRIT,
                    message=message + parent_info,
                    details={
                        'ranges': all_ranges,
                        'installed_version': installed_version,
                        'parent_packages': parent_packages
                    }
                ))
        
        return issues
    
    def _check_outdated_packages(self, tree: Dict[str, DependencyNode], ignore_packages: List[str]) -> List[AuditIssue]:
        """Check for outdated packages by querying the registry."""
        issues = []
        
        for node in tree.values():
            if node.name in ignore_packages:
                continue
            
            if node.version == '0.0.0':  # Skip placeholders
                continue
            
            try:
                # Query registry for latest version
                latest_version = self._get_latest_version(node.name)
                if latest_version is None:
                    continue
                
                current_ver = SemVer.parse(node.version)
                latest_ver = SemVer.parse(latest_version)
                
                if current_ver < latest_ver:
                    # Determine severity based on version difference
                    severity = self._determine_outdated_severity(current_ver, latest_ver)
                    
                    message = f"Outdated: {node.version} → {latest_version}"
                    
                    issues.append(AuditIssue(
                        package_name=node.name,
                        severity=severity,
                        message=message,
                        details={
                            'current_version': node.version,
                            'latest_version': latest_version,
                            'version_diff': {
                                'major': latest_ver.major - current_ver.major,
                                'minor': latest_ver.minor - current_ver.minor,
                                'patch': latest_ver.patch - current_ver.patch
                            }
                        }
                    ))
            
            except Exception as e:
                # Skip packages that can't be checked
                continue
        
        return issues
    
    def _are_ranges_compatible(self, ranges: List[str]) -> bool:
        """Check if a list of version ranges are compatible."""
        if not ranges:
            return True
        
        try:
            # Create a combined range from all ranges
            combined_range = self._combine_ranges(ranges)
            
            # If we can create a combined range, they're compatible
            return combined_range is not None
        
        except Exception:
            return False
    
    def _combine_ranges(self, ranges: List[str]) -> Optional[SemVerRange]:
        """Combine multiple version ranges into a single range."""
        if not ranges:
            return None
        
        # For now, use a simple approach: check if all ranges overlap
        # This is a simplified implementation
        try:
            # Parse all ranges
            range_objects = [SemVerRange(r) for r in ranges]
            
            # Find common versions that satisfy all ranges
            # This is a simplified check - in practice, you'd need more sophisticated logic
            return range_objects[0]  # Simplified for now
            
        except Exception:
            return None
    
    def _get_latest_version(self, package_name: str) -> Optional[str]:
        """Get the latest non-prerelease version from the registry."""
        try:
            # Query registry for all versions
            registry = self.registry._load_registry()
            
            available_versions = []
            for reg_key in registry.keys():
                if reg_key.startswith(f"{package_name}@"):
                    version_part = reg_key[len(f"{package_name}@"):]
                    # Skip prerelease versions
                    if '-' not in version_part:
                        available_versions.append(version_part)
            
            if not available_versions:
                return None
            
            # Find the highest version
            versions = [SemVer.parse(v) for v in available_versions]
            latest = max(versions)
            return str(latest)
        
        except Exception:
            return None
    
    def _determine_outdated_severity(self, current: SemVer, latest: SemVer) -> Severity:
        """Determine severity based on version difference."""
        major_diff = latest.major - current.major
        minor_diff = latest.minor - current.minor
        patch_diff = latest.patch - current.patch
        
        if major_diff > 0:
            return Severity.CRIT
        elif minor_diff > 0:
            return Severity.WARN
        else:
            return Severity.INFO
    
    def _get_severity_level(self, severity: Severity) -> int:
        """Get numeric level for severity comparison."""
        levels = {
            Severity.INFO: 0,
            Severity.WARN: 1,
            Severity.CRIT: 2
        }
        return levels.get(severity, 0)
    
    def format_report(self, issues: List[AuditIssue], json_output: bool = False) -> str:
        """Format audit issues into a report."""
        if json_output:
            return self._format_json_report(issues)
        else:
            return self._format_text_report(issues)
    
    def _format_text_report(self, issues: List[AuditIssue]) -> str:
        """Format issues as human-readable text."""
        if not issues:
            return "✓ No issues found"
        
        lines = []
        
        # Group by severity
        by_severity = {}
        for issue in issues:
            if issue.severity not in by_severity:
                by_severity[issue.severity] = []
            by_severity[issue.severity].append(issue)
        
        # Format each issue
        for severity in [Severity.CRIT, Severity.WARN, Severity.INFO]:
            if severity not in by_severity:
                continue
            
            severity_symbol = {
                Severity.CRIT: "✖",
                Severity.WARN: "⚠",
                Severity.INFO: "ℹ"
            }[severity]
            
            for issue in by_severity[severity]:
                parent_info = f" (parent: {issue.parent_package})" if issue.parent_package else ""
                lines.append(f"{severity_symbol} {issue.package_name}{parent_info} – {issue.message}")
        
        # Summary
        crit_count = len(by_severity.get(Severity.CRIT, []))
        warn_count = len(by_severity.get(Severity.WARN, []))
        info_count = len(by_severity.get(Severity.INFO, []))
        
        total = len(issues)
        lines.append(f"\n{total} issue{'s' if total != 1 else ''} found ({crit_count} critical, {warn_count} warning{'s' if warn_count != 1 else ''})")
        
        return "\n".join(lines)
    
    def _format_json_report(self, issues: List[AuditIssue]) -> str:
        """Format issues as JSON."""
        report = {
            'issues': [
                {
                    'package': issue.package_name,
                    'severity': issue.severity.value,
                    'message': issue.message,
                    'details': issue.details,
                    'parent_package': issue.parent_package
                }
                for issue in issues
            ],
            'summary': {
                'total': len(issues),
                'critical': len([i for i in issues if i.severity == Severity.CRIT]),
                'warnings': len([i for i in issues if i.severity == Severity.WARN]),
                'info': len([i for i in issues if i.severity == Severity.INFO])
            }
        }
        
        return json.dumps(report, indent=2) 