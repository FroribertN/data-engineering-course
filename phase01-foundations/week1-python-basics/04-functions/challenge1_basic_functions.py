"""
PROGRAM: Basic Function Practice

Create the following functions:

1. calculate_rectangle_area(length, width)
   - Returns the area of a rectangle
   - Formula: length x width

2. calculate_circle_area(radius)
   - Returns the area of a circle
   - Formula: π x radius²
   - Use 3.14159 for π

3. celsius_to_fahrenheit(celsius)
   - Converts Celsius to Fahrenheit
   - Formula: (C x 9/5) + 32

4. is_even(number)
   - Returns True if number is even, False if odd

5. find_maximum(a, b, c)
   - Returns the largest of three numbers

6. calculate_average(numbers)
   - Takes a list of numbers
   - Returns the average
   - Handle empty list (return 0)

7. count_vowels(text)
   - Count vowels (a, e, i, o, u) in a string
   - Case-insensitive
   - Return the count

8. reverse_string(text)
   - Return the reversed string
   - Example: "hello" → "olleh"

Test each function with different inputs!

"""
def header(title):
    print("\n" + "=" * 40)
    print(title.center(40))
    print("=" * 40)

def seperator():
    print("-" * 30)

# 1. Rectangle Area
def calculate_rectangle_area(length, width):
    return length * width

# 2.Circle Area
def calculate_circle_area(radius):
    return 3.14159 * radius ** 2

# 3. Celsius to Fahrenheit
def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

# 4. Is Even 
def is_even(number):
    # Returns True if remainder of division by 2 is 0
    return number % 2 == 0

# 5. Find Maximum
def find_maximum(a, b, c):
    return max(a, b, c)

# 6. Calculate Average
def calculate_average(numbers):
    if not numbers: # Check if the list is empty first to avoid division by zero
        return 0
    return sum(numbers) / len(numbers)

# 7. Count Vowels
def count_vowels(text):
    vowels = "aeiou"
    count = 0
    # Convert to lower case to make it case-insensitive
    for char in text.lower():
        if char in vowels:
            count += 1
    return count

# 8. Reverse String
def reverse_string(text):
    # Using string slicing [start:stop:step] with a step of -1
    return text[::-1]

"""
================ Calling functions ======================
"""
header("BASIC FUNCTIONS TEST")

# Testing Math Functions
print(f"Rectangle Area (5x10): {calculate_rectangle_area(5, 10)}")
print(f"Circle Area (r=3):     {calculate_circle_area(3):.2f}")
print(f"Temp (25°C to F):      {celsius_to_fahrenheit(25)}°F")

seperator()

# Testing String Manipulation
sample_text = "Hello World"
print(f"Vowels in '{sample_text}':  {count_vowels(sample_text)}")
print(f"Reverse '{sample_text}':    {reverse_string(sample_text)}")

header("TESTING COMPLETE")