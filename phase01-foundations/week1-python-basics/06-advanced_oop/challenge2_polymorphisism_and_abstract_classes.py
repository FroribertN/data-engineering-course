"""
PROGRAM: Polymorphism and Abstract Classes

Create an abstract payment system:

1. Payment (Abstract Base Class)
   - Abstract methods:
     - process_payment(amount)
     - validate()
     - get_receipt()
   - Concrete method:
     - record_transaction(amount)

2. CreditCardPayment (inherits Payment)
   - Attributes: card_number, cvv, expiry_date
   - Implement all abstract methods
   - Validate: check if card not expired

3. PayPalPayment (inherits Payment)
   - Attributes: email, password
   - Implement all abstract methods
   - Validate: check email format

4. CryptocurrencyPayment (inherits Payment)
   - Attributes: wallet_address, crypto_type
   - Implement all abstract methods
   - Validate: check wallet address length

5. PaymentProcessor
   - Method: process_payments(payments: List[Payment])
   - Should work with any payment type (polymorphism)

Test with different payment types!
"""

from abc import ABC, abstractmethod
from typing import List
from datetime import datetime

# ====================================
# 1. THE ABSTRACT BASE CLASS
# ====================================

class Payment(ABC):
    """
    Abstract Base Class for all payment methods.
    Forces all children to implement validation and processing
    """

    @abstractmethod
    def validate(self) -> bool:
        """Checks if the payment details are correct and valid"""
        pass

    @abstractmethod
    def payment_process(self, amount: float) -> bool:
        """Handles the actual transfer of funds."""
        pass

    @abstractmethod
    def get_receipt(self) -> str:
        """Returns a formatted receipt for the transaction."""
        pass

    def record_transaction(self, amount: float):
        """A concrete method shared by all payment types to log the action."""
        print(f"Internal log: Transaction of ${amount:,.2f} recorded at {datetime.now()}.")


# =======================================
# 2. THE CONCRETE CLASSES (The Children)
# =======================================

class CreditCardPayment(Payment):
    """Payment processing via Credit Card."""

    def __init__(self, card_number: str, cvv: str, expiry_date: datetime):
        self.card_number = card_number
        self.cvv = cvv
        self.expiry_date = expiry_date
        self._last_processed_amount = 0.0

    def validate(self):
        """Checks if the card is not expired."""
        return self.expiry_date > datetime.now()
    
    def payment_process(self, amount: float) -> bool:
        if self.validate():
            self._last_processed_amount = amount
            print(f"Charging Card Ending in {self.card_number[-4:]} for ${amount:,.2f}")
            return True
        return False
    
    def get_receipt(self) -> str:
        return f"RECEIPT: Credit Card Payment - ${self._last_processed_amount:,.2f}"
    

class PayPalPayment(Payment):
    """Payment processing via PayPal."""

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self._last_processed_amount = 0.0

    def validate(self):
        """Basic email format check."""
        return "@" in self.email and "." in self.email
    
    def payment_process(self, amount: float) -> bool:
        if self.validate():
            self._last_processed_amount = amount
            print(f"PayPal transfer: ${amount:,.2f} from {self.email}")
            return True
        return False
    
    def get_receipt(self) -> str:
        return f"RECEIPT: PayPal Payment ({self.email} - ${self._last_processed_amount:,.2f}"
    

class CryptocurrencyPayment(Payment):
    """Payment processing via Crypto Wallet."""

    def __init__(self, wallet_address: str, crypto_type: str):
        self.wallet_address = wallet_address
        self.crypto_type = crypto_type
        self._last_processed_amount = 0.0

    def validate(self):
        """Checks if the wallet address length is valid (typically more than 20)."""
        return len(self.wallet_address) > 20
    
    def payment_process(self, amount: float) -> bool:
        if self.validate():
            self._last_processed_amount = amount
            print(f"Mining {self.crypto_type} Transaction: ${amount:,.2f} to {self.wallet_address[:8]}...")
            return True
        return False
    
    def get_receipt(self) -> str:
        return f"RECEIPT: {self.crypto_type} Payment - ${self._last_processed_amount:,.2f}"
    

# =======================================
# 3. THE PAYMENT PROCESSOR (Polymorphism)
# =======================================

class PaymentProcessor:
    """Manager class that handle multiple payments regardless of their type."""
    def execute_payments(self, payment_list: List[dict]):
        """
        Processes a list of payment tasks.
        Each task should be a dict: {'amount': float, 'method', PaymentObject}
        """

        print(f"\n{'=' * 15} STARTING BATCH PROCESSING {'=' * 15}")
        for task in payment_list:
            method = task['method']
            amount = task['amount']

            if method.payment_process(amount):
                method.record_transaction(amount)
                print(method.get_receipt())
            else:
                print(f"Transaction Failed: Details invalid for{type(method).__name__}")
            print('-' * 80)


# =======================================
#              TESTING
# =======================================

# 1. Setup Payment Methods
card = CreditCardPayment("4111222233334444", "123", datetime(2030, 1, 1))
paypal = PayPalPayment("user@example.com", "secret123")
crypto = CryptocurrencyPayment("0x71C7656EC7ab88b098defB751B7401B5f6d8976F", "Ethereum")

# 2. Create a batch of transactions
transactions = [
    {"amount": 150.00, "method": card},
    {"amount": 45.50, "method": paypal},
    {"amount": 1200.00, "method": crypto}
]

# 3. Process them all at once!
processor = PaymentProcessor()
processor.execute_payments(transactions)