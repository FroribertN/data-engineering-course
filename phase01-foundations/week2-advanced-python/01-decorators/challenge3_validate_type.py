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
from typing import Callable, Any, Type, Tuple, Union

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
            for name, value in bound.arguments.items():
                if name not in expected_types:
                    continue

                allowed_types = expected_types[name]
                # Normalize allowed types to a tuple for consistent checking
                allowed_tuple = allowed_types if isinstance(allowed_types, tuple) else (allowed_types,)

                # Check if current value is already valid
                if isinstance(value, allowed_tuple):
                    continue

                # Attempt auto-conversion
                converted = False
                for target_type in allowed_tuple:
                    try:
                        bound.arguments[name] = target_type(value) # Try to convert value to target type
                        converted = True
                        break
                    except (ValueError, TypeError):
                        continue

                if not converted:
                    type_names = ", ".join(t.__name__ for t in allowed_tuple)
                    raise TypeError(
                        f"Argument '{name}' in {func.__name__}() failed validation. "
                        f"Expected {type_names}, got {type(value).__name__}."
                    )
            
            # Execute with cleaned/converted arguments
            return func(*bound.args, **bound.kwargs)
        return wrapper
    return decorator


# ==================================================
# 2. Return Type Validator
# ==================================================

def validate_return_type(expected_type: Union[Type[Any], Tuple[Type[Any], ...]]) -> Callable:
    """
    Ensures that the function output meets the expected schema before downstream usage.

    Args:
        expected_type: The expected return type.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            allowed_tuple = expected_type if isinstance(expected_type, tuple) else (expected_type,)

            if not isinstance(result, allowed_tuple):
                type_names = ", ".join(t.__name__ for t in allowed_tuple)
                raise TypeError(
                    f"Return value of {func.__name__}() must be {type_names}, "
                    f"not {type(result).__name__}."
                )
            return result
        return wrapper
    return decorator


# ====================================
#           TESTING
# ====================================

@validate_types(name=str, age=(int, float))
@validate_return_type(str)
def create_user(name: str, age: Union[int, float]) -> str:
    """Creates a standardized user record"""
    return f"User: {name}, Age: {age}"

if __name__ == "__main__":
    # Case 1: Strict match
    print(f"Success 1: {create_user('Alice', 25)}")

    # Case 2: Auto-conversion of age ('30' -> int)
    print(f"Success 2: {create_user('Bob', '30')} ")  

    # Case 3: Invalid Input (the uncovertable case)
    try:
        print("Attempting to pass 'Thirty' as an integer...")
        create_user('Charlie', 'Thirty')  # Age is a string that cannot be converted to int
    except TypeError as e:
        print(f"Caught expected error: {e}")

    # Case 4: Return type failure   
    # Let's create a quick function that lies about its return type.
    @validate_return_type(int)
    def returns_wrong():
        return "I am a string, not an int"

    try:
        print("\nAttempting invalid return type...")
        returns_wrong()
    except TypeError as e:
        print(f"Caught expected return error: {e}") 