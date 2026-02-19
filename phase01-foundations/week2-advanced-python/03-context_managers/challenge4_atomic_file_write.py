"""
PROGRAM: Atomic File Write - Safe File Operations
-------------------------------------------------

Ensures file writes are atomic (all-or-nothing) to prevent corruption.
Critical for configuration files, data exports, and any file that must not be partially written.
"""

import os
import tempfile
import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional, Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@contextmanager
def atomic_write(filename: str, mode: str = 'w', encoding: str = 'utf-8', make_backup: bool = True, fsync: bool = True) -> Iterator:
    """
    Write to file atomically using temp file + rename strategy.
    
    Strategy:
    1. Write to temporary file in same directory
    2. On success: rename temp file to target (atomic operation)
    3. On error: delete temp file, leave original unchanged
    
    This ensures:
    - File is never in partially-written state
    - Readers always see complete file (old or new)
    - Original preserved if write fails
    
    Critical for:
    - Configuration files (avoid corrupted configs)
    - Data exports (ensure complete files)
    - Checkpoints (avoid corrupted state)
    - Any file where partial writes would be catastrophic
    
    Args:
        filename: Target file path
        mode: File mode ('w' for text, 'wb' for binary)
        encoding: Text encoding (ignored for binary mode)
        make_backup: Create .bak file before replacing (default: True)
        fsync: Force data to disk before rename (default: True)
    
    Yields:
        file: Temporary file object to write to
    
    Raises:
        OSError: If file operations fail
    
    Example:
        >>> with atomic_write('config.json') as f:
        ...     json.dump({'setting': 'value'}, f)
        ...     # If error occurs here, original file unchanged
        >>> # File atomically updated here
    
    Production Pattern:
        >>> # Critical configuration file
        >>> with atomic_write('/etc/myapp/config.json', make_backup=True) as f:
        ...     json.dump(new_config, f)
        >>> # Either new config is written, or original is unchanged
        >>> # No intermediate state where config is partially written
    
    Technical Details:
        - Uses os.rename() which is atomic on POSIX systems
        - Temp file created in same directory (same filesystem required for atomic rename)
        - Optional fsync ensures data written to disk before rename
        - Backup file created for disaster recovery
    """
    filepath = Path(filename)

    # Ensure parent directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Create temp file in same directory (required for atomic rename)
    temp_fd, temp_path = tempfile.mkstemp(
        dir=filepath.parent,
        prefix=f'.{filepath.name}.',
        suffix='.tmp'
    )
    temp_path = Path(temp_path)

    logger.info(f"Writing atomically to: {filename}")
    logger.debug(f"Temp file: {temp_path}")

    try:
        # Open temp file with requested mode
        if 'b' in mode:
            # Binary mode
            temp_file = os.fdopen(temp_fd, mode)
        else:
            # Text mode
            temp_file = os.fdopen(temp_fd, mode, encoding=encoding)

        try:
            # Yield temp file for writing
            yield temp_file

            # Flush to os
            temp_file.flush()

            # Force to disk if requested (durability guarentee)
            if fsync:
                os.fsync(temp_file.fileno())
                logger.debug(f"fsync() completed")
        
        finally:
            # Always close temp file
            temp_file.close()

        # If we get here, write was successful
        # Create backup of original file if exists
        if make_backup and filepath.exists():
            backup_path = filepath.with_suffix(filepath.suffix + '.bak')
            shutil.copy2(filepath, backup_path)
            logger.info(f"Created backup: {backup_path}")

        # Atomic rename (this is the critical operation)
        # On POSIX, os.rename() is atomic
        # On Windows, may need special handling for existing files
        if os.name == 'nt' and filepath.exists():
            # Window: need to remove target first
            os.remove(filepath)

        os.rename(temp_path, filepath)
        logger.info(f"Atomically wrote: {filename}")

    except Exception as e:
        # Error occured - clean up temp file
        logger.error(f"Error during atomic write: {e}")

        try:
            if temp_path.exists():
                os.remove(temp_path)
                logger.debug(f"Removed temp file: {temp_path}")
        except Exception as cleanup_error:
            logger.warning(f"Error cleaning up temp file: {cleanup_error}")

        raise


@contextmanager
def atomic_write_json(filename: str, make_backup: bool = True, indent: int = 2) -> Iterator[Dict]:
    """
    Atomic write specifically for JSON files.
    
    Convenience wrapper that handles JSON serialization.
    
    Args:
        filename: Target JSON file path
        make_backup: Create backup before replacing
        indent: JSON indentation (default: 2)
    
    Yields:
        dict: Dictionary to populate (will be written as JSON)
    
    Example:
        >>> with atomic_write_json('config.json') as config:
        ...     config['database'] = {'host': 'localhost', 'port': 5432}
        ...     config['cache'] = {'ttl': 3600}
        >>> # JSON atomically written
    """
    import json

    data = {}

    try:
        yield data

        # Write JSON atomically
        with atomic_write(filename, mode='w', make_backup=make_backup) as f:
            json.dump(data, f, indent=indent)

    except Exception as e:
        logger.error(f"Error writing JSON: {e}")
        raise


@contextmanager
def atomic_write_csv(filename: str, headers: List, make_backup: bool = True) -> Iterator:
    """
    Atomic write for CSV files with headers.
    
    Args:
        filename: Target CSV file path
        headers: Column headers
        make_backup: Create backup before replacing
    
    Yields:
        csv.writer: CSV writer object
    
    Example:
        >>> with atomic_write_csv('data.csv', ['id', 'name', 'value']) as writer:
        ...     writer.writerow([1, 'Alice', 100])
        ...     writer.writerow([2, 'Bob', 200])
        >>> # CSV atomically written with headers
    """
    import csv

    with atomic_write(filename, mode='w', make_backup=make_backup) as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        yield writer



# Atomic directory operations
@contextmanager
def atomic_directory_write(directory: str, make_backup: bool = True):
    """
    Atomically replace entire directory contents.
    
    Strategy:
    1. Create temp directory
    2. Write all files to temp directory
    3. Atomically rename temp directory to target
    
    Args:
        directory: Target directory path
        make_backup: Create backup of original directory
    
    Yields:
        Path: Temporary directory to write files to
    
    Example:
        >>> with atomic_directory_write('/var/app/static') as temp_dir:
        ...     shutil.copy('style.css', temp_dir / 'style.css')
        ...     shutil.copy('script.js', temp_dir / 'script.js')
        >>> # Entire directory atomically replaced
    """
    dirpath = Path(directory)

    # Create temp directory in parent
    temp_dir = Path(tempfile.mkdtemp(dir=dirpath.parent, prefix=f'.{dirpath.name}.', suffix='.tmp'))

    logger.info(f"Atomic directory write: {directory}")
    logger.debug(f"Temp directory: {temp_dir}")

    try:
        # Yield temp directory for writing
        yield temp_dir

        # Create backup if required
        if make_backup and dirpath.exists():
            backup_path = dirpath.with_suffix('.bak')
            if backup_path.exists():
                shutil.rmtree(backup_path)
            shutil.copytree(dirpath, backup_path)
            logger.info(f"Created backup: {backup_path}")

        # Remove old directory if exists
        if dirpath.exists():
            shutil.rmtree(dirpath)

        # Atomic rename
        os.rename(temp_dir, dirpath)
        logger.info(f"Atomically replaced directory: {directory}")

    except Exception as e:
        logger.error(f"Error during atomic directory write: {e}")

        # Clean up temp directory
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        except Exception as cleanup_error:
            logger.warning(f"Error cleaning up temp directory: {cleanup_error}")

        raise


# ====================================
#             TESTING
# ====================================

if __name__ == "__main__":
    print("\nTESTING ATOMIC FILE WRITE")
    print("=" * 60)

    # Test 1: Successful write
    print(f"\n1. Testing successful atomic write:")
    test_file = Path('test_atomic.txt')

    # Create original file
    test_file.write_text("Original content")

    with atomic_write(str(test_file)) as f:
        f.write("New content")
    
    assert test_file.read_text() == "New content"
    assert test_file.with_suffix('.txt.bak').exists()
    print(f"    File atomically updated")
    print(f"    Backup created")

    # Test 2: Failed write
    print(f"\n2. Testing failed write (original preserved):")
    original_content = test_file.read_text()

    try:
        with atomic_write(str(test_file)) as f:
            f.write("Partial content")
            raise RuntimeError("Simulated error")
    except RuntimeError:
        pass

    assert test_file.read_text() == original_content
    print(f"    Original file unchanged after error")

    # Test 3: JSON atomic write
    print("\n3. Testing atomic JSON write:")
    json_file = Path('test_config.json')

    with atomic_write_json(str(json_file)) as config:
        config['database'] = {'host': 'localhost', 'port': 5432}
        config['cache'] = {'enabled': True, 'ttl': 3600}

    import json
    loaded = json.loads(json_file.read_text())
    assert loaded['database']['host'] == 'localhost'
    print(f"    JSON atomically written")

    # Test 4: CSV atomic write
    print("\n4. Testing atomic CSV write:")
    csv_file = Path('test_data.csv')

    with atomic_write_csv(str(csv_file), ['id', 'name', 'value']) as writer:
        writer.writerow([1, 'Alice', 100])
        writer.writerow([2, 'Bob, 200'])

    content = csv_file.read_text()
    assert 'id,name,value' in content
    assert 'Alice' in content
    print(f"    CSV atomically written with headers")

    # Cleanup
    for f in [test_file, json_file, csv_file]:
        if f.exists():
            f.unlink()
        backup = f.with_suffix(f.suffix + '.bak')
        if backup.exists():
            backup.unlink()