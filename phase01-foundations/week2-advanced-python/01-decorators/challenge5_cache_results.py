import time
from functools import wraps
from typing import Callable, Any, Dict, Tuple

def cache_result(func: Callable) -> Callable:
    """
    A decorator that caches function results based on their input arguments.

    DE Context:
    Caching is essential when dealing with expensive API calls or heavy data transformations.
    This pattern ensures we only "pay" the computation cost once for any unique set of inputs.
    """
    # 1. Initialize a private dictionary to store cached results
    # Key = Tuple of function arguments, Value = Result of the function call
    _cache: Dict[Tuple[Any, ...], Any] = {}

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # 2. Create a hashable key from the function arguments
        # We convert kwargs to a sorted tuple of items because dictionaries are not hashable
        cache_key = (args, tuple(sorted(kwargs.items())))

        # 3. Check if we seen  these argument before
        if cache_key not in _cache:
            # First time seeing these args: execute the function and store the result in the cache
            _cache[cache_key] = func(*args, **kwargs)

        # 4. Return the cached result
        return _cache[cache_key]
    
    return wrapper

# =========================================
#                 TESTING
# =========================================

@cache_result
def expensive_calculation(x: int, y: int) -> int:
    """Simulates a heavy computational task"""
    time.sleep(2)  # Simulate a delay
    return x * y


if __name__ == "__main__":
    # First call: Ttakes 2 seconds
    print(f"Call 1 (5, 3): {expensive_calculation(5, 3)}") 

    # Second call with same args: Should be instant
    print(f"Call 2 (5, 3): {expensive_calculation(5, 3)}")

    # Third call (new args): Takes 2 seconds again
    print(f"Call 3 (5, 4): {expensive_calculation(5, 4)}")