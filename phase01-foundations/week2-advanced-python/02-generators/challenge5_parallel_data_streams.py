"""
PROGRAM: Merge Sorted Streams: Distributed Data Processing
----------------------------------------------------------

Efficiently merge multiple sorted data streams into a single sorted  output.
Core algorithm for distributed computing and external sorting.
"""

import heapq
from typing import Iterator, TypeVar, Tuple, List, Dict

T = TypeVar('T')

def merge_sorted_streams(*streams: Iterator[T]) -> Iterator[T]:
    """
    Merge multiple sorted iterators into a single sorted output.

    Uses a min-heap for efficient merging.
    This is the algorithm used in:
    - External merge sort (sorting data larger than RAM)
    - Distributed query processing (merging sorted results from multiple nodes)
    - Time-series data processing (combining multiple sensor streams)

    Algorithm:
    1. Take first element from each stream and put in heap
    2. Pop minimum element from heap, yield it
    3. Get next element from that stream, add to heap
    4. Repeat until all streams exhausted
    
    Args:
        *streams: Variable number of sorted iterators
    
    Yields:
        T: Elements in sorted order
    
    Raises:
        ValueError: If any stream is not sorted
    
    Time Complexity: O(N log k) where N = total elements, k = number of streams
    Space Complexity: O(k) - heap size equals number of streams
    
    Example:
        >>> stream1 = iter([1, 3, 5, 7])
        >>> stream2 = iter([2, 4, 6, 8])
        >>> stream3 = iter([0, 5, 10])
        >>> merged = merge_sorted_streams(stream1, stream2, stream3)
        >>> list(merged)
        [0, 1, 2, 3, 4, 5, 5, 6, 7, 8, 10]
    
    Production Use Case:
        Merging sorted partitions from distributed query:
        >>> partitions = [
        ...     sorted_results_from_node_1(),
        ...     sorted_results_from_node_2(),
        ...     sorted_results_from_node_3(),
        ... ]
        >>> final_results = merge_sorted_streams(*partitions)    
    """
    if not streams:
        return
    
    # Initialize heap with first element from each stream
    # Heap contains tuples (value, stream_index, iterator)\
    heap: List[Tuple[T, int, Iterator[T]]] = []

    for stream_index, stream in enumerate(streams):
        try:
            first_value = next(stream)
            heapq.heappush(heap, (first_value, stream_index, stream))
        except StopIteration:
            # Stream is empty, skip it
            continue

    # Track last value from each stream to verify sorting
    last_values: List[T] = [None] * len(streams)

    # Process heap
    while heap:
        # Pop minimum element
        value, stream_idx, stream = heapq.heappop(heap)

        # Verify stream is sorted
        if last_values[stream_idx] is not None:
            if value < last_values[stream_idx]:
                raise ValueError(
                    f"Stream {stream_idx} is not sorted: "
                    f"{last_values[stream_idx]} followed by {value}"
                )
        last_values[stream_idx] = value

        yield value

        # Get next value from this stream
        try:
            next_value = next(stream)
            heapq.heappush(heap, (next_value, stream_idx, stream))
        except StopIteration:
            # This stream is exhausted
            pass


def merge_sorted_streams_with_metadata(*streams: Tuple[Iterator[T], str]) -> Iterator[Tuple[T, str]]:
    """
    Merge sorted streams while preserving source metadata.

    Useful for distributed query processing where you need to track which partition/node each result came from.

    Args:
        *streams: Tuple of (iterator, source_indentifier)
    
    Yields:
        Tuple[T, str]: (value, source_identifier)

    Example:
        >>> results = merge_sorted_streams_with_metadata(
        ...     (iter([1, 5, 9]), 'node1'),
        ...     (iter([2, 6, 10]), 'node2'),
        ...     (iter([3, 7, 11]), 'node3'),
        ... )
        >>> for value, source in results:
        ...     print(f"{value} from {source}")  
    """
    if not streams:
        return
    
    # Initialize heap
    heap: List[Tuple[T, int, str, Iterator[T]]] = []

    for idx, (stream, source_id) in enumerate(streams):
        try:
            first_value = next(stream)
            heapq.heappush(heap, (first_value, idx, source_id, stream))
        except StopIteration:
            continue

    while heap:
        value, idx, source_id, stream = heapq.heappop(heap)
        yield (value, source_id)

        try:
            next_value = next(stream)
            heapq.heappush(heap, (next_value, idx, source_id, stream))
        except StopIteration:
            pass


# =========================================================
#   PRODUCTION PATTERN: Distributed query result merging
# =========================================================

class DistributedQueryMerger:
    """
    Merge sorted results from multiple database shards/partitions.

    Production pattern for distributed databases and data warehouses.
    """

    def __init__(self, partition_queries: List[str], connection_pool):
        """
        Initialize distributed query merger.

        Args:
            partition_queries: SQL queries for each partition
            connection_pool: Database connection pool        
        """
        self.partition_queries = partition_queries
        self.connecion_pool = connection_pool

    def execute_partition_query(self, query: str, partition_id: int) -> Iterator[Tuple[int, Dict]]:
        """
        Execute query on a partition and yield results.

        Args:
            query: SQL query
            partition_id: Partition identifier

        Yields:
            Tuple[int, Dict]: (sort_key, record)        
        """
        # In production, this would execute query on database
        # Simulated here
        results = [
            {'id': 1, 'value': i * 10, 'partition': partition_id}
            for i in range(partition_id * 100, (partition_id + 1) * 100)
        ]

        for record in results:
            # Yield (sort_key, record)
            yield (record['id'], record)

    def merge_results(self) -> Iterator[Dict]:
        """
        Execute queries on all partitions and merge sorted results.

        Yields:
            Dict: Records in sorted order        
        """
        # Create stream for each partition
        partition_streams = [
            (
                (sort_key for sort_key, _ in self.execute_partition_query(query, idx)),
                self.execute_partition_query(query, idx)
            )
            for idx, query in enumerate(self.partition_queries)
        ]

        # Merge streams
        for sort_key, record in merge_sorted_streams(*[s[1] for s in partition_streams]):
            yield record


# ======================================
#    TESTING WITH EXAMAPLE DATA
# ======================================

if __name__ == "__main__":
    print("\nTESTING merge_sorted_streams")
    print("=" * 50)

    # Test 1: Basic merge
    stream1 = iter([1, 3, 5, 7, 9])
    stream2 = iter([2, 4, 6, 8, 10])
    stream3 = iter([0, 5, 15])

    merged = list(merge_sorted_streams(stream1, stream2, stream3))
    print(f"Merged: {merged}")
    assert merged == [0, 1, 2, 3, 4, 5, 5, 6, 7, 8, 9, 10, 15]

    # Test 2: With metadata
    print("\nTESTING with metadata:")
    results = merge_sorted_streams_with_metadata(
        (iter([1, 5, 9]), 'shard_1'),
        (iter([2, 6, 10]), 'shard_2'),
        (iter([3, 7, 11]), 'shard_3'),
    )
    for value, source in results:
        print(f"    {value} from {source}")

    # Test 3: Error detection
    print("\nTESTING error detection")
    try:
        bad_stream = iter([1, 5, 3, 7])  # Not sorted
        good_stream = iter([2, 4, 6])
        list(merge_sorted_streams(bad_stream, good_stream))
        print("     ERROR: Should have detected unsorted stream")
    except ValueError as e:
        print(f"Correctly detected unsorted stream: {e}")