"""
PROGRAM: Pattern Printing with Nested Loops
---------------------------------
PURPOSE:
    A geometric rendering tool that uses nested iteration to 
    generate structural patterns and mathematical grids.

OBJECTIVES:
    - Implement varied nested loop structures (incremental and decremental).
    - Apply mathematical spacing for symmetrical shapes (Pyramids/Diamonds).
    - Reintegrate the Matrix Grid logic from previous modules.
    - Provide a persistent user interface for iterative pattern generation.
"""

import sys

def print_right_triangle(size):
    for row in range(1, size + 1):
        print("*" * row)

def print_inverted_triangle(size):
    for row in range(size, 0, -1):
        print("*" * row)

def print_pyramid(size):
    for row in range(1, size + 1):
        # Calculate leading spaces and star count (2n - 1)
        spaces = " " * (size - row)
        stars = "*" * (2 * row - 1)
        print(f"{spaces}{stars}")

def print_diamond(size):
    # Top half (including middle)
    for row in range(1, size + 1):
        print(" " * (size - row) + "*" * (2 * row - 1))
    # Bottom half
    for row in range(size - 1, 0, -1):
        print(" " * (size - row) + "*" * (2 * row - 1))

def print_number_triangle(size):
    for row in range(1, size + 1):
        for col in range(1, row + 1):
            print(col, end="")
        print() # Move to next line

def print_multiplication_grid(size):
    # Horizontal Header
    print("    ", end="")
    for i in range(1, size + 1):
        print(f"{i:>4}", end="")
    print(f"\n" + "    " + "----" * size)
    
    # Grid Logic
    for row in range(1, size + 1):
        print(f"{row:>2} |", end="")
        for col in range(1, size + 1):
            print(f"{row * col:>4}", end="")
        print()

def main():
    while True:
        print("\n" + "=" * 50)
        print("VISUAL PATTERN ARCHITECT".center(50))
        print("=" * 50)
        print("1. Right Triangle\n2. Inverted Triangle\n3. Pyramid")
        print("4. Diamond\n5. Number Triangle\n6. Multiplication Grid\n7. Exit")
        
        try:
            choice = input("\nSelect Pattern (1-7): ").strip()
            if choice == '7': 
                print("Closing Architect. Goodbye!")
                break
                
            size = int(input("Enter size/magnitude: "))
            print("\nGenerating Output:\n")

            if choice == '1':
                print_right_triangle(size)
            elif choice == '2': 
                print_inverted_triangle(size)
            elif choice == '3': 
                print_pyramid(size)
            elif choice == '4': 
                print_diamond(size)
            elif choice == '5': 
                print_number_triangle(size)
            elif choice == '6': 
                print_multiplication_grid(size)
            else: 
                print("[!] Selection out of range.")

        except ValueError:
            print("ERROR: Please enter a valid numeric size.")

        if input("\nPrint another pattern? (yes/no): ").lower().strip() != "yes":
            break

if __name__ == "__main__":
    main()