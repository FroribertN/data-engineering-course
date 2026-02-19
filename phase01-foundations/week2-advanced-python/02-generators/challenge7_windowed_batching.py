"""
PROGRAM: Windowed Batching - Time-Based Stream Processing

Batch streaming data based on size OR time constraints.
Core pattern for real-time data pipelines and streaming analytics.
"""

import time
from typing import Iterator, List, TypeVar, Optional, Any, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

T = TypeVar('T')


class BatchTrigger(Enum):
    """Reason why a batch was emitted"""
    SIZE_LIMIT = "size_limit"
    TIMEOUT = "timeout"
    STREAM_END = "stream_end"


@dataclass
class Batch:
    """Container for a batch with metadata"""
    items: List[Any]
    trigger: BatchTrigger
    start_time: float
    end_time: float

    @property
    def duration(self) -> float:
        """Duration of batch in seconds"""
        return self.end_time - self.start_time
    
    @property
    def size(self) -> int:
        """Number of items in batch"""
        return len(self.items)
    

def batch_with_timeout(stream: Iterator[T], max_size: int = 100, timeout: float = 5.0) -> Iterator[List[T]]:
    """
    Batch items from stream based on size OR time limit.
    
    Critical pattern for:
    - Real-time analytics (flush metrics every N seconds)
    - Bulk API calls (batch requests, but don't wait forever)
    - Database bulk inserts (batch writes with timeout)
    - Message queue processing (commit offsets periodically)
    
    A batch is emitted when EITHER:
    - Batch reaches max_size items, OR
    - timeout seconds have passed since batch started
    
    Args:
        stream: Input data stream
        max_size: Maximum items per batch
        timeout: Maximum seconds to wait before flushing batch
    
    Yields:
        List[T]: Batches of items
    
    Example:
        >>> def slow_stream():
        ...     for i in range(100):
        ...         time.sleep(0.3)  # Slow data arrival
        ...         yield i
        >>> 
        >>> batches = batch_with_timeout(
        ...     slow_stream(),
        ...     max_size=10,
        ...     timeout=2.0
        ... )
        >>> # Some batches will have 10 items (size limit)
        >>> # Others will have <10 items (timeout)
    
    Production Use Cases:
        # Bulk database inserts with timeout
        >>> for batch in batch_with_timeout(records, max_size=1000, timeout=30):
        ...     db.bulk_insert(batch)
        ...     db.commit()
        
        # API rate limiting
        >>> for batch in batch_with_timeout(requests, max_size=100, timeout=60):
        ...     api.bulk_request(batch)
        ...     time.sleep(1)  # Rate limit
    """
    if max_size < 1:
        raise ValueError(f"max_size must be >= 1, got {max_size}")
    if timeout <= 0:
        raise ValueError(f"timeout must be > 0, got {timeout}")
    
    batch: List[T] = []
    batch_start_time = time.time()

    for item in stream:
        current_time = time.time()
        elapsed = current_time - batch_start_time

        # Check if timeout exceed BEFORE adding item
        if elapsed >= timeout and batch:
            # Timeout reached - flush current batch
            yield batch
            batch = []
            batch_start_time = current_time

        # Add item to batch
        batch.append(item)

        # Check if size limit reached
        if len(batch) >= max_size:
            yield batch
            batch = []
            batch_start_time = current_time

    # Do not forget remaining items
    if batch:
        yield batch


def batch_with_timeout_metadata(stream: Iterator[T], max_size: int = 100, timeout: float = 5.0) -> Iterator[Batch]:
    """
    Enhanced batching with metadata about why batch was emitted.
    
    Provides debugging and monitoring information about batch behaviour.
    
    Args:
        stream: Input data stream
        max_size: Maximum items per batch
        timeout: Maximum seconds before flushing
    
    Yields:
        Batch: Batch object with items and metadata
    
    Example:
        >>> for batch in batch_with_timeout_metadata(stream, 100, 5.0):
        ...     print(f"Batch of {batch.size} items "
        ...           f"(trigger: {batch.trigger.value}, "
        ...           f"duration: {batch.duration:.2f}s)")
        ...     process(batch.items)
    """
    batch_items: List[T] = []
    batch_start = time.time()

    for item in stream:
        current = time.time()
        elapsed = current - batch_start

        # Check timeout
        if elapsed >= timeout and batch_items:
            yield Batch(
                items=batch_items,
                trigger=BatchTrigger.TIMEOUT,
                start_time=batch_start,
                end_time=current
            )
            batch_items = []
            batch_start = current
        
        batch_items.append(item)

        # Check size
        if len(batch_items) >= max_size:
            yield Batch(
                items=batch_items,
                trigger=BatchTrigger.SIZE_LIMIT,
                start_time=batch_start,
                end_time=time.time()
            )
            batch_items = []
            batch_start = time.time()

    # Remaining items
    if batch_items:
        yield Batch(
            items=batch_items,
            trigger=BatchTrigger.STREAM_END,
            start_time=batch_start,
            end_time=time.time()
        )


def tumbling_window(stream: Iterator[T], window_size: float) -> Iterator[List[T]]:
    """
    Create fixed-size tumbling windows.
    
    Windows do NOT overlap. Each item belongs to exactly one window.
    
    Args:
        stream: Input data stream
        window_size: Window duration in seconds
    
    Yields:
        List[T]: Items in each window
    
    Example:
        >>> # Process data in 60-second windows
        >>> for window in tumbling_window(events, window_size=60):
        ...     metrics = calculate_metrics(window)
        ...     store_metrics(metrics)
    """
    window: List[T] = []
    window_start = time.time()

    for item in stream:
        current = time.time()

        # Check if we have passed window boundary
        if current - window_start >= window_size:
            if window:
                yield window
            window = []
            window_start = current
        
        window.append(item)

    if window:
        yield window


def sliding_window(stream: Iterator[T], window_size: float, slide_interval: float) -> Iterator[List[T]]:
    """
    Create overlapping sliding windows.
    
    Windows overlap - each item may appear in multiple windows.
    
    Args:
        stream: Input data stream
        window_size: Window duration in seconds
        slide_interval: How often to emit a window (seconds)
    
    Yields:
        List[T]: Items in each window
    
    Example:
        >>> # 60-second windows, emitted every 30 seconds (50% overlap)
        >>> for window in sliding_window(events, window_size=60, slide_interval=30):
        ...     avg = calculate_average(window)
        ...     print(f"Moving average: {avg}")
    
    Note:
        Requires buffering items for window_size duration.
        Memory usage: O(items in window_size seconds)
    """
    from collections import deque

    # Buffer to hold items with timestamps
    buffer: deque = deque()
    last_window_time = time.time()

    for item in stream:
        current = time.time()

        # Add item with timestamp
        buffer.append(current, item)

        # Remove items outside window
        cutoff_time = current - window_size
        while buffer and buffer[0][0] < cutoff_time:
            buffer.popleft()

        # Check if it is time to emit a window
        if current - window_size >= slide_interval:
            # Emit current window
            window_items = [item for _, item in buffer]
            if window_items:
                yield window_items
            last_window_time = current


# ===========================================================
#      PRODUCTION PATTERN: Real-Time Metrics Aggregation
# ===========================================================

class StreamingAggregator:
    """
    Aggregate streaming metrics with windowed batching.
    
    Production pattern for real-time dashboards and monitoring.
    """

    def __init__(self, window_size: float = 60.0, max_batch_size: int = 1000):
        """
        Initialize streaming aggregator.

        Args:
            window_size: Time window in seconds
            max_batch_size: Max events per batch
        """
        self.window_size = window_size
        self.max_batch_size = max_batch_size

    def process_event_stream(self, events: Iterator[Dict]) -> Iterator[Dict]:
        """
        Process event stream and emit windowed aggregations.
        
        Args:
            events: Stream of events with 'value' field
        
        Yields:
            Dict: Aggregated metrics for each window
        
        Example:
            >>> events = (
            ...     {'timestamp': time.time(), 'value': random.random()}
            ...     for _ in range(1000)
            ... )
            >>> aggregator = StreamingAggregator(window_size=5.0)
            >>> for metrics in aggregator.process_event_stream(events):
            ...     print(f"Count: {metrics['count']}, Avg: {metrics['avg']:.2f}")
        """
        for batch in batch_with_timeout(events, max_size=self.max_batch_size, timeout=self.window_size):
            # Aggregate batch
            values = [event['value'] for event in batch]

            yield {
                'timestamp': datetime.now().isoformat(),
                'count': len(values),
                'sum': sum(values),
                'avg': sum(values) / len(values) if values else 0.0,
                'min': min(values) if values else 0,
                'max': max(values) if values else 0,
            }


# =================================================
#     EXAMPLE: Simulated real-time processing
# =================================================
if __name__ == "__main__":
    import random

    print("\n" + "=" * 60)
    print("WINDOW BATCHING EXAMPLES".center(60))
    print("=" * 60)

    # Simulated slow data stream
    def simulated_stream(num_items: int = 50):
        """Simulate data arriving at variable rates"""
        for i in range(num_items):
            # Variable delay (0.1 to 0.5 seconds)
            delay = random.uniform(0.1, 0.5)
            time.sleep(delay)
            yield {'id': i, 'value': random.random(), 'delay': delay}

    print("\nTEST 1: Basic Windowed Batching")
    print("-" * 60)
    batch_count = 0
    start = time.time()

    for batch in batch_with_timeout(simulated_stream(30), max_size=10, timeout=2.0):
        batch_count += 1
        elapsed = time.time() - start
        print(f"Batch {batch_count}: {len(batch)} items after {elapsed:.1f}s")

    print(f"\nTotal Batches: {batch_count}")

    
    # Test with metadata
    print("\nTEST 2: Batching with Metadata")
    print("-" * 60)

    for batch in batch_with_timeout_metadata(simulated_stream(30), max_size=30, timeout=2.0):
        print(
            f"Batch: size={batch.size}, "
            f"trigger={batch.trigger.value}, "
            f"duration={batch.duration:.2f}s"
        )

    
    # Test streaming aggregation
    print("\nTEST 3: Real-Time Aggregation")
    print("=" * 60)

    def metric_steam():
        """Simulate metrics arriving"""
        for i in range(100):
            time.sleep(0.1)
            yield {'value': random.uniform(10, 100)}

    aggregator = StreamingAggregator(window_size=2.0, max_batch_size=50)

    for window_num, metrics in enumerate(aggregator.process_event_stream(metric_steam()), 1):
        print(
            f"Window {window_num}: "
            f"count={metrics['count']}, "
            f"avg={metrics['avg']:.2f}, "
            f"min={metrics['min']:.2f}, "
            f"max={metrics['max']:.2f}"
        )