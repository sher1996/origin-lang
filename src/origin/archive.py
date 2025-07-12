import tarfile
import zipfile
import pathlib
from .errors import OriginPkgError


def extract_archive(archive_path: pathlib.Path, extract_to: pathlib.Path) -> None:
    """
    Extract an archive file (.tar.gz or .zip) to the specified directory.
    
    Args:
        archive_path: Path to the archive file
        extract_to: Directory to extract to
        
    Raises:
        OriginPkgError: On unsupported archive types or extraction errors
    """
    if not archive_path.exists():
        raise OriginPkgError(f"Archive file not found: {archive_path}")
    
    # Ensure extraction directory exists
    extract_to.mkdir(parents=True, exist_ok=True)
    
    try:
        if archive_path.suffix == '.gz' and archive_path.stem.endswith('.tar'):
            # Handle .tar.gz files
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(extract_to)
                
        elif archive_path.suffix == '.zip':
            # Handle .zip files
            with zipfile.ZipFile(archive_path, 'r') as zip_file:
                zip_file.extractall(extract_to)
                
        elif archive_path.suffix == '.tar':
            # Handle .tar files
            with tarfile.open(archive_path, 'r') as tar:
                tar.extractall(extract_to)
                
        else:
            raise OriginPkgError(
                f"Unsupported archive format: {archive_path.suffix}. "
                "Supported formats: .tar.gz, .tar, .zip"
            )
            
    except (tarfile.TarError, zipfile.BadZipFile) as e:
        raise OriginPkgError(f"Failed to extract archive {archive_path}: {e}")
    except Exception as e:
        raise OriginPkgError(f"Unexpected error extracting {archive_path}: {e}")


def is_archive_file(file_path: pathlib.Path) -> bool:
    """
    Check if a file is a supported archive format.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if the file is a supported archive format
    """
    supported_suffixes = {'.tar.gz', '.tar', '.zip'}
    return file_path.suffix in supported_suffixes or (
        file_path.suffix == '.gz' and file_path.stem.endswith('.tar')
    ) 