"""
PROGRAM: Stream Deduplication - Memory-Efficient Duplicate Removal
------------------------------------------------------------------

Remove duplicates from data streams while maintaining order and minimizing memory usage.
Critical for ETL pipelines processing logs, events, and user activity data.
"""

from typing import Iterator, TypeVar, Callable, Optional, Set, Any, Hashable, Dict, List
from collections import OrderedDict
import hashlib
import json

T = TypeVar('T')


def deduplicate(stream: Iterator[T], key: Optional[Callable[[T], Hashable]] = None) -> Iterator[T]:
    """
    Remove duplicates from a stream while preserving order.

    Uses a set to track seen items. Memory usage is 0(unique_items), which is optimal for exact deduplication.

    This is critical for:
    - Event stream processing (remove duplicate events)
    - Log aggregation (deduplicate log entries)
    - CDC (Change Data Capture) pipelines (handle duplicate updates)

    Args:
        stream: Input data stream
        key: Optional function to extract comparison value.
        If None, compares items directly.

    Yields:
        T: Items from stream with duplicates removed

    Time Complexity: 0(n) where n = total items
    Space Complexity: 0(unique_items)

    Example:
        >>> data = [1, 2, 2, 3, 1, 4, 3, 5]
        >>> list(deduplicate(iter(data)))
        [1, 2, 3, 4, 5]
        
        >>> records = [
        ...     {'id': 1, 'name': 'Alice'},
        ...     {'id': 2, 'name': 'Bob'},
        ...     {'id': 1, 'name': 'Alice Updated'},  # Duplicate ID
        ... ]
        >>> list(deduplicate(iter(records), key=lambda x: x['id']))
        [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
    
    Production Notes:
        - For unhashable types (dicts, lists), provide a key function
        - Memory scales with number of UNIQUE items, not total items
        - If unique items >> available RAM, use approximate deduplication
    """
    seen: Set[Hashable] = set()

    for item in stream:
        # Extract comparison key
        if key is None:
            comparison_value = item
        else:
            comparison_value = key(item)

        # Check if we've seen this before
        if comparison_value not in seen:
            seen.add(comparison_value)
            yield item


def deduplicate_with_latest(stream: Iterator[T], key: Callable[[T], Hashable]) -> Iterator[T]:
    """
    Keep only LATEST occurence for each unique key.

    Useful for CDC (Change Data Capture) where you want to the most recent state of each record.

    WARNING: This requires materializing all items (not streaming).
    Only use when dataset fits in memory.
    
    Args:
        stream: Input data stream
        key: Function to extract unique identifier
    
    Yields:
        T: Latest version of each unique item
    
    Example:
        >>> updates = [
        ...     {'id': 1, 'value': 'v1', 'timestamp': 1},
        ...     {'id': 2, 'value': 'v1', 'timestamp': 1},
        ...     {'id': 1, 'value': 'v2', 'timestamp': 2},  # Update
        ... ]
        >>> list(deduplicate_with_latest(iter(updates), key=lambda x: x['id']))
        [{'id': 1, 'value': 'v2', 'timestamp': 2}, {'id': 2, 'value': 'v1', ...}]
    """
    # Use OrderedDict to maintain insertion order
    seen: OrderedDict[Hashable, T] = OrderedDict()

    for item in stream:
        comparison_value = key(item)
        # Overwrite with latest
        seen[comparison_value] = item
    
    # Yield items in order they were FIRST seen
    yield from seen.values()


def approximate_deduplicate(stream: Iterator[T], key: Optional[Callable[[T], Hashable]] = None, max_memory_mb: int = 100) -> Iterator[T]:
    """
    Approximate deduplication with bounded memory using bloom filter approach.
    
    Uses a simple hash-based approach with fixed-size bit array.
    May have false positives (think item was seen when it wasn't) but
    NEVER false negatives (won't miss actual duplicates).
    
    Use when:
    - Stream has more unique items than fit in RAM
    - Some duplicate retention is acceptable
    - Need guaranteed memory bound
    
    Args:
        stream: Input data stream
        key: Optional function to extract comparison value
        max_memory_mb: Maximum memory to use (in MB)
    
    Yields:
        T: Items from stream with most duplicates removed
    
    Example:
        >>> # Process billion-record stream with 100MB memory limit
        >>> huge_stream = (record for record in fetch_records())
        >>> deduped = approximate_deduplicate(
        ...     huge_stream,
        ...     key=lambda x: x['user_id'],
        ...     max_memory_mb=100
        ... )
    """
    # Calculate bit array size based on memory limit
    bits_available = max_memory_mb * 1024 * 1024 * 8
    bit_array_size = min(bits_available, 100_000_000) # Cap of 100M bits
    bit_array = bytearray(bit_array_size // 8)

    def set_bit(value: Hashable) -> None:
        """Set bit in array based on hash of value"""
        hash_value = hash(value) % bit_array_size
        byte_index = hash_value // 8
        bit_index = hash_value % 8
        bit_array[byte_index] |= (1 << bit_index)

    def check_bit(value: Hashable) -> bool:
        """Check if bit is set for value"""
        hash_value = hash(value) % bit_array_size
        byte_index = hash_value // 8
        bit_index = hash_value % 8
        return bool(bit_array[byte_index] & (1 << bit_index))
    
    for item in stream:
        # Extract comparison key
        comparison_value = key(item) if key else item

        # Check if we've seen this before
        if not check_bit(comparison_value):
            set_bit(comparison_value)
            yield item
        else:
            continue


def deduplicate_sorted_stream(stream: Iterator[T]) -> Iterator[T]:
    """
    Deduplicate a SORTED stream with O(1) memory.
    
    If your stream is already sorted (or can be sorted efficiently),
    this is the most memory-efficient approach.
    
    Args:
        stream: SORTED input stream
    
    Yields:
        T: Unique items
    
    Example:
        >>> sorted_data = [1, 1, 2, 2, 2, 3, 4, 4, 5]
        >>> list(deduplicate_sorted_stream(iter(sorted_data)))
        [1, 2, 3, 4, 5]
    
    Time Complexity: O(n)
    Space Complexity: O(1) - Only stores last item!
    """
    previous = object()  # Sentinel value

    for item in stream:
        if item != previous:
            yield item
            previous = item


# ========================================================================
#        PRODUCTION PATTERN: CDC (Change Data Capture) Deduplication
# ========================================================================

class CDCDeduplicator:
    """
    Deduplicate CDC events while handling updates and deletes correctly.

    Production pattern for database replication and event sourcing.
    """

    def __init__(self, key_field: str = 'id'):
        """
        Initialize CDC deduplicator.
        
        Args:
            key_field: Field name containing unique identifier
        """
        self.key_field = key_field
        self.seen_keys: Set[Any] = set()
        self.latest_state: OrderedDict[Any, Dict] = OrderedDict()

    def process_stream(self, events: Iterator[Dict]) -> Iterator[Dict]:
        """
        Process CDC event stream.
        
        Handles:
        - INSERT: First occurrence
        - UPDATE: Latest value wins
        - DELETE: Remove from state
        
        Args:
            events: Stream of CDC events with 'operation' and data
        
        Yields:
            dict: Final state of each record
        
        Example:
            >>> events = [
            ...     {'operation': 'INSERT', 'id': 1, 'value': 'v1'},
            ...     {'operation': 'UPDATE', 'id': 1, 'value': 'v2'},
            ...     {'operation': 'DELETE', 'id': 1},
            ...     {'operation': 'INSERT', 'id': 2, 'value': 'v1'},
            ... ]
            >>> processor = CDCDeduplicator()
            >>> list(processor.process_stream(iter(events)))
            [{'operation': 'INSERT', 'id': 2, 'value': 'v1'}]
        """
        for event in events:
            key = event[self.key_field]
            operation = event.get('operation', 'INSERT')

            if operation == 'DELETE':
                # Remove from state if exists
                self.latest_state.pop(key, None)
            else:
                # INSERT or UPDATE - store latest
                self.latest_state[key] = event

        # Yield final state
        yield from self.latest_state.values()


# ====================================================
#    PRODUCTION PATTERN: Distributed Deduplication
# ====================================================

def distributed_deduplicate(stream: Iterator[T], key: Callable[[T], Hashable], num_partitions: int = 10) -> Iterator[T]:
    """
    Deduplicate using partitioning strategy for distributed processing.
    
    Strategy:
    1. Hash each item's key to determine partition
    2. Group items by partition
    3. Deduplicate within each partition
    4. Merge results
    
    This allows parallel processing of partitions on different machines.
    
    Args:
        stream: Input data stream
        key: Function to extract unique identifier
        num_partitions: Number of partitions (workers)
    
    Yields:
        T: Deduplicated items
    
    Note:
        In production, each partition would be processed by a different worker.
        This example shows the algorithm; actual distributed implementation
        would use Spark, Flink, or similar framework.
    """
    # Partition items by hash of key
    partitions: List[List[T]] = [[] for _ in range(num_partitions)]

    for item in stream:
        partition_id = hash(key(item)) % num_partitions
        partitions[partition_id].append(item)

    # Process each partition (in production: parallel on different nodes)
    for partition in partitions:
        # Deduplicate within partition
        seen: Set[Hashable] = set()
        for item in partition:
            item_key = key(item)
            if item_key not in seen:
                yield item


def print_section(title):
    print("\n" + "=" * 60)
    print(title.center(60))
    print("=" * 60)

# ==============================================
#         TESTING AND DEMONSTRATION
# ==============================================

if __name__ == "__main__":
    print_section("DEDUPLICATION TESTS")

    # Test 1: Basic deduplication
    print("\n1. Basic Deduplication:")
    print("-----------------------")
    data = [1, 2, 2, 3, 1, 4, 3, 5, 1]
    result = list(deduplicate(iter(data)))
    print(f"    Input:  {data}")
    print(f"    Output: {result}")


    # Test 2: Deduplication with key function
    print(f"\n2. Deduplication with key Function:")
    print("-----------------------------------")
    records = [
        {'id': 1, 'name': 'Alice', 'version': 1},
        {'id': 2, 'name': 'Bob', 'version': 1},
        {'id': 1, 'name': 'Alice', 'version': 2},       # Duplicate ID
        {'id': 3, 'name': 'Charlie', 'version': 1},
    ]
    result = list(deduplicate(iter(records), key=lambda x: x['id']))
    print(f"    Kept {len(result)} unique records (by ID)")
    for r in result:
        print(f"    {r}")


    # Test 3: Keep latest
    print("\n3. Keep Latest Version:")
    print("-----------------------")
    result = list(deduplicate_with_latest(iter(records), key=lambda x: x['id']))
    print(f"    Kept latest version of each record:")
    for r in result:
        print(f"    {r}")


    # Test 4: Sorted stream (0(1)  memory)
    print("\n4. Deduplicate Sorted Stream (0(1) Memory):")
    print("-------------------------------------------")
    sorted_data = [1, 1, 1, 2, 2, 3, 4, 4, 4, 5]
    result = list(deduplicate_sorted_stream(iter(sorted_data)))
    print(f"    Input:  {sorted_data}")
    print(f"    Output: {result}")


    # Test 5: CDC processing
    print("\n5. CDC Event Processing:")
    print("------------------------")
    cdc_events = [
        {'operation': 'INSERT', 'id': 1, 'value': 'initial'},
        {'operation': 'UPDATE', 'id': 1, 'value': 'updated'},
        {'operation': 'INSERT', 'id': 2, 'value': 'second'},
        {'operation': 'DELETE',  'id': 1},
    ]
    processor = CDCDeduplicator()
    result = list(processor.process_stream(iter(cdc_events)))
    print(f"    Final state:    {result}")