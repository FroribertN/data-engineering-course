import time
from functools import wraps
from typing import Callable, Any, List

def rate_limit(max_calls: int, time_window: int) -> Callable:
    """
    A decorator that ensures a function is not called more than max_calls within time_window seconds.

    DE Context:
    Essential for interacting with exernal APIs that have strict usage limits.
    This prevents your pipelines from being blocked due to exceeding API call limits, ensuring smooth data retrieval and processing.
    """
    def decorator(func: Callable) -> Callable:
        # State: Persistent list of timestamps for this specific function instance
        timestamps: List[float] = []

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_time = time.time()

            # 1. Filter out timestamps that have expired (outside thhe time window)
            # Logic: keep 't' only if (current_time - t) is less than the time_window
            timestamps[:] = [t for t in timestamps if current_time - t < time_window]

            # 2. Check if we have reached the max_calls limit
            if len(timestamps) >= max_calls:
                raise Exception(f"Rate limit exceeded: Max {max_calls} calls allowed per {time_window}s.")
            
            # 3. Record the current call's timestamp and exceute the function
            timestamps.append(current_time)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# =====================================
#           TESTING
# =====================================

@rate_limit(max_calls=3, time_window=10)
def api_call():
    """Simulates a restricted external API requestt"""
    return "successful API call"


if __name__ == "__main__":
    try:
        print(f"Call 1: {api_call()}")
        print(f"Call 2: {api_call()}")
        print(f"Call 3: {api_call()}")
        print(f"Call 4 (should fail): {api_call()}")
    except Exception as e:
        print(f"Caught: {e}")