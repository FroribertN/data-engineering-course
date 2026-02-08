"""
PROGRAM: Recursive Functions
-------------------------------

1. power(base, exponent)
   - Calculate base^exponent using recursion
   - Example: power(2, 3) → 8
   - Don't use ** operator

2. reverse_string(text)
   - Reverse a string using recursion
   - Example: reverse_string("hello") → "olleh"

3. count_digits(number)
   - Count digits in a number using recursion
   - Example: count_digits(12345) → 5

4. sum_range(start, end)
   - Sum all numbers from start to end (inclusive)
   - Example: sum_range(1, 5) → 15 (1+2+3+4+5)

5. gcd(a, b)
   - Find Greatest Common Divisor using Euclidean algorithm
   - Example: gcd(48, 18) → 6

6. flatten_list(nested_list)
   - Flatten a nested list
   - Example: flatten_list([1, [2, 3], [4, [5, 6]]]) → [1, 2, 3, 4, 5, 6]

7. binary_search(sorted_list, target, low=0, high=None)
   - Search for target in sorted list using recursion
   - Return index if found, -1 if not found
   - Example: binary_search([1, 3, 5, 7, 9], 5) → 2

8. print_triangle(n)
   - Print triangle pattern using recursion
   - Example: print_triangle(5)
     *
     **
     ***
     ****
     *****

Bonus: Add memoization to optimize your solutions!
"""
from functools import lru_cache

# 1. Power Function
@lru_cache(maxsize=None) # Bonus: Memoization
def power(base, exponent):
    """
    Calculates the power of a base to an exponent recursively.

    Args:
        base (int/float): The number to be multiplied.
        exponent (int): The power to raise the base to (must be >= 0)

    Returns:
        int/float: The result of the base raised to the exponent
    """
    # Base Case: Any numberr to the power of 0 is 1
    if exponent == 0:
        return 1
    # Recursive Step: b^e = b * b^(e-1)
    return base * power(base, exponent - 1)

# 2. String Reversal
def reverse_string(text):
    """
    Reverses a string using recursive slicing.

    Args:
        text (str): The string to reverse

    Returns:
        str: The reversed string
    """
    # Base Case: Empty string or single character
    if len(text) <= 1:
        return text
    # Recursive Step: Take the last character and add reversal of the rest
    return text[-1] + reverse_string(text[:-1])

# 3. Digital Counter
def count_digits(number):
    """
    Counts the number of digits in an integer recursively.  

    Args:
        number (int): The number to evaluate
    
    Returns:
        int: The number of digits
    """
    number = abs(number) # Handles negative numbers
    # Base Case: Single digit number
    if number < 10:
        return 1
    # Recursive Step: 1 + count of digits after removing the last one
    return 1 + count_digits(number // 10)

# 4. Range Summer
def sum_range(start, end):
    """
    Calculates the sum of all integers between start and end inclusive.

    Args:
        start (int): The starting integer
        end (int): The ending integer
    
    Returns:
        int: The cumulative sum
    """
    # Base Case: Start has met or exceeded end
    if start > end:
        return 0
    if start == end:
        return start
    # Recursive Step: current + sum of all the remaining range
    return start + sum_range(start + 1, end)

# 5. Greatest Common Divisor (GCD)
def gcd(a, b):
    """
    Finds the GCD of two numbers using Euclidean Algorithm.

    Args:
        a (int): First number
        b (int): Second number
    
    Returns:
        int: The greatest common divisor
    """
    # Base Case: When the remainder becomes 0
    if b == 0:
        return a
    # Recursive Step: gcd(a, b) = gcd(b, a % b)
    return gcd(b, a % b)

# 6. List Flattener
def flatten_list(nested_list):
    """
    Recursively flatterns a nested list of arbitrary depth.

    Args:
        nested_list (list): A list containing integers or other lists
    
    Returns:
        list: A single-level list of all elements
    """
    flat = []
    for item in nested_list:
        if isinstance(item, list):
            # Recursive Step: If item is a list, flatten it and extend
            flat.extend(flatten_list(item))
        else:
            flat.append(item)
    return flat

# 7. Binary Search
def binary_search(sorted_list, target, low=0, high=None):
    """
    Performs a recursive binary search of a sorted list.

    Args:
        sorted_list (list): The list to search through
        target: The value to find
        low (int): Lower index bound
        high (int): Upper index bound

    Returns:
        int: Index of target if found, else -1
    """
    if high is None:
        high = len(sorted_list) - 1

    # Base Case: Range is exhausted
    if low > high:
        return -1
    
    mid = (low + high) // 2

    if sorted_list[mid] == target:
        return mid
    elif sorted_list[mid] > target:
        # Recursive Step: Search lower half
        return binary_search(sorted_list, target, low, mid - 1)
    else:
        # Recursive Step: Search upper half
        return binary_search(sorted_list, target, mid + 1, high)
    
# 8. Triangle Printer
def print_triangle(n):
    """
    Prints a triangle pattern of stars recursively

    Args:
        n (int): The maximum width of the triangle
    """
    # Base Case: Nothing left to print
    if n > 0:
        # Recursive Step: Process smaller triangle first (for ascending order)
        print_triangle(n - 1)
        print("*" * n)

# ---------- TESTING ------------------
print(f"1. Power (2^3): {power(2, 3)}")
print(f"2. Reverse: {reverse_string('hello')}")
print(f"3. Digits: {count_digits(12345)}")
print(f"4. Sum (1-5): {sum_range(1, 5)}")
print(f"5. GCD (48, 18): {gcd(48, 18)}")
print(f"6. Flatten: {flatten_list([1, [2, 3], [4,[5, 6]]])}")

# 7. Binary Search
test_list = [1, 3, 5, 7, 9]
print(f"7. Binary Search (Index 5): {binary_search(test_list, 5)}")

# 8. Triangle
print("\n8. Triangle Pattern:")
print_triangle(8)