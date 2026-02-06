"""
Day 3 Final Challenge: Contact Management System
Complete Working Program

A comprehensive contact manager using lists, tuples, dictionaries, and sets.
"""

import random
import string

# ==========================================
# GLOBAL STORAGE
# ==========================================

contacts = {}

# Sample data for testing (optional - comment out if you want to start empty)
contacts = {
    "C001": {
        "name": "Alice Smith",
        "email": "alice@email.com",
        "phones": ["123-456-7890", "098-765-4321"],
        "address": {
            "street": "123 Main St",
            "city": "Sydney",
            "postcode": "2000"
        },
        "tags": {"friend", "work"},
        "notes": "Met at engineering conference 2024"
    },
    "C002": {
        "name": "Bob Johnson",
        "email": "bob@company.com",
        "phones": ["555-123-4567"],
        "address": {
            "street": "456 Oak Ave",
            "city": "Melbourne",
            "postcode": "3000"
        },
        "tags": {"work", "colleague"},
        "notes": "Project manager at Tech Corp"
    },
    "C003": {
        "name": "Charlie Brown",
        "email": "charlie@example.com",
        "phones": ["777-888-9999", "666-555-4444"],
        "address": {
            "street": "789 Pine Rd",
            "city": "Sydney",
            "postcode": "2001"
        },
        "tags": {"friend", "family"},
        "notes": "Cousin, lives nearby"
    }
}


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def generate_id():
    """Generate unique contact ID like C001, C002, etc."""
    if not contacts:
        return "C001"
    
    # Get all existing IDs, extract numbers, find max
    existing_nums = [int(cid[1:]) for cid in contacts.keys()]
    next_num = max(existing_nums) + 1
    return f"C{next_num:03d}"  # Format as C001, C002, etc.


def validate_email(email):
    """Check if email contains @ symbol"""
    return "@" in email and len(email) > 3


def clear_screen():
    """Print newlines to simulate clearing screen"""
    print("\n" * 2)


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 110)
    print(title.center(110))
    print("=" * 110)


def print_separator():
    """Print a separator line"""
    print("-" * 110)


def display_contact(contact_id, contact):
    """Display a single contact's full information"""
    print("\n" + "=" * 60)
    print(f"CONTACT ID: {contact_id}".center(60))
    print("=" * 60)
    print(f"Name:     {contact['name']}")
    print(f"Email:    {contact['email']}")
    print(f"Phones:   {', '.join(contact['phones'])}")
    print(f"Tags:     {', '.join(sorted(contact['tags'])) if contact['tags'] else 'None'}")
    print(f"\nAddress:")
    print(f"  Street:   {contact['address']['street']}")
    print(f"  City:     {contact['address']['city']}")
    print(f"  Postcode: {contact['address']['postcode']}")
    print(f"\nNotes:    {contact['notes'] if contact['notes'] else 'None'}")
    print("=" * 60)


def display_contact_summary(contact_id, contact):
    """Display contact in one line (for lists)"""
    primary_phone = contact['phones'][0] if contact['phones'] else 'N/A'
    city = contact['address']['city']
    tags = ','.join(sorted(list(contact['tags']))[:2]) if contact['tags'] else ''
    print(f"{contact_id:5s} | {contact['name'][:20]:20s} | {primary_phone:15s} | {contact['email'][:25]:25s} | {city[:12]:12s} | {tags[:15]:15s}")


def pause():
    """Wait for user to press Enter"""
    input("\nPress Enter to continue...")


# ==========================================
# MAIN FUNCTIONS
# ==========================================

def add_contact():
    """Add a new contact to the system"""
    print_header("ADD NEW CONTACT")
    
    # Generate unique ID
    contact_id = generate_id()
    
    # Get name (required)
    name = input("Enter full name: ").strip().title()
    while not name:
        print("Name cannot be empty!")
        name = input("Enter full name: ").strip().title()
    
    # Get email (required, must be valid)
    email = input("Enter email: ").strip().lower()
    while not validate_email(email):
        print("Invalid email! Must contain @ and be at least 4 characters.")
        email = input("Enter email: ").strip().lower()
    
    # Get phone numbers (at least one required)
    phones = []
    print("\nEnter phone numbers (press Enter without typing to finish): ")
    while True:
        phone = input(f"  Phone #{len(phones) + 1}: ").strip()
        if not phone:
            if phones:  # At least one phone required
                break
            else:
                print("WARNING: At least one phone number is required!")
        else:
            phones.append(phone)
            print(f"Added: {phone}")
    
    # Get address
    print("\nAddress Information:")
    street = input("  Street address: ").strip().title()
    city = input("  City: ").strip()
    postcode = input("  Postcode: ").strip()
    
    # Get tags (optional)
    print("\nTags (comma-separated, e.g., friend,work,family):")
    tags_input = input("  Tags: ").strip()
    if tags_input:
        tags = set(tag.strip().lower() for tag in tags_input.split(",") if tag.strip())
    else:
        tags = set()
    
    # Get notes (optional)
    notes = input("\nNotes (optional): ").strip()
    
    # Create contact dictionary
    contacts[contact_id] = {
        "name": name,
        "email": email,
        "phones": phones,
        "address": {
            "street": street,
            "city": city,
            "postcode": postcode
        },
        "tags": tags,
        "notes": notes
    }
    
    print(f"\nContact added successfully!")
    print(f"   Contact ID: {contact_id}")
    print(f"   Name: {name}")


def view_all_contacts():
    """Display all contacts in a formatted table"""
    print_header("ALL CONTACTS")
    
    if not contacts:
        print("\nNo contacts found. Add your first contact!")
        return
    
    # Sort contacts by name (case-insensitive)
    sorted_contacts = sorted(contacts.items(), key=lambda x: x[1]['name'].lower())
    
    # Print table header
    print(f"\n{'ID':5s} | {'Name':20s} | {'Phone':15s} | {'Email':25s} | {'City':12s} | {'Tags':15s}")
    print_separator()
    
    # Display each contact
    for contact_id, contact in sorted_contacts:
        display_contact_summary(contact_id, contact)
    
    print_separator()
    print(f"Total contacts: {len(contacts)}")


def search_contact():
    """Search for contacts by name (partial, case-insensitive)"""
    print_header("SEARCH CONTACT")
    
    if not contacts:
        print("\nNo contacts to search.")
        return
    
    search_term = input("\nEnter name to search: ").strip()
    
    if not search_term:
        print("Search term cannot be empty!")
        return
    
    # Find matches (case-insensitive, partial match)
    matches = {
        cid: contact for cid, contact in contacts.items()
        if search_term in contact['name'].lower()
    }
    
    if not matches:
        print(f"\nNo contacts found matching '{search_term}'")
        return
    
    print(f"\nFound {len(matches)} contact(s) matching '{search_term}':")
    
    for contact_id, contact in matches.items():
        display_contact(contact_id, contact)


def update_contact():
    """Update an existing contact's information"""
    print_header("UPDATE CONTACT")
    
    if not contacts:
        print("\nNo contacts to update.")
        return
    
    contact_id = input("\nEnter contact ID to update: ").strip().upper()
    
    if contact_id not in contacts:
        print(f"Contact ID '{contact_id}' not found!")
        return
    
    contact = contacts[contact_id]
    
    # Show current information
    print("\nCurrent Information:")
    display_contact(contact_id, contact)
    
    print("\nUpdate Information (press Enter to keep current value)")
    print_separator()
    
    # Update name
    new_name = input(f"Name [{contact['name']}]: ").strip().title()
    if new_name:
        contact['name'] = new_name
        print("Name updated")
    
    # Update email
    new_email = input(f"Email [{contact['email']}]: ").strip().lower()
    if new_email:
        if validate_email(new_email):
            contact['email'] = new_email
            print("Email updated")
        else:
            print("Invalid email format, keeping old value")
    
    # Update address
    print("\nAddress:")
    new_street = input(f"  Street [{contact['address']['street']}]: ").strip().title()
    if new_street:
        contact['address']['street'] = new_street
        print("Street updated")
    
    new_city = input(f"  City [{contact['address']['city']}]: ").strip().title()
    if new_city:
        contact['address']['city'] = new_city
        print("City updated")
    
    new_postcode = input(f"  Postcode [{contact['address']['postcode']}]: ").strip()
    if new_postcode:
        contact['address']['postcode'] = new_postcode
        print("Postcode updated")
    
    # Update notes
    current_notes = contact['notes'] if contact['notes'] else "None"
    new_notes = input(f"\nNotes [{current_notes}]: ").strip()
    if new_notes:
        contact['notes'] = new_notes
        print("Notes updated")
    
    print("\nContact updated successfully!")


def delete_contact():
    """Delete a contact after confirmation"""
    print_header("DELETE CONTACT")
    
    if not contacts:
        print("\nNo contacts to delete.")
        return
    
    contact_id = input("\nEnter contact ID to delete: ").strip().upper()
    
    if contact_id not in contacts:
        print(f"Contact ID '{contact_id}' not found!")
        return
    
    # Show contact to be deleted
    print("\nYou are about to delete this contact:")
    display_contact(contact_id, contacts[contact_id])
    
    # Confirm deletion
    confirm = input("\nAre you sure you want to delete? Type 'YES' to confirm: ").strip()
    
    if confirm.upper() == 'YES':
        name = contacts[contact_id]['name']
        del contacts[contact_id]
        print(f"\nContact '{name}' (ID: {contact_id}) deleted successfully!")
    else:
        print("\nDeletion cancelled.")


def manage_tags():
    """Add or remove tags from a contact"""
    print_header("MANAGE TAGS")
    
    if not contacts:
        print("\nNo contacts available.")
        return
    
    contact_id = input("\nEnter contact ID: ").strip().upper()
    
    if contact_id not in contacts:
        print(f"Contact ID '{contact_id}' not found!")
        return
    
    contact = contacts[contact_id]
    
    print(f"\nContact: {contact['name']}")
    print(f"Current tags: {', '.join(sorted(contact['tags'])) if contact['tags'] else 'None'}")
    
    print("\nOptions:")
    print("1. Add tags")
    print("2. Remove tags")
    print("3. Replace all tags")
    print("4. Cancel")
    
    choice = input("\nSelect choice: ").strip()
    
    if choice == "1":
        # Add tags
        new_tags_input = input("\nEnter tags to add (comma-separated): ").strip()
        if new_tags_input:
            new_tags = set(tag.strip().lower() for tag in new_tags_input.split(",") if tag.strip())
            contact['tags'].update(new_tags)  # Set union
            print(f"Added tags: {', '.join(sorted(new_tags))}")
        else:
            print("No tags entered.")
    
    elif choice == "2":
        # Remove tags
        if not contact['tags']:
            print("No tags to remove!")
            return
        
        print(f"\nCurrent tags: {', '.join(sorted(contact['tags']))}")
        tags_to_remove_input = input("Enter tags to remove (comma-separated): ").strip()
        if tags_to_remove_input:
            tags_to_remove = set(tag.strip().lower() for tag in tags_to_remove_input.split(",") if tag.strip())
            removed = contact['tags'].intersection(tags_to_remove)
            contact['tags'].difference_update(tags_to_remove)  # Set difference
            if removed:
                print(f"Removed tags: {', '.join(sorted(removed))}")
            else:
                print("No matching tags found to remove.")
        else:
            print("No tags entered.")
    
    elif choice == "3":
        # Replace all tags
        new_tags_input = input("\nEnter new tags (comma-separated): ").strip()
        if new_tags_input:
            contact['tags'] = set(tag.strip().lower() for tag in new_tags_input.split(",") if tag.strip())
            print(f"Tags replaced: {', '.join(sorted(contact['tags']))}")
        else:
            contact['tags'] = set()
            print("All tags removed.")
    
    elif choice == "4":
        print("Cancelled.")
        return
    else:
        print("Invalid choice! Select 1-4.")
        return
    
    print(f"\nUpdated tags: {', '.join(sorted(contact['tags'])) if contact['tags'] else 'None'}")


def list_by_tag():
    """List all contacts that have a specific tag"""
    print_header("LIST CONTACTS BY TAG")
    
    # Collect all unique tags from all contacts
    all_tags = set()
    for contact in contacts.values():
        all_tags.update(contact['tags'])
    
    if not all_tags:
        print("\nNo tags found in any contacts.")
        return
    
    # Display available tags
    print("\nAvailable tags:")
    sorted_tags = sorted(all_tags)
    for i, tag in enumerate(sorted_tags, 1):
        # Count contacts with this tag
        count = sum(1 for c in contacts.values() if tag in c['tags'])
        print(f"  {i}. {tag} ({count} contacts)")
    
    # Get tag choice
    tag_choice = input("\nEnter tag name to filter by: ").strip().lower()
    
    if tag_choice not in all_tags:
        print(f"Tag '{tag_choice}' not found!")
        return
    
    # Find contacts with this tag
    matching_contacts = {
        cid: contact for cid, contact in contacts.items()
        if tag_choice in contact['tags']
    }
    
    if not matching_contacts:
        print(f"\nNo contacts found with tag '{tag_choice}'.")
        return
    
    # Display results
    print(f"\nFound {len(matching_contacts)} contact(s) with tag '{tag_choice}':")
    print_separator()
    print(f"{'ID':5s} | {'Name':20s} | {'Phone':15s} | {'Email':25s} | {'City':12s}")
    print_separator()
    
    for contact_id, contact in sorted(matching_contacts.items(), key=lambda x: x[1]['name'].lower()):
        display_contact_summary(contact_id, contact)
    
    print_separator()


def show_statistics():
    """Display statistics about all contacts"""
    print_header("CONTACT STATISTICS")
    
    if not contacts:
        print("\nNo contacts to analyze.")
        return
    
    # Total contacts
    total = len(contacts)
    print(f"\nTotal Contacts: {total}")
    
    # Contacts per city
    print("\nContacts by City:")
    cities = {}
    for contact in contacts.values():
        city = contact['address']['city']
        cities[city] = cities.get(city, 0) + 1
    
    for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total) * 100
        bar = "█" * int(percentage / 5)  # Simple bar chart
        print(f"  {city:15s}: {count:3d} ({percentage:5.2f}%) {bar}")
    
    # Tag statistics
    print("\nTag Usage:")
    tag_counts = {}
    for contact in contacts.values():
        for tag in contact['tags']:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    if tag_counts:
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            bar = "█" * int(percentage / 5)
            print(f"  {tag:15s}: {count:3d} ({percentage:5.2f}%) {bar}")
    
    # Phone statistics
    print("\nPhone Number Statistics:")
    total_phones = sum(len(contact['phones']) for contact in contacts.values())
    avg_phones = total_phones / total
    max_phones = max(len(contact['phones']) for contact in contacts.values())
    min_phones = min(len(contact['phones']) for contact in contacts.values())
    
    print(f"  Total phone numbers: {total_phones}")
    print(f"  Average per contact: {avg_phones:.2f}")
    print(f"  Maximum: {max_phones}")
    print(f"  Minimum: {min_phones}")
    
    # Contacts with notes
    with_notes = sum(1 for c in contacts.values() if c['notes'])
    print(f"\nContacts with notes: {with_notes} ({(with_notes/total)*100:.1f}%)")
    
    # Email domains
    print("\nEmail Domains:")
    domains = {}
    for contact in contacts.values():
        domain = contact['email'].split('@')[-1]
        domains[domain] = domains.get(domain, 0) + 1
    
    for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {domain:20s}: {count}")


def export_contacts():
    """Export all contacts to a formatted text file"""
    print_header("EXPORT CONTACTS")
    
    if not contacts:
        print("\nNo contacts to export.")
        return
    
    filename = input("\nEnter filename (e.g., contacts.txt): ").strip()
    if not filename:
        filename = "contacts_export.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("CONTACT EXPORT\n")
            f.write(f"Total Contacts: {len(contacts)}\n")
            f.write("=" * 70 + "\n\n")
            
            # Sort by name
            sorted_contacts = sorted(contacts.items(), key=lambda x: x[1]['name'].lower())
            
            for contact_id, contact in sorted_contacts:
                f.write(f"ID: {contact_id}\n")
                f.write(f"Name: {contact['name']}\n")
                f.write(f"Email: {contact['email']}\n")
                f.write(f"Phones: {', '.join(contact['phones'])}\n")
                f.write(f"Address: {contact['address']['street']}, ")
                f.write(f"{contact['address']['city']} {contact['address']['postcode']}\n")
                f.write(f"Tags: {', '.join(sorted(contact['tags'])) if contact['tags'] else 'None'}\n")
                f.write(f"Notes: {contact['notes'] if contact['notes'] else 'None'}\n")
                f.write("-" * 70 + "\n\n")
        
        print(f"Contacts exported successfully to '{filename}'!")
        print(f"   {len(contacts)} contacts exported.")
    
    except Exception as e:
        print(f"Error exporting contacts: {e}")


# ==========================================
# MAIN MENU
# ==========================================

def display_menu():
    """Display the main menu"""
    print("\n" + "=" * 60)
    print("MAIN MENU".center(60))
    print("=" * 60)
    print("1. Add new contact")
    print("2. View all contacts")
    print("3. Search contact")
    print("4. Update contact")
    print("5. Delete contact")
    print("6. Manage tags")
    print("7. List contacts by tag")
    print("8. Show statistics")
    print("9. Export contacts")
    print("0. Exit")
    print("=" * 60)


def main():
    """Main program loop"""
    print("=" * 60)
    print("CONTACT MANAGEMENT SYSTEM".center(60))
    print("=" * 60)
    print("\nWelcome! Manage your contacts efficiently.")
    print(f"Current contacts in system: {len(contacts)}")
    
    while True:
        display_menu()
        
        choice = input("\nSelect an option: ").strip()
        
        if choice == "1":
            add_contact()
        elif choice == "2":
            view_all_contacts()
        elif choice == "3":
            search_contact()
        elif choice == "4":
            update_contact()
        elif choice == "5":
            delete_contact()
        elif choice == "6":
            manage_tags()
        elif choice == "7":
            list_by_tag()
        elif choice == "8":
            show_statistics()
        elif choice == "9":
            export_contacts()
        elif choice == "0":
            print("\n" + "=" * 60)
            print("Thank you for using Contact Management System!".center(60))
            print("Goodbye!".center(60))
            print("=" * 60)
            break
        else:
            print("\nInvalid choice! Please enter a number from 0-9.")
        
        pause()


# ==========================================
# RUN THE PROGRAM
# ==========================================

if __name__ == "__main__":
    main()