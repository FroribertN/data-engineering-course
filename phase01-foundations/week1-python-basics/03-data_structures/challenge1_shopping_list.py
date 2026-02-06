"""
PROGRAM: Shopping List Manager
-------------------------------------
Create a program that manages a shopping list with these features:

MENU:
1. View shopping list
2. Add item
3. Remove item
4. Check if item is in list
5. Clear entire list
6. Show list statistics (total items, sorted list)
7. Exit

Requirements:
- Use a list to store items
- Use a while loop for the menu
- Validate all inputs
- Show appropriate messages for each action

"""

# --- INITIALIZATION ---
shopping_list = []

def display_menu():
    width = 30
    print("\n" + "=" * width)
    print("SHOPPING LIST MANAGER".center(width))
    print("=" * width)
    print("1. View List")
    print("2. Add item")
    print("3. Remove item")
    print("4. Check item")
    print("5. Clear list")
    print("6. View Statistics")
    print("7. Exit")
    print("-" * width)

# --- OPERATION LOOP ---
while True:
    display_menu()
    choice = input("Select an option: ").strip()

    # 1. View list
    if choice == "1":
        print(f"\n[ YOUR SHOPPING LIST ]")
        if not shopping_list:
            print("Your list is currently empty.")
        else:
            for index, item in enumerate(shopping_list, start=1):
                print(f"{index}. {item}")
    
    # 2. Add item
    elif choice == "2":
        new_item = input("Enter item to add: ").strip().lower()
        if new_item:
            shopping_list.append(new_item)
            print(f"Added '{new_item}' to the list.")
        else:
            print("ERROR: Item name cannot be empty.")
    
    # 3. Remove item
    elif choice == "3":
        remove_item = input("Enter item to remove: ").strip().lower()
        if remove_item in shopping_list:
            shopping_list.remove(remove_item)
            print(f"Removed '{remove_item}' from the list.")
        else:
            print(f"ERROR: '{remove_item}' not found in list.")
    
    # 4. Check item
    elif choice == "4":
        search_item = input("Check if item is in list: ").strip().lower()
        if search_item in shopping_list:
            print(f"Yes: '{search_item}' is on your list.")
        else:
            print(f"No: '{search_item}' is not on your list.")
    
    # 5. Clear list
    elif choice == "5":
        confirm = input("Are you sure you want to clear the entire list? (y/n): ").strip().lower()
        if confirm == "y":
            shopping_list.clear()
            print("Shopping list cleared.")
        
    # 6. Statistics
    elif choice == "6":
        print("\n" + "=" * 20)
        print("STATISTICS".center(20))
        print("=" * 20)
        print(f"Total items:     {len(shopping_list)}")
        if shopping_list:
            sorted_list = sorted(shopping_list)
            print(f"Sorted list:     {', '.join(sorted_list)}")
        else:
            print("Sorted list: (list is empty)")
    
    # 7. Exit
    elif choice == "7":
        print(f"\nClosing Shopping List Manager. Goodbye!")
        break

    else:
        print("ERROR: Invalid selection. Please choose 1-7.")
    
    input("\nPress Enter to continue...")