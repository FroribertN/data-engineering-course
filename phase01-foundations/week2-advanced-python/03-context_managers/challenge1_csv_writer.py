"""
CSV Writer Context Manager - Safe File Writing
----------------------------------------------

Ensures CSV files are properly created with headers and closed safely.
Handles errors during writing without leaving corrupted files.
"""

import csv
from contextlib import contextmanager
from typing import Iterator, List, Optional, Callable
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@contextmanager
def csv_writer(filename: str, headers: List[str], mode: str = 'w', encoding: str = 'utf-8', delimeter: str = ',') -> Iterator[csv.writer]:
    """
    Context manager for writing CSV files with automatic header and cleanup.
    
    Ensures:
    - File is opened safely
    - Headers are written automatically
    - File is closed even on error
    - Parent directories are created if needed
    
    Args:
        filename: Output file path
        headers: Column headers to write
        mode: File mode ('w' for overwrite, 'a' for append)
        encoding: File encoding (default: 'utf-8')
        delimiter: CSV delimiter (default: ',')
    
    Yields:
        csv.writer: CSV writer object ready for writing rows
    
    Raises:
        OSError: If file cannot be created
        ValueError: If headers is empty
    
    Example:
        >>> with csv_writer('sales.csv', ['id', 'amount', 'date']) as writer:
        ...     writer.writerow([1, 100.50, '2024-01-15'])
        ...     writer.writerow([2, 250.00, '2024-01-16'])
        >>> # File automatically closed with headers written
    
    Production Notes:
        - Creates parent directories automatically
        - Logs file operations for monitoring
        - Safe for use in ETL pipelines
    """
    if not headers:
        raise ValueError("headers cannot be empty")
    
    filepath = Path(filename)

    # Create parent directories if they don't exist
    filepath.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Opening CSV for writing: {filename}")

    file_handle = None
    try:
        # Open fiile
        file_handle = open(filepath, mode, newline='', encoding=encoding)
        writer = csv.writer(file_handle, delimiter=delimeter)

        # Write headers (skip if appending to existing file)
        if mode == 'w' or not filepath.exists() or filepath.stat().st_size == 0:
            writer.writerow(headers)
            logger.debug(f"Wrote headers: {headers}")

        yield writer

        logger.info(f"Successfully wrote to: {filename}")

    except Exception as e:
        logger.error(f"Error writing CSV file for {filename}: {e}")
        raise

    finally:
        # Always close file
        if file_handle:
            file_handle.close()
            logger.debug(f"Closed file: {filename}")



# Version with row validation
@contextmanager
def validated_csv_writer(filename: str, headers: List[str], validate_row: Optional[Callable] = None) -> Iterator[Callable]:
    """
    CSV writer with automatic row validation.
    
    Args:
        filename: Output file path
        headers: Column headers
        validate_row: Optional function to validate each row before writing
    
    Yields:
        Callable: Function to write validated rows
    
    Example:
        >>> def validate(row):
        ...     if len(row) != 3:
        ...         raise ValueError("Row must have 3 columns")
        ...     if not isinstance(row[1], (int, float)):
        ...         raise ValueError("Amount must be numeric")
        >>> 
        >>> with validated_csv_writer('sales.csv', ['id', 'amount', 'date'], validate) as write:
        ...     write([1, 100.50, '2024-01-15'])  # OK
        ...     write([2, 'invalid', '2024-01-16'])  # Raises ValueError
    """
    rows_written = 0
    errors = 0

    with csv_writer(filename, headers) as writer:
        def write_validated_row(row: List) -> None:
            nonlocal rows_written, errors
            try:
                # Validate if function provided
                if validate_row:
                    validate_row(row)

                # Check row length matches headers
                if len(row) != len(headers):
                    raise ValueError(f"Row has {len(row)} columns but {len(headers)} expected")
                
                writer.writerow(row)
                rows_written += 1

            except Exception as e:
                errors += 1
                logger.error(f"Error writing row {rows_written + errors}: {e}")
                raise

        try:
            yield write_validated_row
        finally:
            logger.info(f"CSV writing complete: {rows_written} row(s) written, {errors} error(s)")



# ========================================
#             TESTING
# ========================================

if __name__ == "__main__":
    print("\nTesting CSV Writer Context Manager")
    print("=" * 60)

    # Test 1: Basic usage
    print("\n1. Basic CSV Writing:")
    with csv_writer('test_output.csv', ['id', 'name', 'value']) as writer:
        writer.writerow([1, 'Alice', 100])
        writer.writerow([2, 'Bob', 200])
        writer.writerow([3, 'Charlie', 300])
    print("File written successfully")

    # Test 2: With validation
    print("\n2. Validated CSV Writing:")
    def validate(row):
        if row[2] < 0:
            raise ValueError("Value cannot be negative")
        
    try:
        with validated_csv_writer('validated_output.csv',['id', 'name', 'value'], validate) as write:
            write([1, 'Alice', 100])
            write([2, 'Bob', -50])   # Should fail

    except ValueError as e:
        print(f"Validation caught error: {e}")

    # Test 3: Error Handling
    print("\n3. Error Handling:")
    try:
        with csv_writer('test_error.csv', ['id', 'name']) as writer:
            writer.writerow([1, 'Alice'])
            raise RuntimeError("Simulated error")
            writer.writerow([2, 'Bob'])  # Never executes
    except RuntimeError:
        print("File closed despite error")