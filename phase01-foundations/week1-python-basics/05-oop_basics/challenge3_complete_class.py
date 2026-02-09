"""
PROGRAM: Product Inventory System
-----------------------------------

Create a Product class for an inventory management system.

Requirements:

Class: Product
--------------
Attributes:
- name: Product name
- sku: Stock keeping unit (unique identifier)
- price: Product price
- quantity: Number in stock
- category: Product category

Class Variables:
- total_products: Count of products created
- categories: Set of all unique categories

Methods:
- restock(amount): Add to quantity
- sell(amount): Reduce quantity (check if enough stock)
- apply_discount(percentage): Reduce price by percentage
- get_value(): Return total value (price * quantity)
- is_in_stock(): Return True if quantity > 0
- is_low_stock(threshold=10): Return True if quantity < threshold

Properties:
- stock_status: Return "In Stock", "Low Stock", or "Out of Stock"

String Representation:
- __str__: User-friendly display
- __repr__: Developer representation

Class Methods (BONUS):
- get_all_categories(): Return list of all categories
- count_products(): Return total products created

Test your class thoroughly!
"""

class Product:
    """
    Represents a product in an inventory management system.
    """
    total_products = 0
    categories = set()

    def __init__(self, name: str, sku: str, price: float, quantity: int, category: str):
        self.name = name
        self.sku = sku
        self.price = price
        self.quantity = quantity
        self.category = category

        # Update class-level tracking
        Product.total_products += 1
        Product.categories.add(category)
    
    def restock(self, amount: int):
        """Adds the specified amount to the current stock quantity."""
        self.quantity += amount

    def sell(self, amount: int) -> bool:
        """
        Reduces quantity if enough stock exists.
        Returns True if successful, False otherwise
        """
        if amount <= self.quantity:
            self.quantity -= amount
            return True
        print(f"ERROR: Not enough stock for {self.name} to sell {amount}")
        return False
    
    def apply_discount(self, percentage: float):
        """Reduces the product price by a given percentage."""
        self.price -= self.price * (percentage / 100)

    def get_value(self) -> bool:
        """Calculates the total monetary value of the current stock"""
        return self.price * self.quantity
    
    def is_in_stock(self) -> bool:
        """Returns True if there iis a leat one item in stock."""
        return self.quantity > 0
    
    def is_low_stock(self, threshold: int = 10) -> bool:
        """Returns True if quantity falls below the given threshold."""
        return self.quantity < threshold
    
    @property
    def stock_status(self)-> str:
        """Returns a string describing the current inventory levels."""
        if self.quantity <= 0:
            return "Out of Stock"
        elif self.is_low_stock():
            return "Low Stock"
        else:
            return "In Stock"
    
    def __str__(self) -> str:
        """User-friendly display string."""
        return f"[{self.sku}] {self.name} ({self.category}) - ${self.price:,.2f}"
    
    def __repr__(self) -> str:
        """Developer-focused representation."""
        return f"Product(name='{self.name}', sku='{self.sku}', price={self.price}, quantity={self.quantity}, category='{self.category}')"
    
    @classmethod
    def get_all_categories(cls) -> list:
        """Returns a list of all unique categories across all products."""
        return list(cls.categories)
    
    @classmethod
    def count_products(cls) -> int:
        """Returns the total number of Product instances created."""
        return cls.total_products
    

# ====================
# TESTING
# ====================

# 1. Initialization and Class variables
print("\n======= 1. INVENTORY INITIALIZATION =======")
laptop = Product("Laptop", "LP001", 1000.00, 50, "Electronics")
phone = Product("Phone", "PH001", 500.00, 5, "Electronics")
desk = Product("Desk", "DK001", 200.00, 0, "Furniture")

print(f"Total Products Created:     {Product.count_products()}")
print(f"Unique Categories:          {Product.get_all_categories()}")

# 2. Stock Management and Properties
print("\n======= 2. STOCK LOGIC & PROPERTIES =======")
print(f"Desk Status (Initial 0):    {desk.stock_status}") # Out of Stock

phone.sell(2) # 5 -> 3
print(f"Phone Status (Qty 3):       {phone.stock_status}") # Low Stock (Threshold is 10)

laptop.sell(10) # 50 -> 40
print(f"Laptop Status (Qty 40):     {laptop.stock_status}") # In Stock

# 3. Financial Calculations
print("\n======= 3. FINANCIAL LOGIC =======")
print(f"Laptop Value Before Discount:     ${laptop.get_value():,.2f}")
laptop.apply_discount(10) #10% off $1,000 -> $900
print(f"Laptop Price After 10% Discount:  ${laptop.price:,.2f}")
print(f"New Laptop Value (Qty 40):        ${laptop.get_value():,.2f}")

# 4. REPRESENTATIONS
print("\n======= 4. STRING REPRESENTATIONS =======")
print(f"__str__: {laptop}")
print(f"__repr__:  {repr(laptop)}")



