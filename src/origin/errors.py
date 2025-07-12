class OriginPkgError(Exception):
    """Custom exception for package management errors."""
    pass


class PublishError(OriginPkgError):
    """Custom exception for publishing errors."""
    pass 