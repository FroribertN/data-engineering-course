"""
PROGRAM: Count Calls
--------------------

Create a decorator that tracks how many times a function has been called.
"""

from functools import wraps
from typing import Callable, Any

def count_calls(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    DE Context: In complex ETL flows, tracking call counts is vital for detecting 'infinite loops'
    in recursive data parsing or for implementing basic circuit breakers when an API extractor exceeds
    its daily quota.

    Args:
        func: The target function to monitor

    Returns: 
        Callable: The wrapped function equipped with a '.call_count'attribute.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # increment the call counter attached to this specific function object 
        wrapper.call_count += 1
        return func(*args, **kwargs)
    
    # Initialize the attribute on the wrapper function (ensuring it exists even before the first call)
    wrapper.call_count = 0
    
    return wrapper

# -------- PRODUCTION SIMULATION --------

@count_calls
def process_record() -> str:
    """Simulates processing a single data record"""
    return "done"

if __name__ == "__main__":
    # Simulates three separate data events
    process_record()
    process_record()
    process_record()

    # Accessing the metadata injected by the decorator to report call count
    print(f"\n====== METRIC REPORT ======")
    print(f"Function: {process_record.__name__}")
    print(f"Total Calls: {process_record.call_count}")