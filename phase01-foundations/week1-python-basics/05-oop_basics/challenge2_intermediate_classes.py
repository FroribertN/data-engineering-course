"""
PROGRAM: Classes with Methods and Properties
----------------------------------------------

1. Book
   - Attributes: title, author, pages, current_page (starts at 0)
   - Methods:
     - read(pages): advance current_page
     - get_progress(): return percentage of book read
     - is_finished(): return True if finished
     - reset(): go back to page 0
   - String representation

2. ShoppingCart
   - Attributes: items (list of dicts with 'name', 'price', 'quantity')
   - Methods:
     - add_item(name, price, quantity=1)
     - remove_item(name)
     - update_quantity(name, quantity)
     - get_total(): return total cost
     - get_item_count(): return total number of items
     - clear(): remove all items
   - Use @property for total

3. Counter
   - Attributes: _count (private, starts at 0)
   - Methods:
     - increment(amount=1): increase count
     - decrement(amount=1): decrease count
     - reset(): set to 0
   - Properties:
     - count (read-only): return current count
   - Class variable: total_counters (count how many created)

Test all functionality!
"""

# 1. Book Class
class Book:
    """
    Represents a book with progress tracking.

    Attributes:
        title (str): The name of the book
        author (str): The book's author
        pages (int): Total number of pages
        current_page (int): The page the reader is currently on
    """
    def __init__(self, title: str, author: str, pages: int):
        self.title = title
        self.author = author
        self.pages = pages
        self.current_page = 0

    def read(self, pages: int):
        """Advances current_page by a given amount, capped at total pages."""
        self.current_page = min(self.current_page + pages, self.pages)
    
    def get_progress(self) -> float:
        """Calculates percentage of the book read."""
        return (self.current_page / self.pages) * 100
    
    def is_finished(self) -> bool:
        """Checks if the current page has reached the end of the book."""
        return self.current_page >= self.pages
    
    def reset(self):
        """Returns the current_page to 0."""
        self.current_page = 0

    def __str__(self):
        """Returns a user-friendly description of the reading progress."""
        return f"'{self.title}' by {self.author} ({self.current_page} / {self.pages} pages)"


# 2. The ShoppingCart Class
class ShoppingCart:
    """
    Manages a collection of items to be purchased.

    Attributes:
        items (list): A list of dictionaries, each containing name, price and quantity.
    """
    def __init__(self):
        self.items = []
    
    def add_item(self, name: str, price: float, quantity: int = 1):
        """Adds a new item or update the quantity of an existing item."""
        for item in self.items:
            if item['name'] == name:
                item['quantity'] += quantity
                return
        self.items.append({'name': name, 'price': price, 'quantity': quantity})

    def remove_item (self, name: str):
        """Removes all instances of an item by name."""
        self.items = [item for item in self.items if item['name'] != name]

    def update_quantity(self, name: str, quantity: str):
        """Changes the quantity for a specific item name."""
        for item in self.items:
            if item['name'] == name:
                item['quantity'] = quantity
    
    @property
    def total(self) -> float:
        """Calculates the total cost of all items in the cart (Ready-only)."""
        return sum(item['price'] * item['quantity'] for item in self.items)
    
    def get_item_count(self) -> int:
        """Returns the sum of all item quantities in the cart."""
        return sum(item['quantity'] for item in self.items)
    
    def clear(self):
        """Wipes all items from the cart."""
        self.items = []

    
# 3. Counter Class
class Counter:
    """
    An object-oriented counter with global instance tracking.

    Class Attributes:
        total_counters (int): Tracks the number of Counter instances created.

    Attributes:
        _count (int): The protected value of the individual counter
    """
    total_counters = 0

    def __init__(self):
        self._count = 0
        Counter.total_counters += 1

    def increment(self, amount: int = 1):
        """Increases the counter value by a specified amount."""
        self._count += amount

    def decrement(self, amount: int = 1):
        """Decreases the counter value by a specified amount."""
        self._count -= 1

    def reset(self):
        """Resets the individual counter to 0."""
        self._count = 0
    
    @property
    def count(self) -> bool:
        """Provides read-only access to the protected _acount attribute."""
        return self._count
    

# =================================================================
# TEST SETUP
# =================================================================

def run_test_header(title):
    print(f"\n{'='*20} {title} {'='*20}")

# =================================================================
# 1. BOOK CLASS TESTS
# =================================================================
run_test_header("TESTING BOOK")

my_book = Book("The Great Gatsby", "F. Scott Fitzgerald", 180)
print(f"Created: {my_book}")

# Test Reading
my_book.read(50)
print(f"Read 50 pages. Progress: {my_book.get_progress():.1f}%")

# Test Overflow Prevention (Reading more pages than exist)
my_book.read(200)
print(f"Read 200 more. Current Page: {my_book.current_page} (Capped at {my_book.pages})")
print(f"Finished? {my_book.is_finished()}")

# Test Reset
my_book.reset()
print(f"Resetting... Current Page: {my_book.current_page}")


# =================================================================
# 2. SHOPPING CART TESTS
# =================================================================
run_test_header("TESTING SHOPPING CART")

cart = ShoppingCart()

# Test Adding Items
cart.add_item("Laptop", 1200.0, 1)
cart.add_item("Mouse", 25.0, 2)
print(f"Added Laptop ($1200) and 2 Mice ($25 each).")
print(f"Total Property: ${cart.total}") # Testing @property
print(f"Item Count: {cart.get_item_count()}")

# Test Updating Quantity
cart.update_quantity("Mouse", 5)
print(f"Updated Mice to 5. New Total: ${cart.total}")

# Test Removing Item
cart.remove_item("Laptop")
print(f"Removed Laptop. New Total: ${cart.total}")


# =================================================================
# 3. COUNTER TESTS
# =================================================================
run_test_header("TESTING COUNTER")

# Reset class variable for clean testing if needed
# Counter.total_counters = 0 

c1 = Counter()
c2 = Counter()

print(f"Initial Counter 1 value: {c1.count}")

# Test Increment/Decrement
c1.increment(10)
c1.decrement(3)
print(f"Counter 1 after +10 and -3: {c1.count}")

# Test Read-Only Property (Should fail if we try to set it)
try:
    c1.count = 20
except AttributeError:
    print("Success: count property is read-only.")

# Test Class Variable (Shared State)
print(f"Total Counter objects created: {Counter.total_counters}")

print(f"\n{'='*15} ALL TESTS COMPLETED {'='*15}")