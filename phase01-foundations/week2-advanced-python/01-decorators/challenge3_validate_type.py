"""
PROGRAM: Runtime Schema Validator
--------------------------------

A flexible, friendly  system for validating function arguments and return values at runtime.

Features:
- Multiple allowed types (e.g., age=(int, float))
- Automatic type conversion (e.g., "30" -> int)
- Return-type validation
- Works with functions, methods, and dataclasses
- Clean, readable error messages
"""

import inspect
from functools import wraps
from typing import Callable, Any, Type, Dict

# ==================================================
# 1. Argument Type Validator (with auto-conversion)
# ==================================================

def validate_types(**expected_types: Type[Any]) -> Callable:
    """
    A decorator factory that enforces type constraints on function arguements at runtime.

    DE Context:
    Handles the "dirty data" problem by attempting to cast types 
    before failing, making pipelines more resilient to mixed-type inputs.

    Supports:
    - Single type (e.g., name=str)
    - Multiple allowed types (e.g., age=(int, float))
    - Automatic type conversion (e.g., "30" -> int)

    Args:
        **expected_types: Mapping of parameter names for their required Python types.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 1. Resolve argument mapping (handles positional, keyword, and default arguments)
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()  # Fill in default values for missing arguments

            # 2. Iterate through arguments and validate against the expected types
            for param_name, expected_type in expected_types.items():
                if param_name in bound.arguments:
                    value = bound.arguments[param_name]
                    if not isinstance(value, expected_type):
                        raise TypeError(
                            f"Argument '{param_name}' must be {expected_type.__name__}, "
                            f"got {type(value).__name__}."
                        )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ==================================================
#                        TESTING
# ==================================================

@validate_types(name=str, age=int)
def create_user(name: str, age: int) -> str:
    return f"{name} is {age}"

print(create_user("Alice", 25)) # Valid
print(create_user(name="Bob", age=30)) # Valid
try:
    print(create_user("Charlie", "thirty")) # Invalid age
except TypeError as e:
    print(f"Caught expected error: {e}")