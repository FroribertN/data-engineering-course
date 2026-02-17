from functools import wraps
from typing import Callable, Any

def uppercase_result(func: Callable[..., Any])  -> Callable[..., Any]:
    """
    A decorator that intercepts the return value of a function and converts it to uppercase if it's a string.

    DE context: This is useful in data cleaning pipelines where specific fields (like ISO Country Codes or Currency Codes)
    must be normalized to uppercase before being written to a data warehouse.

    Arhs:
        func: Callable - the function to be decorated

    Returns:
        Callable: The wrapped function that returns an uppercase string.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Execute the primary logic of the original function and capture its return value
        result = func(*args, **kwargs)

        # Validation: Check if the result is a string before converting to uppercase
        if isinstance(result, str):
            return result.upper()
        
        return result
    
    return wrapper

@uppercase_result
def get_name() -> str:
    """Returns the name of the user"""
    return "alice"


# ===========================
# Test the decorated function
# ===========================

if __name__ == "__main__":
    print(f"Result: {get_name()}") 

    # Metadata Check
    print(f"Function identity preserved: {get_name.__name__}")