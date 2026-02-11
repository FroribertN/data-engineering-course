"""
PROGRAM: Advanced OOP - Magic Methods and Class Methods

Create a Money class with advanced features:

1. Money class
   - Attributes: amount, currency
   - Magic methods to implement:
     - __add__: Add money (must be same currency)
     - __sub__: Subtract money
     - __mul__: Multiply by a number
     - __eq__, __lt__, __gt__: Comparisons
     - __str__: Display as "$100.00 USD"
     - __repr__: Developer representation
     - __bool__: True if amount > 0
   
   - Class methods:
     - from_string(cls, string): Create from "$100 USD"
     - get_exchange_rate(currency1, currency2): Return exchange rate
   
   - Static methods:
     - validate_currency(currency): Check if valid currency code
     - format_amount(amount): Format with 2 decimals
   
   - Instance methods:
     - convert_to(currency): Convert to another currency
     - add_interest(rate): Add interest percentage

Test all functionality!
"""

from __future__ import annotations
import re

class Money:
    """
    A robust Money class handling currency validation, arithmetic,  and exchange conversions.
    """
    
    # Mock exchange rate for demonstration purposes
    EXCHANGE_RATES =  {
        ("USD", "EUR"): 0.84,
        ("EUR", "USD"): 1.19,
        ("USD", "GBP"): 0.73,
        ("GBP", "USD"): 1.37 
    }

    def __init__(self, amount: float, currency: str):
        if not self.validate_currency(currency):
            raise ValueError(f"Invalid currency code: {currency}")
        
        self.amount = float(amount)
        self.currency = currency.upper()

    # ------------------ Magic Methods (Operator Overloading) ------------------
    
    def __add__(self, other: Money) -> Money:
        """Add two Money instances. Must be the same currency."""
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise TypeError("Cannot add different currencies. Convert first.")
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: Money) -> Money:
        """Subtracts two Money instances. Must be the same currency."""
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise TypeError("Cannot subtract different currenciees.")
        return Money(self.amount - other.amount, self.currency)
    
    def __mul__(self, scalar: float) -> float:
        """Multiplies money by a numeric scalar value."""
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Money(self.amount * scalar, self.currency)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
    
    def __lt__(self, other: Money) -> bool:
        if self.currency != other.currency:
            raise TypeError("Comparisons required identical currencies.")
        return self.amount  < other.amount
    
    def __gt__(self, other: Money) -> bool:
        if self.currency != other.currency:
            raise TypeError("Comparisons require identical currencies.")
        return self.amount > other.amount
    
    def __bool__(self) -> bool:
        """Returns True if the amount is positive."""
        return self.amount > 0
    
    def __str__(self) -> str:
        """User-friendly representanion: $100.00 USD."""
        symbol = "$" if self.currency == "USD" else ""
        return f"{symbol}{self.format_amount(self.amount)} {self.currency}"
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Money(amount={self.amount}, currency='{self.currency}')"
    

    # ------------------ Class Methods (Factories) ------------------
    @classmethod
    def from_string(cls, data_string: str) -> Money:
        """
        Creates an instance from a string like '$100.50 USD'.
        Uses regex to extract numeric and apha components.
        """
        # Regex finds the number (including decimals) and the 3-letter currency code
        match = re.search(r"(\d+\.?\d*)\s*([A-Z]{3})", data_string.upper())
        if not match:
            raise ValueError("String format must be 'Amount CUR' (e.g., '100.00 USD')")
        
        amount, currency = match.groups()
        return cls(float(amount), currency)
    
    @classmethod
    def get_exchange_rate(cls, c1: str, c2: str) -> float:
        """Fetches the rate between two currencies."""
        if c1 == c2:
            return 1.0
        return cls.EXCHANGE_RATES.get((c1.upper(), c2.upper()), 1.0)
    

    # ------------------ Static Methods (Utilities) ------------------
    @staticmethod
    def validate_currency(currency: int) -> bool:
        """Checks if the currency is a standard 3-letter ISO-like code."""
        return isinstance(currency, str) and len(currency) == 3
    
    @staticmethod
    def format_amount(amount: float) -> str:
        """Formats a float to two decimal places."""
        return f"{amount:,.2f}"
    

    # ------------------ Instance Methods ------------------
    def convert_to(self, target_currency: str) -> Money:
        """Converts the current amount to a target currency."""
        rate = self.get_exchange_rate(self.currency, target_currency)
        new_amount = self.amount * rate
        return Money(new_amount, target_currency)
    
    def add_interest(self, rate_percentage: float):
        """
        Applies interest rate to the balance.
        Formula: $$A = P(1 + r) $$
        """
        self.amount *= (1 + rate_percentage /100)


# ------------------ TESTING ------------------

def run_tests():
    print("\n--- 1. Initialization & String Formatting ---")
    m1 = Money(100, "USD")
    m2 = Money(50, "USD")
    m3 = Money.from_string("$75.50 EUR")
    print(f"m1: {m1}")
    print(f"m3 (from string): {m3}")

    print("\n--- 2. Arithmetic (Magic Methods) ---")
    combined = m1 + m2
    print(f"Addition: {m1} + {m2} = {combined}")
    
    doubled = m1 * 2
    print(f"Multiplication: {m1} * 2 = {doubled}")

    print("\n--- 3. Comparisons & Booleans ---")
    print(f"Is {m1} > {m2}?: {m1 > m2}")
    print(f"Is m1 empty?: {not bool(m1)}")

    print("\n--- 4. Conversion & Interest ---")
    euro_ver = m1.convert_to("EUR")
    print(f"Convert {m1} to EUR: {euro_ver}")
    
    m1.add_interest(5) # 5% interest
    print(f"m1 after 5% interest: {m1}")

    print("\n--- 5. Error Handling ---")
    try:
        m1 + m3 # Different currencies
    except TypeError as e:
        print(f"Caught expected error: {e}")

run_tests()