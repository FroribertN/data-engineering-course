"""
PROGRAM: Multiplication Table Generator
---------------------------------------
PURPOSE:
    A mathematical utility to generate targeted multiplication series 
    and comprehensive product grids for educational purposes.

OBJECTIVES:
    1. Single Table (Part A): Ask for a base number and row count 
    to display a specific multiplication sequence.
    2. Product Grid (Part B): Generate a 2D multiplication matrix 
    showing products for all numbers up to the chosen limit.
    
REQUIREMENTS & CONSTRAINTS:
    - Input Validation: Ensure all user entries are between 1 and 20.
    - Professional Formatting: Align columns using string padding 
    for a clean, table-like appearance.
    - Visual Enhancement: Apply ANSI color codes to distinguish 
    headers from data.
"""
import sys

# --- ANSI COLOR CODES ---
HEADER_COLOR = "\033[95m"
SUCCESS_COLOR = "\033[92m"
ERROR_COLOR = "\033[91m"
RESET = "\033[0m"

# Header Display
print("=" * 60)
print(f"{HEADER_COLOR}MATHEMATICAL MATRIX GENERATOR{RESET}".center(60))
print("=" * 60)

try:
    # 1. DATA COLLECTION
    target_number = int(input("Enter base number (1-20): "))
    total_rows = int(input("Enter number of rows (1-20): "))

    # 2. INPUT VALIDATION
    if not (1 <= target_number <= 20 and 1 <= total_rows <= 20):
        print(f"{ERROR_COLOR}[!] LIMIT ERROR: Inputs must be between 1 and 20.{RESET}")
        sys.exit()

    # --- PART A: TARGETED MULTIPLICATION TABLE ---
    print(f"\n{SUCCESS_COLOR}[ PART A: TABLE FOR {target_number} ]{RESET}")
    print("-" * 30)
    for multiplier in range(1, total_rows + 1):
        product = target_number * multiplier
        # Padding applied to multiplier (:2) and product (:3) for alignment
        print(f"{target_number} x {multiplier:>2} = {product:>3}")
    print("-" * 30)

    # --- PART B: FULL MULTIPLICATION GRID ---
    print(f"\n{SUCCESS_COLOR}[ PART B: {target_number}x{target_number} PRODUCT GRID ]{RESET}")
    
    # Generate Header Row
    print("    ", end="") # Top-left corner gap
    for column_header in range(1, target_number + 1):
        print(f"{column_header:>4}", end="")
    print(f"\n" + "    " + "----" * target_number)

    # Generate Grid Rows using Nested Loops
    # The outer loop handles the vertical rows
    for row_val in range(1, target_number + 1):
        # Print the side header (vertical index)
        print(f"{row_val:>2} |", end="")
        
        # The inner loop handles the horizontal columns
        for col_val in range(1, target_number + 1):
            cell_product = row_val * col_val
            # :4 padding ensures columns stay straight regardless of digit count
            print(f"{cell_product:>4}", end="")
        
        # New line after each row is finished
        print()

except ValueError:
    print(f"{ERROR_COLOR}[!] INPUT ERROR: Please enter valid integers only.{RESET}")

print("\n" + "=" * 60)
print("UTILITY OPERATION COMPLETE".center(60))
print("=" * 60)