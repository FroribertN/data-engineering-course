"""
PROGRAM: Data Analysis with List Comprehensions
------------------------------------------------
You have data about products in a store:

products = [
    {"name": "Laptop", "price": 999, "category": "Electronics", "stock": 15},
    {"name": "Phone", "price": 699, "category": "Electronics", "stock": 25},
    {"name": "Desk", "price": 299, "category": "Furniture", "stock": 8},
    {"name": "Chair", "price": 149, "category": "Furniture", "stock": 20},
    {"name": "Monitor", "price": 399, "category": "Electronics", "stock": 12},
    {"name": "Keyboard", "price": 79, "category": "Electronics", "stock": 30},
    {"name": "Mouse", "price": 29, "category": "Electronics", "stock": 50},
    {"name": "Bookshelf", "price": 189, "category": "Furniture", "stock": 5},
]

Using list comprehensions, create:
1. List of all product names
2. List of all prices
3. List of products under $100
4. List of Electronics products
5. List of products that are low stock (< 10)
6. Dictionary mapping product names to prices
7. List of product names in uppercase
8. Total value of all inventory (price * stock for each)

Then create a menu that shows:
- All products
- Products by category
- Products by price range
- Products sorted by price
- Low stock alert
- Total inventory value
"""
products = [
    {"name": "Laptop", "price": 999, "category": "Electronics", "stock": 15},
    {"name": "Phone", "price": 699, "category": "Electronics", "stock": 25},
    {"name": "Desk", "price": 299, "category": "Furniture", "stock": 8},
    {"name": "Chair", "price": 149, "category": "Furniture", "stock": 20},
    {"name": "Monitor", "price": 399, "category": "Electronics", "stock": 12},
    {"name": "Keyboard", "price": 79, "category": "Electronics", "stock": 30},
    {"name": "Mouse", "price": 29, "category": "Electronics", "stock": 50},
    {"name": "Bookshelf", "price": 189, "category": "Furniture", "stock": 5},
]

# --- PART 1: DATA ANALYSIS (List Comprehensions) ---
# 1. Names
product_names = [p["name"] for p in products]

# 2. Prices
all_prices = [p["price"] for p in products]

# 3. Filtering: Under $100
cheap_items = [p for p in products if p["price"] < 100 ]

# 4. Filtering: Electronics
electronics = [p for p in products if p["category"] == "Electronics"]

# 5. Filtering: Low Stock (< 10)
low_stock = [p for p in products if p["stock"] < 10]

# 6. Dictionary Mapping (Names > Price)
price_map = {p["name"]: p["price"] for p in products}

# 7. Uppercase Names
upper_names = [p["name"].upper() for p in products]

# 8. Total Inventory Value (Sum of Price * Stock)
total_value = sum([p["price"] * p["stock"] for p in products])

# --- PART 2: INTERACTIVE MENU ---
def show_products(p):
    # Helper function to help format product output
    print(f"{p['name']:<12} | ${p['price']:>4} | {p['category']:<12} | Stock: {p['stock']}")

while True:
    width = 60
    print("\n" + "=" * width)
    print("INVENTORY DATA ANALYSIS".center(width))
    print("=" * width)

    print("1. View All Products")
    print("2. Filter by Category")
    print("3. Filter by Price Range")
    print("4. Sort by Price (High to Low)")
    print("5. Low Stock Alert")
    print("6. Total Inventory Value")
    print("7. Exit")

    choice = input("\nSelect option: ").strip()

    if choice == "1":
        print(f"\n{'Name':<12} | {'Price':<5} | {'Category':<12} | Stock")
        print("-" * 50)
        for p in products:
            show_products(p)

    elif choice == "2":
        cat = input("Enter category (Electronics/Furniture): ").title()
        filtered = [p for p in products if p['category'] == cat]
        for p in filtered:
            show_products(p)

    elif choice == "3":
        try:
            limit = float(input("Enter maximum price: "))
            filtered = [p for p in products if p['price'] <= limit]
            for p in products:
                show_products(p)
        except ValueError:
            print("ERROR: Invalid price input.")

    elif choice == "4":
        # Using sorted() with a lambda key
        sorted_products = sorted(products, key = lambda x: x['price'], reverse=True)
        for p in sorted_products:
            show_products(p)
    
    elif choice == "5":
        print("\n!! LOW STOCK ALERT !!")
        for p in low_stock:
            print(f"ORDER SOON: {p['name']} (Only {p['stock']} left)")
    
    elif choice == "6":
        print(f"\nTOTAL ASSET VALUATION: ${total_value:,.2f}")
    
    elif choice == "7":
        print("Closing analyst program. Goodbye!")
        break

    input("\nPress enter to continue...")