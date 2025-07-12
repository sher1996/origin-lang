import re
from typing import List, Optional, Tuple
from dataclasses import dataclass
from .errors import OriginPkgError


@dataclass
class SemVer:
    """Semantic version representation."""
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None
    
    def __post_init__(self):
        """Validate version components."""
        if not all(isinstance(x, int) and x >= 0 for x in [self.major, self.minor, self.patch]):
            raise ValueError("Version numbers must be non-negative integers")
    
    @classmethod
    def parse(cls, version_str: str) -> 'SemVer':
        """Parse a semantic version string."""
        # Basic semver pattern: major.minor.patch[-prerelease][+build]
        pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
        match = re.match(pattern, version_str)
        
        if not match:
            raise OriginPkgError(f"Invalid semantic version: {version_str}")
        
        major, minor, patch, prerelease, build = match.groups()
        
        return cls(
            major=int(major),
            minor=int(minor),
            patch=int(patch),
            prerelease=prerelease,
            build=build
        )
    
    def __str__(self) -> str:
        """Convert back to string representation."""
        result = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            result += f"-{self.prerelease}"
        if self.build:
            result += f"+{self.build}"
        return result
    
    def __eq__(self, other: 'SemVer') -> bool:
        """Compare versions for equality."""
        if not isinstance(other, SemVer):
            return False
        return (self.major, self.minor, self.patch, self.prerelease) == \
               (other.major, other.minor, other.patch, other.prerelease)
    
    def __lt__(self, other: 'SemVer') -> bool:
        """Compare versions for ordering."""
        if not isinstance(other, SemVer):
            return NotImplemented
        
        # Compare major.minor.patch
        if (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch):
            return True
        if (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch):
            return False
        
        # If versions are equal, prerelease versions are lower
        if self.prerelease is None and other.prerelease is not None:
            return False
        if self.prerelease is not None and other.prerelease is None:
            return True
        if self.prerelease is not None and other.prerelease is not None:
            return self.prerelease < other.prerelease
        
        return False
    
    def __le__(self, other: 'SemVer') -> bool:
        return self < other or self == other
    
    def __gt__(self, other: 'SemVer') -> bool:
        return not self <= other
    
    def __ge__(self, other: 'SemVer') -> bool:
        return not self < other


class SemVerRange:
    """Semantic version range parser and matcher."""
    
    def __init__(self, range_str: str):
        """Initialize with a range string."""
        self.range_str = range_str
        self.comparators = self._parse_range(range_str)
    
    def _parse_range(self, range_str: str) -> List[Tuple[str, SemVer]]:
        """Parse a version range string into comparators."""
        range_str = range_str.strip()
        
        # Handle wildcard
        if range_str == '*' or range_str == '':
            return []
        
        # Handle exact version
        if not any(op in range_str for op in ['^', '~', '>=', '<=', '>', '<', '=']):
            try:
                version = SemVer.parse(range_str)
                return [('>=', version), ('<', self._next_patch(version))]
            except OriginPkgError:
                pass
        
        # Handle caret ranges (^1.2.3, ^1.2, ^1)
        if range_str.startswith('^'):
            version_str = range_str[1:]
            version = SemVer.parse(version_str)
            return self._parse_caret_range(version)
        
        # Handle tilde ranges (~1.2.3, ~1.2)
        if range_str.startswith('~'):
            version_str = range_str[1:]
            version = SemVer.parse(version_str)
            return self._parse_tilde_range(version)
        
        # Handle comparison operators
        for op in ['>=', '<=', '>', '<', '=']:
            if range_str.startswith(op):
                version_str = range_str[len(op):]
                version = SemVer.parse(version_str)
                return [(op, version)]
        
        # Handle compound ranges (e.g., ">=1.2 <2.0")
        parts = re.split(r'\s+', range_str)
        comparators = []
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Check for operators first
            found_op = False
            for op in ['>=', '<=', '>', '<', '=']:
                if part.startswith(op):
                    version_str = part[len(op):]
                    try:
                        version = SemVer.parse(version_str)
                        comparators.append((op, version))
                        found_op = True
                        break
                    except OriginPkgError:
                        raise OriginPkgError(f"Invalid version in range: {version_str}")
            
            if not found_op:
                # Try parsing as exact version
                try:
                    version = SemVer.parse(part)
                    comparators.append(('>=', version))
                    comparators.append(('<', self._next_patch(version)))
                except OriginPkgError:
                    raise OriginPkgError(f"Invalid range specification: {part}")
        
        return comparators
    
    def _parse_caret_range(self, version: SemVer) -> List[Tuple[str, SemVer]]:
        """Parse caret range (^1.2.3)."""
        if version.major == 0:
            if version.minor == 0:
                # ^0.0.x: only patch updates
                return [('>=', version), ('<', SemVer(0, 0, version.patch + 1))]
            else:
                # ^0.x.x: only minor updates
                return [('>=', version), ('<', SemVer(0, version.minor + 1, 0))]
        else:
            # ^x.x.x: allow minor and patch updates
            return [('>=', version), ('<', SemVer(version.major + 1, 0, 0))]
    
    def _parse_tilde_range(self, version: SemVer) -> List[Tuple[str, SemVer]]:
        """Parse tilde range (~1.2.3)."""
        if version.minor is None:
            # ~1: allow patch updates
            return [('>=', version), ('<', SemVer(version.major + 1, 0, 0))]
        else:
            # ~1.2: allow patch updates
            return [('>=', version), ('<', SemVer(version.major, version.minor + 1, 0))]
    
    def _next_patch(self, version: SemVer) -> SemVer:
        """Get the next patch version."""
        return SemVer(version.major, version.minor, version.patch + 1)
    
    def satisfies(self, version: SemVer) -> bool:
        """Check if a version satisfies this range."""
        if not self.comparators:
            return True  # Wildcard matches everything
        
        for op, range_version in self.comparators:
            if op == '>=':
                if version < range_version:
                    return False
            elif op == '<=':
                if version > range_version:
                    return False
            elif op == '>':
                if version <= range_version:
                    return False
            elif op == '<':
                if version >= range_version:
                    return False
            elif op == '=':
                if version != range_version:
                    return False
        
        return True


def parse_version_range(range_str: str) -> SemVerRange:
    """Parse a version range string."""
    return SemVerRange(range_str)


def find_highest_compatible_version(versions: List[str], range_str: str) -> Optional[str]:
    """Find the highest version that satisfies the given range."""
    if not versions:
        return None
    
    try:
        range_obj = SemVerRange(range_str)
        compatible_versions = []
        
        for version_str in versions:
            try:
                version = SemVer.parse(version_str)
                if range_obj.satisfies(version):
                    compatible_versions.append(version)
            except OriginPkgError:
                continue  # Skip invalid versions
        
        if not compatible_versions:
            return None
        
        # Return the highest compatible version
        highest = max(compatible_versions)
        return str(highest)
    
    except OriginPkgError:
        return None 