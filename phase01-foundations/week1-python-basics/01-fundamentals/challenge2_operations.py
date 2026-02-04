"""
PROGRAM: Multi-Utility Operator & Logic Suite
---------------------------------------------
PURPOSE:
    A three-part challenge demonstrating advanced Python operators, 
    arithmetic logic, and conditional decision-making systems.

COMPONENTS:
    1. Shopping Cart: Financial arithmetic including tax and discounts.
    2. Number Analyser: Mathematical properties and modulo operations.
    3. Access Control: Complex boolean logic for security permissions.

REQUIREMENTS:
    - Input validation for numeric types.
    - Boolean conversion for string-based responses (yes/no).
    - Precise output formatting ($AUD and Boolean flags).
"""

def shopping_cart():
    # Part A: Financial calculation for retail transcations.
    print(f"\n{'[ PART A: Shopping Cart ]':^40}")

    try:
        price = float(input("Enter product price: $"))
        quantity = int(input("Enter quantity: "))
        tax_rate = float(input("Enter tax rate (%): "))
        discount_percentage = float(input("Enter discount percentage (%): "))

        # Calculations
        subtotal = price * quantity
        discount_amount = subtotal * (discount_percentage / 100)
        discounted_price = subtotal - discount_amount
        tax_amount = discounted_price * (tax_rate / 100)
        final_total = discounted_price + tax_amount

        # Formatting output
        print("\n" + "-" * 40)
        print(f"{'Receipt':^40}")
        print("-" * 40)

        print(f"{'Subtotal':<20} ${subtotal:,.2f}")
        print(f"{f'Discount ({discount_percentage}%)':<20} -${discount_amount:,.2f}")
        print(f"{f'Tax ({tax_rate}%)':<20} +${tax_amount:,.2f}")

        print("=" * 40)
        print(f"{'FINAL TOTAL':<20} ${final_total:,.2f}")

    except ValueError:
        print("Error: Invalid numeric input in Part A.")

def number_analyser():
    # Part B: Mathematical analysis of integer properties
    print(f"\n{'[ Part B: Number Analyser ]':^40}")

    try:
        num = int(input("Enter an integer number for analysis: "))

        #---- Determine properties -----
        positive_negative = "Positive" if num > 0 else "Negative" if num < 0 else "Zero"
        parity = "Even" if num % 2 == 0 else "Odd"

        div_3 = (num % 3 == 0)
        div_5 = (num % 5 == 0)
        div_both = div_3 and div_5
        remainder_7 = num % 7

        print(f"\nAnalysis for: {num}")
        print(f" - Classification: {positive_negative}")
        print(f" - Parity: {parity}")
        print(f" - Division by 3: {div_3}")
        print(f" - Division by 5: {div_5}")
        print(f" - Division by 3 and %: {div_both}")
        print(f" - Modulo 7: {remainder_7}")
    except ValueError:
        print("Error: Please enter a whole integer.")

def access_control ():
    # Part C: Boolean logic for security entry requirements
    print(f"\n{'[ Part C: Access Control System ]':^40}")

    try:
        age = int(input("Enter guest age: "))
        has_id = input("Possess valid ID? (yes/no): ").lower().strip() == 'yes'
        is_member = input("Club member status? (yes/no): ").lower().strip() == 'yes'
        with_member = input("Accompanying a member (yes/no): ").lower().strip() == 'yes'

        # Rule Definitions
        rule_adult = (age >= 21 and has_id)
        rule_membership = is_member
        rule_guest = (age >= 18 and has_id and with_member)

        print("\n" + "="*30)
        if rule_adult or rule_membership or rule_guest:
            print("STATUS: Access Granted")
            if rule_membership:
                print("REASON: Valid Membership.")
            elif rule_adult:
                print("REASON: Legal Age Requirement Met.")
            else:
                print("REASON: Verified Guest of Member")
        else:
            print("STATUS: Access Denied")
            print("REASON: Does not meet security criteria.")
    except ValueError:
        print("ERROR: Invalid age entry.")

def main():
    # Main execution flow
    print("=" * 45)
    print(f"{'OPERATIONS & LOGICAL CONDITIONS':^45}")
    print("=" * 45)

    shopping_cart()
    number_analyser()
    access_control()

    print("\n" + "=" * 45)
    print(f"{'All Challenges Complete':^45}")
    print("=" * 45)

if __name__ == "__main__":
    main()