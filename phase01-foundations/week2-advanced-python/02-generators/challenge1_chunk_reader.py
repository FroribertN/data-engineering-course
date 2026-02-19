"""
PROGRAM: Chunk File Reader - Batch Processing Tool
--------------------------------------------------

Reads large files in configurable chunks for batch processing.
Ideal for scenarios where processing benefits from batching (e.g., bulk datasets inserts).
"""

from typing import Iterator, List, Optional
from pathlib import Path

def read_in_chunks(
        filename: str, 
        chunk_size: int = 100, 
        encoding: str = 'utf-8', 
        skip_empty: bool = True
    ) -> Iterator[List[str]]:
    """
    Read a file in chunks (batches of lines) for efficient batch processing.

    This generator read a file line-by-line but yields groups of lines together,
    which is optimal for:
    - Bulk database operations
    - API calls with batch endpoints
    - Parallel processing of line groups

    Args:
        filename: Path to the file to read
        chunk_size: Number of lines per chunk (default: 100)
        encoding: File encoding (default: 'utf-8')
        skip_empty: Whether to skip empty lines (default: True)

    Yields:
        List[str]: Chunks of lines, each chunk containing up to chunk_size lines

    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: if chunk_size is less than 1

    Example:
        >>> for chunk in read_in_chunks('logs.txt', chunk_size=1000):
                bulk_insert_to_db(chunk) # Inserts 1000 lines at once
    
    Memory Complexity: 0(chunk_size) - Only one chunk in memory at a time
    Time Complexity: 0(n) where n is the total lines
    """
    if chunk_size < 1:
        raise ValueError(f"chunk_size must be >= 1, got {chunk_size}")
    
    filepath = Path(filename)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filename}")
    
    chunk: List[str] = []

    with open(filepath, 'r', encoding=encoding) as f:
        for line in f:
            line = line.strip()

            # Skip empty lines if configured
            if skip_empty and not line:
                continue

            chunk.append(line)

            # Yield when chunk is full
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []  # Reset for next chunk

        # Remaing lines
        if chunk:
            yield chunk


# ===========================================
#             USAGE EXAMPLE
# ===========================================

def process_large_log_file(filename: str) -> dict:
    """
    Process a large log file using chunk-based reading.

    Production pattern: Batch processing with progress tracking and error handling.
    """
    total_lines = 0
    error_lines = 0
    chunks_processed = 0

    try:
        for chunk in read_in_chunks(filename, chunk_size=1000):
            chunks_processed += 1
            total_lines += len(chunk)

            # Process chunk (e.g., bulk insert to database)
            try:
                # Simulate batch processing
                process_batch(chunk)
            except Exception as e:
                error_lines += len(chunk)
                print(f"Error processing chunk {chunks_processed}: {e}")
                continue

            # Process logging every 10 seconds
            if chunks_processed %10 == 0:
                print(f"Processed {chunks_processed} chunks ({total_lines:,} lines)")

    except Exception as e:
        print(f"Fatal error: {e}")
        raise

    return {
        'total_lines': total_lines,
        'chunks_processed': chunks_processed,
        'error_lines': error_lines,
        'success_rate': (total_lines - error_lines) / total_lines if total_lines > 0 else 0
    }


def process_batch(lines: List[str]) -> None:
    """Simulates batch processing"""
    # In production: bulk_insert_to_db(lines), bulk_api_call(lines), etc.
    pass