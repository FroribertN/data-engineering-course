"""
PROGRAM: Advanced Function Features
------------------------------------

1. create_greeting(name, greeting="Hello", punctuation="!")
   - Create a customizable greeting
   - Use default parameters
   - Example: create_greeting("Alice") → "Hello, Alice!"
   - Example: create_greeting("Bob", "Hi", ".") → "Hi, Bob."

2. calculate_stats(numbers, include_median=False)
   - Calculate statistics for a list of numbers
   - Always return: mean, min, max
   - If include_median=True, also return median
   - Return as a dictionary
   - Handle empty list

3. format_name(first, last, middle=None, title=None)
   - Format a person's name
   - Example: format_name("John", "Doe") → "John Doe"
   - Example: format_name("John", "Doe", "Smith") → "John Smith Doe"
   - Example: format_name("John", "Doe", title="Dr.") → "Dr. John Doe"
   - Example: format_name("John", "Doe", "Smith", "Dr.") → "Dr. John Smith Doe"

4. validate_email(email, strict=False)
   - Validate email address
   - Basic: Must contain @ and a dot after @
   - If strict=True: Also check no spaces, valid domain
   - Return True/False

5. build_profile(**kwargs)
   - Accept any number of keyword arguments
   - Build and return a profile dictionary
   - Example: build_profile(name="Alice", age=25, city="Sydney")
   - Should handle any keys passed

6. apply_operation(numbers, operation="sum")
   - Apply different operations to a list
   - Operations: "sum", "product", "max", "min", "average"
   - Use default parameter
   - Return the result

Write comprehensive docstrings for each function!
"""
def header(title):
    print("\n" + "=" * 75)
    print(title.center(75))
    print("=" * 75)

def seperator():
    print("-" * 75)

# 1. Customizable Greeting with Default Parameters
def create_greating(name, greeting = "Hello", punctuation = "!"):
    """ 
    Create a personalized greeting string.

    Args:
        name (str): The name of the person to greet.
        greeting (str): The opening salutation. Defaults to "Hello".
        punctuation (str): The ending punctuation. Defaults to "!".
    
    Returns:
        str: The combined greeting (e.g., "Hello, Alice!")
    """
    return f"{greeting}, {name}{punctuation}"

# 2. Stats Calculator returning a Dictionary 
def calculate_stats(numbers, include_median = False):
    """
    Calculates statistical metrics for a list of numbers

    Args:
        numbers(list): A list of integers or floats.
        include_median (bool): Whether to calculate the median. Defaults to False.

    Returns:
        dict: A dictionary containing 'mean', 'min', 'max', and optionally 'median'.
              Returns None if list is empty.
    """
    if not numbers:
        return None
    stats = {
        "mean": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers)
    }

    if include_median:
        sorted_nums = sorted(numbers)
        nums = len(sorted_nums)
        mid = nums // 2

        if nums % 2 == 0 :
            median = (sorted_nums)[mid-1]  + sorted_nums[mid] / 2
        else:
            median = sorted_nums[mid]
        stats["median"] = median
    return stats

# 3. Name Formatter with Optional Middle and Title 
def format_name(first, last, middle=None, title=None):
    """
    Constructs a full name string based on provided components

    Args:
        first (str): First name
        last (str): Last name
        middle (str, optional): Middle name
        title (str,optional): Prefix (e.g., Mr., Ms., Dr.)
    
    Returns:
        str: Properly spaced full name
    """
    parts = []
    if title:
        parts.append(title)
    parts.append(first)
    
    if middle:
        parts.append(middle)
    parts.append(last)

    return " ".join(parts)

# 4. Email Validator (Basic vs Strict)
def validate_email(email, strict=False):
    """
    Checks if a string follows standard email formatting.

    Args:
        email (str): The string to validate.
        strict (bool): If True, checks for spaces and valid domain suffix.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    if "@" not in email:
        return False
    
    # Check that there is at least one dot after the @
    parts = email.split("@")
    if len(parts) != 2 or "." not in parts[1]:
        return False
    
    if strict:
        if " " in email:
            return False
        if len(parts[1].split(".")[1]) < 2: # Domain extension check (e.g., .com)
            return False
        
    return True

# 5. Profile Builder using Keyword Arguements (**kwargs)
def build_profile(**kwargs):
    """
    Dynamically captures user data into a profiile dictionary.

    Args:
        **kwargs: Arbitrary keyword arguements (e.g., age = 30, job = "Engineer")
    
    Returns:
        dict: A dictionary containing all passed keyword arguements
    """
    return kwargs

# 6. Operation Applicator (The "Swiss Army Knife")
def apply_operation(numbers, operation="sum"):
    """
    Performs a mathematical operation on a list of numbers.

    Args:
        numbers (list): List of numeric values
        operation (str): "sum", "product", "max", "min", or "average".
    
    Returns:
        Float/int: Result of the calculation
    """
    if not numbers:
        return 0
    
    if operation == "sum".lower():
        return sum(numbers)
    elif operation == "max".lower():
        return max(numbers)
    elif operation == "min".lower():
        return min(numbers)
    elif operation == "average".lower():
        return sum(numbers) / len(numbers)
    elif operation == "product".lower():
        result = 1
        for number in numbers:
            result *= number
    else:
        return "Invalid Operation"
    
# --------- TESTING THE FUNCTIONS -------------
header("1. GREETINGS")
print(create_greating("Alice"))
print(create_greating("Bob", "Hi", "."))

seperator()

header("2. STATS")
data = [10, 20, 30, 40]
print(f"Basic Stats: {calculate_stats(data)}")
print(f"With Median: {calculate_stats(data, include_median = True)}")

seperator()

header("3. NAME FORMATTING")
print(format_name("John", "Newton"))
print(format_name("George", "Doe", title = "Dr."))
print(format_name("George", "Doe", "Smith", "Dr."))

seperator()

header("4. EMAIL VALIDATION")
print(f"Is 'test@me valid? {validate_email('test@me')}")
print(f"Is 'test@me.com' valid? {validate_email('test@me.com')}")

seperator()

header("5. BUILD PROFILE")
user_profile = build_profile(name = "Sarah", age = 31, role = "Engineer", location = "Berlin")
print(user_profile)

seperator()

header("6. OPERATIONS")
nums = [2, 4, 6]
print(f"Sum: {apply_operation(nums)}")
print(f"Average: {apply_operation(nums, 'average')}")
