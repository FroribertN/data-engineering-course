"""
PROGRAM: Advanced Calculator with Menu
-----------------------------------------
Create a calculator program with:

MENU:
1. Basic Calculator (+, -, *, /, //, %, **)
2. Temperature Converter (C↔F↔K)
3. Area Calculator (Rectangle, Circle, Triangle)
4. Statistics Calculator (Mean, Median, Mode from list)
5. Factorial Calculator
6. Prime Number Checker
7. Fibonacci Sequence Generator
8. Exit

Requirements:
- Show menu in a loop
- Validate all inputs
- Use if/elif for menu choices
- Use for/while loops where appropriate
- Use break/continue appropriately
- Handle errors gracefully
- Format output nicely
"""

import math
import statistics

# --- MODULE 1: BASIC CALCULATOR ---
def basic_calculator():
    print("\n--- Basic Calculator ---")
    try:
        num1 = float(input("Enter first number: "))
        op = input("Enter operator (+, -, *, /, //, %, **): ").strip()
        num2 = float(input("Enter second number: "))

        if op == '+':   
            result = num1 + num2
        elif op == '-': 
            result = num1 - num2
        elif op == '*': 
            result = num1 * num2
        elif op == '/': 
            result = num1 / num2  if num2 != 0 else "Error: Division by zero"
        elif op == '//': 
            result = num1 // num2 if num2 != 0 else "Error: Division by zero"
        elif op == '%': 
            result = num1 % num2 if num2 != 0 else "Error: Division by zero"
        elif op == '**': 
            result = num1 ** num2
        else:
            print("Invalid operator.")
            return

        print(f"\nResult: {num1} {op} {num2} = {result}")
    except ValueError:
        print("ERROR: Please enter valid numbers.")

# --- MODULE 2: TEMPERATURE CONVERTER ---
def temp_converter():
    print("\n--- Temperature Converter ---")
    print("1. Celsius to Fahrenheit | 2. Fahrenheit to Celsius | 3. Celsius to Kelvin | 4. Kelvin to Celsius")
    choice = input("Select conversion: ")
    try:
        value = float(input("Enter value: "))
        if choice == '1':   
            print(f"{value}°C = {(value * 9/5) + 32:.2f}°F")
        elif choice == '2': 
            print(f"{value}°F = {(value - 32) * 5/9:.2f}°C")
        elif choice == '3': 
            print(f"{value}°C = {value + 273.15:.2f}K")
        elif choice == '4': 
            print(f"{value}K = {value - 273.15:.2f}°C")
    except ValueError:
        print("ERROR: Invalid numeric input.")

# --- MODULE 3: AREA CALCULATOR ---
def area_calculator():
    print("\n--- Area Calculator ---")
    print("1. Rectangle | 2. Circle | 3. Triangle")
    choice = input("Select shape: ")
    try:
        if choice == '1':
            length = float(input("Length: "))
            width = float(input("Width: "))
            print(f"Area: {length * width}")
        elif choice == '2':
            radius = float(input("Radius: "))
            print(f"Area: {math.pi * (radius**2):.2f}")
        elif choice == '3':
            base = float(input("Base: "))
            height = float(input("Height: "))
            print(f"Area: {0.5 * base * height}")
    except ValueError:
        print("ERROR: Invalid dimensions.")

# --- MODULE 4: STATISTICS CALCULATOR ---
def stats_calculator():
    print("\n--- Statistics Calculator ---")
    try:
        data = input("Enter numbers separated by spaces: ")
        num_list = [float(n) for n in data.split()]
        if not num_list: return

        print(f"Mean:   {statistics.mean(num_list):.2f}")
        print(f"Median: {statistics.median(num_list)}")
        try:
            print(f"Mode:   {statistics.mode(num_list)}")
        except statistics.StatisticsError:
            print("Mode:   No unique mode found")
    except ValueError:
        print("ERROR: List must contain numbers only.")

# --- MODULE 5: FACTORIAL CALCULATOR ---
def factorial_calc():
    try:
        number = int(input("Enter a positive integer: "))
        print(f"Result: {number}! = {math.factorial(number)}" if number >= 0 else "Must be positive.")
    except (ValueError, OverflowError):
        print("ERROR: Number too large or invalid.")

# --- MODULE 6: PRIME CHECKER ---
def prime_checker():
    try:
        number = int(input("Enter number to check: "))
        if number < 2:
            is_prime = False
        else:
            is_prime = True
            for i in range(2, int(number**0.5) + 1):
                if number % i == 0:
                    is_prime = False
                    break
        print(f"{number} is {'a Prime' if is_prime else 'not a Prime'}")
    except ValueError:
        print("ERROR: Enter an integer.")

# --- MODULE 7: FIBONACCI GENERATOR ---
def fibonacci_gen():
    try:
        count = int(input("How many Fibonacci numbers to generate? "))
        a, b = 0, 1
        series = []
        for _ in range(count):
            series.append(str(a))
            a, b = b, a + b
        print(", ".join(series))
    except ValueError:
        print("[!] Error: Enter an integer.")

# --- MAIN CONTROLLER ---
def main():
    while True:
        print("\n" + "="*30)
        print("ADVANCED CALCULATOR".center(30))
        print("="*30)
        print("1. Basic Calculator\n2. Temperature Converter\n3. Area Calculator")
        print("4. Statistics\n5. Factorial\n6. Prime Checker")
        print("7. Fibonacci Sequence\n8. Exit")
        
        choice = input("\nEnter choice (1-8): ").strip()

        if choice == '1': 
            basic_calculator()
        elif choice == '2':
            temp_converter()
        elif choice == '3': 
            area_calculator()
        elif choice == '4': 
            stats_calculator()
        elif choice == '5': 
            factorial_calc()
        elif choice == '6': 
            prime_checker()
        elif choice == '7': 
            fibonacci_gen()
        elif choice == '8':
            print("\nExiting. Thank you for using the calculator!")
            break
        else:
            print("Invalid selection. Try again.")
            continue

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()