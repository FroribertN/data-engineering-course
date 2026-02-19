"""
PROGRAM:Resource Limiter - Concurrency Control
----------------------------------------------

Limiits concurrent access to resources using semaphores.
Essential for rate limiting, connection pooling, and preventing resource exhaustion.
"""

import threading
import time
import logging
from contextlib import contextmanager
from typing import Optional, Iterator
from dataclasses import dataclass
from datetime import datetime
import queue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LimiterStats:
    """Statistics about resource limiter usage"""
    total_acquisitions: int
    total_releases: int
    current_active: int
    max_concurrent: int
    total_wait_time: float
    acquisition_times: list


class ResourceLimiter:
    """
    Limit concurrent access to resources using semaphore.
    
    Thread-safe concurrency limiter. Ensures that at most N threads
    can access a resource simultaneously.
    
    Use Cases:
    - Database connection limits (max 10 concurrent connections)
    - API rate limiting (max 5 concurrent requests)
    - File handle limits (max 100 open files)
    - CPU-bound task limits (max 4 concurrent processing jobs)
    
    Example:
        >>> limiter = ResourceLimiter(max_concurrent=5)
        >>> 
        >>> def worker():
        ...     with limiter:
        ...         # Only 5 threads can be here at once
        ...         expensive_operation()
        >>> 
        >>> threads = [threading.Thread(target=worker) for _ in range(20)]
        >>> for t in threads: t.start()
        >>> # Only 5 workers active at once, others wait
    
    Production Pattern:
        >>> # Limit concurrent API calls
        >>> api_limiter = ResourceLimiter(max_concurrent=10)
        >>> 
        >>> def fetch_data(url):
        ...     with api_limiter:
        ...         return requests.get(url)
        >>> 
        >>> # Even with 1000 URLs, max 10 concurrent requests
        >>> results = [fetch_data(url) for url in urls]
    """

    def __init__(self, max_concurrent: int, timeout: Optional[float] = None, name: str = "ResourceLimiter"):

        """
        Initialize resource limiter.
        
        Args:
            max_concurrent: Maximum concurrent acquisitions allowed
            timeout: Seconds to wait for acquisition (None = wait forever)
            name: Name for logging and debugging
        
        Raises:
            ValueError: If max_concurrent < 1
        """
        if max_concurrent < 1:
            raise ValueError(f"max_concurrent must be >= 1, got {max_concurrent}")
        
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.name = name

        # Semaphore for limiting concurrency
        self._semaphore = threading.Semaphore(max_concurrent)

        # Statistics tracking
        self._lock = threading.Lock()
        self._stats = {
            'acquisitions': 0,
            'releases': 0,
            'active': 0,
            'wait_times': [],
            'timeouts': 0,
        }

        logger.info(f"{name}: Initialized with max_concurrent={max_concurrent}, timeout={timeout}")


    def __enter__(self):
        """Acquire resource (blocking)"""
        start_time = time.time()

        # Try to acquire semaphore
        acquired = self._semaphore.acquire(timeout=self.timeout)

        if not acquired:
            # Timeout
            with self._lock:
                self._stats['timeouts'] += 1
            raise TimeoutError(f"{self.name}: Could not acqure resource within {self.timeout}s")
        
        # Tracking stats
        wait_time = time.time() - start_time
        with self._lock:
            self._stats['acquisitions'] += 1
            self._stats['active'] += 1
            self._stats['wait_times'].append(wait_time)

        logger.debug(f"{self.name}: Acquired (active: {self._stats['active']}/{self.max_concurrent})")

        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release resource"""
        self._semaphore.release()

        with self._lock:
            self._stats['releases'] += 1
            self._stats['active'] -= 1

        logger.debug(f"{self.name}: Released (active: {self._stats['active']}/{self.max_concurrent})")

        return False
    
    def get_stats(self) -> LimiterStats:
        """
        Get current limiter statistics.

        Returns:
            LimiterStats: Current statistics.
        """
        with self._lock:
            total_wait = sum(self._stats['wait_times'])

            return LimiterStats(
                total_acquisitions=self._stats['acquisitions'],
                total_releases=self._stats['releases'],
                current_active=self._stats['active'],
                max_concurrent=self.max_concurrent,
                total_wait_time=total_wait,
                acquisition_times=self._stats['wait_times'].copy()
            )


class RateLimiter:
    """
    Rate limiter using token bucket algorithm.
    
    Limits operations per time window (e.g., 100 requests per second).
    More sophisticated than simple concurrent limiter.
    
    Token Bucket Algorithm:
    - Bucket holds N tokens
    - Each operation consumes 1 token
    - Tokens refill at constant rate
    - If no tokens available, wait or fail
    
    Example:
        >>> limiter = RateLimiter(rate=10, per_seconds=1)  # 10 ops/second
        >>> 
        >>> for i in range(100):
        ...     with limiter:
        ...         api_call()
        >>> # Automatically throttled to 10 calls/second
    """

    def __init__(self, rate: int, per_seconds: float = 1.0, burst: Optional[int] = None):
        """
        Initialize rate limiter.
        
        Args:
            rate: Number of operations allowed
            per_seconds: Time window in seconds
            burst: Maximum burst size (default: same as rate)
        
        Example:
            >>> # 100 requests per second
            >>> limiter = RateLimiter(rate=100, per_seconds=1.0)
            >>> 
            >>> # 1000 requests per minute (16.67/sec)
            >>> limiter = RateLimiter(rate=1000, per_seconds=60.0)
        """
        self.rate = rate
        self.per_seconds = per_seconds
        self.burst = burst or rate

        # Token bucket
        self._tokens = float(self.burst)
        self._last_update = time.time()
        self._lock = threading.Lock()

        logger.info(f"RateLimiter: {rate} operations per {per_seconds}s (burst: {self.burst})")

    def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self._last_update

        # Calculate tokens to add
        tokens_to_add = (elapsed / self.per_seconds) * self.rate

        # Add tokens (capped at burst)
        self._tokens = min(self.burst, self._tokens + tokens_to_add)
        self._last_update = now

    def __enter__(self):
        """Acquire token (blocking until available)"""
        while True:
            with self._lock:
                self._refill_tokens()

                if self._tokens >= 1.0:
                    # Token available
                    self._tokens -= 1
                    logger.debug(f"RateLimiter: Token acquired ({self._tokens:.1f} remaining)")
                    return self
                
                # No token available
                tokens_needed = 1.0 - self._tokens
                wait_time = (tokens_needed / self.rate) * self.per_seconds

            time.sleep(wait_time)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """No-op for rate limiter"""
        return False
    

class AdaptiveRateLimiter:
    """
    Adaptive rate limiter that adjusts based on success/failure rate.
    
    Increases rate on success, decreases on failure.
    Useful for APIs with dynamic rate limits or backpressure.
    
    Example:
        >>> limiter = AdaptiveRateLimiter(initial_rate=100, min_rate=10, max_rate=1000)
        >>> 
        >>> with limiter:
        ...     try:
        ...         api_call()
        ...         limiter.record_success()
        ...     except RateLimitError:
        ...         limiter.record_failure()
        >>> # Rate automatically adjusts based on API responses
    """

    def __init__(self, initial_rate: int, min_rate: int, max_rate: int, increase_factor: float = 1.1, decrease_factor: float = 0.5):
        """
        Initialize adaptive rate limiter.
        
        Args:
            initial_rate: Starting rate
            min_rate: Minimum allowed rate
            max_rate: Maximum allowed rate
            increase_factor: Multiply rate by this on success
            decrease_factor: Multiply rate by this on failure
        """
        self.current_rate = float(initial_rate)
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.increase_factor = increase_factor
        self.decrease_factor = decrease_factor

        self._lock = threading.Lock()
        self._last_update = time.time()
        self._tokens = 1.0

        logger.info(f"AdaptiveRateLimiter: initial={initial_rate}, range=[{min_rate}, {max_rate}]")

    def record_success(self) -> None:
        """Record successful operation - increase rate"""
        with self._lock:
            old_rate = self.current_rate
            self.current_rate = min(
                self.max_rate,
                self.current_rate * self.increase_factor
            )

            if self.current_rate != old_rate:
                logger.info(f"AdaptiveRateLimiter: increased rate {old_rate:.1f} -> {self.current_rate:.1f}")

    def record_failure(self) -> None:
        """Record failed operation - decrease factor"""
        with self._lock:
            old_rate = self.current_rate
            self.current_rate = max(
                self.min_rate,
                self.current_rate * self.decrease_factor
            )

            if self.current_rate != old_rate:
                logger.info(f"AdaptiveRateLimiter: Decreased rate {old_rate:.1f} -> {self.current_rate:.1f}")

    def __enter__(self):
        """Acquire token based on current rate"""
        while True:
            with self._lock:
                now = time.time()
                elapsed = now - self._last_update

                # Refill tokens
                tokens_to_add = elapsed * self.current_rate
                self._tokens = min(float(self.max_rate), self._tokens + tokens_to_add)
                self._last_update = now

                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return self
                
            # Wait
            time.sleep(0.01)

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
    


# Test
if __name__ == "__main__":
    print("\nTESTING RESOURCE LIMITER")
    print("=" * 60)

    # Test 1: Basic concurrency limiting
    print("\n1. Testing concurrent access limiting:")
    limiter = ResourceLimiter(max_concurrent=3, name="TestLimiter")

    active_count = {'value': 0}
    max_active = {'value': 0}
    lock = threading.Lock()

    def worker(worker_id):
        with limiter:
            # Track active workers
            with lock:
                active_count['value'] += 1
                max_active['value'] = max(max_active['value'], active_count['value'])

            # Simulate work
            time.sleep(0.1)

            with lock:
                active_count['value'] -= 1

    # Start 10 worker
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"    Max concurrent: {max_active['value']}")
    print(f"    Limiter to 3 concurrent (got {max_active['value']})")
    assert max_active['value'] <= 3

    # Test 2
    print(f"\n2. Limiter statistics:")
    stats = limiter.get_stats()
    print(f"    Total acquisitions: {stats.total_acquisitions}")
    print(f"    Total releases:     {stats.total_releases}")
    print(f"    Current active:     {stats.current_active}")
    print(f"    Total wait time:    {stats.total_wait_time:.3f}s")

    # Test 3: Rate limiting
    print("\n3. Testing rate limiter:")
    rate_limiter = RateLimiter(rate=5, per_seconds=1.0)

    start = time.time()
    for i in range(10):
        with rate_limiter:
            pass
    elapsed = time.time() - start

    print(f"    10 operations took {elapsed:.2f}s")
    print(f"    Rate limited to ~5 ops/second")

    # Test 4: Adaptive rate limiter
    print("\n4. Testing adaptive rate limiter:")
    adaptive = AdaptiveRateLimiter(initial_rate=10, min_rate=5, max_rate=50)
    
    print(f"    Initial rate: {adaptive.current_rate:.1f}")

    # Simulate success
    for _ in range(5):
        adaptive.record_success()
    print(f"    After 5 successes: {adaptive.current_rate:.1f}")

    # Simulate fail
    for _ in range(3):
        adaptive.record_failure()
    print(f"    After 3 failure: {adaptive.current_rate:.1f}")
    print(f"    Rate adapted for success/failure")