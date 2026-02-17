import time
from functools import wraps
from typing import Callable, Any, List

def cache_result(func: Callable) -> Callable:
    cache = {}

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Create a hashable key from the function arguments
        # Args iis already a tuple (hashable)
        # kwargs needs to be converted to a tuple of sorted items (hashable)
        key = (args, tuple(sorted(kwargs.items())))

        if key in cache:
            print(f"Cache hit for {func.__name__} with args {args}")
            return cache[key]
        
        print(f"Cache miss - computing {func.__name__} {args}")
        result = func(*args, **kwargs)
        cache[key] = result
        return result
    
    # Add a method to clear the cache
    def cache_clear():
        cache.clear()
        print("Cache cleared")

    wrapper.cache_clear = cache_clear
    wrapper._cache = cache  # Expose the cache for testing purposes

    return wrapper


# ======================================
#                TESTING
# ======================================

@cache_result
def expensive_calculation(x: int, y: int) -> int:
    print(f"      COMPUTING {x} + {y}...")
    time.sleep(2)  # Simulate a time-consuming calculation
    return x + y

print(expensive_calculation(5, 3)) # Takes 2 seconds, cache miss
print(expensive_calculation(5, 3)) # Instant, cache hit
print(expensive_calculation(5, 4)) # Takes 2 seconds, cache miss
print(expensive_calculation(5, 3)) # Instant, cache hit

# Clear the cache and test again
expensive_calculation.cache_clear() # Clear the cache
print(expensive_calculation(5, 3)) # Takes 2 seconds, cache miss after clearing