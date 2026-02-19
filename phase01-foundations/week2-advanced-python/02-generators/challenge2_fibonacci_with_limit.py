"""
PROGRAM: Bounded Fibonacci Sequence Generatror
----------------------------------------------

Generates Fibonacci numbers up to a specified maximum value.
Useful for mathematical computations, data sampling, and algorithm testing.
"""
import time
from typing import Iterator, Callable, Any

def fibonacci_below(max_value: int) -> Iterator[int]:
    """
    Generate Fibonacci sequence value below a specified  maximum.

    The Fibonacci sequence is defined as:
    F(0) = 0, F(1) = 1, F(n) = F(n-1) + F(n-2)

    This generator is useful for:
    - Creating test datasets with known properties
    - Implementing backoff strategies (Fibonacci backoff)
    - Mathematical computations requiring Fibonacci numbers

    Args:
        max_value: Maximum value (exclusive). Must be non-negative

    Yields:
        int: Fibonacci numbers less than max_value

    Raises:
        ValueError: If max_value is negative

    Example:
        >>> list(fibonacci_below(100))
        [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        
        >>> # Use for exponential backoff in retry logic
        >>> for delay in fibonacci_below(3600):  # Max 1 hour
        ...     time.sleep(delay)
        ...     if retry_operation():
        ...         break
    
    Time Complexity: O(log(max_value)) - Number of Fibonacci numbers below max
    Space Complexity: O(1) - Constant memory
    """
    if max_value < 0:
        raise ValueError(f"max_value must be non-negative, got {max_value}")
    
    a, b = 0, 1
    
    # Generate sequence until we exceed max_value
    while a < max_value:
        yield a
        a, b = b, a + b


def fibonacci_range(start: int, end: int) -> Iterator[int]:
    """
    Generate Fibonacci numbers within a specified rang [start, end].

    Args:
        start: Minimum value (inclusive)
        end: Maximum value (exclusive)

    Yields:
        int: Fibonacci numbers in the specified range

    Example:
        >>> list(fibonacci_range(10, 100))
        [13, 21, 34, 55, 89]
    """
    if start < 0 or end < 0:
        raise ValueError("Start and end must be non-negative")
    
    if start >= end:
        raise ValueError("Start must be less than end")
    
    for fib in fibonacci_below(end):
        if fib >= start:
            yield fib


# ==================================================
#     USAGE: FIBONACCI BACKOFF FOR RETRY LOGIC
# ==================================================
def fibonacci_backoff_retry(
        operation: Callable,
        max_delay: int = 60,
        max_attempts: int = 5
) -> Any:
    """
    Retry an operation with Fibonacci backoff.

    Pattern used in distributed systems for exponential-like backoff that's 
    gentler than pure exponential backoff.

    Args:
        operation: Callable to retry
        max_delay: Maximum delay between retries (seconds)
        max_attempts: Maximum number of retry attempts

    Returns:
        Result of successful operation

    Raises:
        Exception: Last exception if all retries fail
    """
    last_exception = None
    # Use enumerate on the generator to keep memory 0(1)
    for attempt, delay in enumerate(fibonacci_below(max_delay), 1):
        try:
            return operation()
        except Exception as e:
            last_exception = e
            if attempt > max_attempts:
                break
            print(f"Attempt {attempt} failed. Retrying in {delay}s...")
            time.sleep(delay)

    raise last_exception