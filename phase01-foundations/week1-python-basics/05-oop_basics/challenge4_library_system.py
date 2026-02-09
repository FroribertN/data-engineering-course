"""
PROGRAM: Library Management System
------------------------------------

A comprehensive library system demonstrating OOP principles:
- Multiple classes working together
- Encapsulation and validation
- Properties and methods
- String representations
- Real-world business logic

Classes to implement:

1. Book
   - Attributes: title, author, isbn, genre, available
   - Methods: checkout(), return_book(), get_info()
   
2. Member
   - Attributes: name, member_id, email, books_borrowed (list)
   - Methods: borrow_book(book), return_book(book), get_borrowed_books()
   - Property: can_borrow (True if borrowed < 5 books)

3. Library
   - Attributes: name, books (list), members (list)
   - Methods:
     - add_book(book)
     - remove_book(isbn)
     - add_member(member)
     - find_book(isbn or title)
     - find_member(member_id)
     - checkout_book(member_id, isbn)
     - return_book(member_id, isbn)
     - list_available_books()
     - list_borrowed_books()
     - generate_report()

Requirements:
- Use proper encapsulation
- Add validation (can't borrow if book unavailable)
- Track which member has which book
- Implement proper __str__ and __repr__
- Add docstrings to all methods
- Create a menu system to interact with the library

"""
from datetime import datetime, timedelta
from typing import List, Optional


# ====================================
# CLASS 1: BOOK
# ====================================

class Book:
    """Represents a book in the library."""

    # Class variable to track total books
    total_books = 0

    def __init__(self, title: str, author: str, isbn: str, genre: str):
        """
        Initialize a new book.

        Args:
            title: Book title
            author: Book author
            isbn: International Standard Business Number (unique identifier)
            genre: Book genre/category
        """
        self.title = title
        self.author = author
        self.isbn = isbn
        self.genre = genre
        self.available = True
        self.borrowed_by = None  # Member who borrowed this book
        self.due_date = None     # When the book should be returned

        Book.total_books += 1

    def checkout(self, member: str, days: int = 14) -> bool:
        """
        Check out the book to a member.

        Args:
            member: Member borrowing the book
            days: Number of days for the loan (default 14)

        Returns:
            bool: True if successful, False if already borrowed
        """
        if not self.available:
            return False
        
        self.available = False
        self.borrowed_by = member
        self.due_date = datetime.now() + timedelta(days=days)
        return True
    
    def return_book(self) -> int:
        """
        Return the book to the library.

        Returns:
            int: Late fee if applicable (0 if on time)
        """
        late_fee = 0
        
        if self.due_date and datetime.now() >self.due_date:
            # Calculate late fee: $1 per day
            days_late = (datetime.now() - self.due_date).days
            late_fee = days_late * 1.0

        self.available = True
        self.borrowed_by = None
        self.due_date = None

        return late_fee
    
    def is_overdue(self) -> bool:
        """Checks if the book is overdue."""
        if self.due_date and not self.available:
            return datetime.now() > self.due_date
        return False
    
    def get_info(self) -> str:
        """Get detailed book information."""
        status = "Available" if self.available else f"Borrowed by {self.borrowed_by.name}"
        info = f"""
Book Information:
-----------------
Title:      {self.title}
Author:     {self.author}
ISBN:       {self.isbn}
Genre:      {self.genre}
Status:     {status}
"""
        
        if self.due_date and not self.available:
            info += f"Due Date:  {self.due_date.strftime('%Y-%m-%d')}\n"
            if self.is_overdue():
                info += "OVERDUE!\n"
        
        return info
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        status = "Available" if self.available else "Unavailable"
        return f"[{status}] {self.title} by {self.author}"
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Book('{self.title}', '{self.author}', '{self.isbn}', '{self.genre}')"
    
    def __eq__(self, other):
        """Books are equal if they have the same ISBN."""
        if isinstance(other, Book):
            return self.isbn == other.isbn
        return False
    

# ====================================
# CLASS 2: MEMER
# ====================================
# 2. The Member Class
class Member:
    """Represents a library member."""

    # Class variables
    total_members = 0
    max_books = 5       # Maximum books a member can borrow

    def __init__(self, name: str, email: str, member_id: Optional[str] = None):

        """ 
        Initialize a new library member.

        Args:
            name: member's full name.
            email: Members email address
            member_id: Optional custom member ID
        """
        self.name = name
        self.email = email
        self.member_id = member_id or f"M{Member.total_members + 1:04d}"
        self.books_borrowed = []    # List of Book objects
        self.total_borrowed = 0     # Lifetime counter
        self.late_fees = 0          # Accumulated late fees

        Member.total_members += 1 
    
    @property
    def can_borrow(self) -> bool:
        """Checks if member can borrow more books"""
        return len(self.books_borrowed) < Member.max_books
    
    @property
    def num_books_borrowed(self) -> bool:
        """Number of books currently borrowed."""
        return len(self.books_borrowed)
    
    def borrow_book(self, book: Book) -> bool:
        """
        Borrow a book from the library.

        Args: 
            book: Book to borrow

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.can_borrow:
            print(f"{self.name} has reached the borrowing limit ({Member.max_books} books)")
            return False
        
        if not book.available:
            print(f"'{book.title}' is not available")
            return False
        
        if book.checkout(self):
            self.books_borrowed.append(book)
            self.total_borrowed += 1
            print(f"{self.name} borrowed '{book.title}'")
            return True
        
        return False
    
    def return_book(self, book: Book) -> bool:
        """
        Return a borrowed book.

        Args:
            book: Book to return

        returns:
            bool: True if successful, False otherwise
        """
        if book not in self.books_borrowed:
            print(f"{self.name} doesn't have '{book.title}'")
            return False
        
        late_fee = book.return_book()
        self.books_borrowed.remove(book)

        if late_fee > 0:
            self.late_fees += late_fee
            print(f"Book returned late. Fee: ${late_fee:,.2f}")
        
        print(f"{self.name} returned '{book.title}'")
        return True
    
    def get_borrowed_books(self) -> List[Book]:
        """Get list of currently borrowed books."""
        return self.books_borrowed.copy()    
    
    def has_overdue_books(self) -> bool:
        """Checks if member has any overdue books."""
        return any(book.is_overdue() for book in self.books_borrowed)
    
    def get_overdue_books(self) -> List[Book]:
        """Get list of overdue books."""
        return [book for book in self.books_borrowed if book.is_overdue()]
    
    def get_info(self) -> str:
        """Get detailed member information."""
        info = f"""
Member Information:
-------------------
Name:              {self.name}
Member ID:         {self.member_id}
Email:             {self.email}
Books Borrowed:    {self.num_books_borrowed} / {Member.max_books}
Total Borrowed:    {self.total_borrowed}
Late Fees:         ${self.late_fees:,.2f}
"""
        
        if self.books_borrowed:
            info += "\nCurrently Borrowed:\n"
            for book in self.books_borrowed:
                overdue = "OVERDUE" if book.is_overdue() else ""
                info += f"  - {book.title} {overdue}\n"
        
        return info
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"{self.name} ({self.member_id}) - {self.num_books_borrowed} books"
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Member('{self.name}', '{self.email}', {self.member_id})"
    
    
# ====================================
# CLASS 3: LIBRARY
# ====================================

class Library:
    """Represents the library system - manages books, members, and the transcations."""

    def __init__(self, name: str):
        """
        Initialize a new library.

        Args:
            name: Library name
        """
        self.name = name
        self.books = []     # List of Book objects
        self.members = []   # list of Member objects
    
    # ============ BOOK MANAGEMENT ============

    def find_book_by_isbn(self, isbn: str) -> Optional[Book]:
        """Find a book by ISBN"""
        for book in self.books:
            if book.isbn == isbn:
                return book
        return None
    
    def find_book_by_title(self, title: str) -> List[Book]:
        """
        Find books by title (partial match, case-insensitive).

        Args:
            title: Title to search for

        Returns:
            List of matching books
        """
        title_lower = title.lower()
        return [book for book in self.books if title_lower in book.title.lower()]
    
    def find_books_by_author(self, author: str) -> List[Book]:
        """Find books by author (partial match)."""
        author_lower = author.lower()
        return [book for book in self.books if author_lower in book.author.lower()]
    
    def find_books_by_genre (self, genre: str) -> List[Book]:
        """Find books by genre."""
        genre_lower = genre.lower()
        return [book for book in self.books if genre_lower in book.genre.lower()]

    def add_book(self, book: Book) -> bool:
        """
        Add a book to the library.
        
        Args:
            book: Book to add

        Returns:
            bool: True if successful
        """
        # Check if book already exists (same ISBN)
        if any(b.isbn == book.isbn for b in self.books):
            print(f"Book with ISBN {book.isbn} already exists")
            return False
        
        self.books.append(book)
        print(f"Added '{book.title}' to library")
        return True
    
    def remove_book(self, isbn: str) -> bool:
        """
        Remove a book from the library.

        Args:
            isbn: ISBN of book to remove
        
        Returns:
            bool: True if successful
        """
        book = self.find_book_by_isbn(isbn)

        if not book:
            print(f"Book with ISBN {isbn} not found")
            return False
        
        if not book.available:
            print(f"Cannot remove '{book.title}' - currently borrowed")
            return False
        
        self.books.remove(book)
        print(f"Removed '{book.title}' from library")
        return True
    
    # ============ MEMBER MANAGEMENT ============

    def find_member(self, member_id: str) -> Optional[Member]:
        """Find a member by ID."""
        for member in self.members:
            if member.member_id == member_id:
                return member
        return None
    
    def find_member_by_name(self, name: str) -> List[Member]:
        """Find members by name (partial match)."""
        name_lower = name.lower()
        return [member for member in self.members if name_lower in member.name.lower()]

    def add_member(self, member: Member) -> bool:
        """
        Add a member to the library.

        Args:
            member: Member to add

        Returns:
            bool: True if successful
        """
        # Check if member ID already exists
        if any(m.member_id == member.member_id for m in self.members):
            print(f"Member with ID {member.member_id} already exists")
            return False
        
        self.members.append(member)
        print(f"Added member {member.name} ({member.member_id})")

    def remove_member(self, member_id: str) -> bool:
        """Removes a member from the library."""
        member = self.find_member(member_id)

        if not member:
            print(f"Member {member_id} not found")
            return False
        
        if member.books_borrowed:
            print(f"Cannot remove {member.name} - has {len(member.books_borrowed)} borrowed books")
            return False
        
        self.members.remove(member)
        print(f"Removed member {member.name}")
        return True
    
    # ============ BORROWING SYSTEM ============

    def checkout_book(self, member_id: str, isbn: str) -> bool:
        """
        Process book checkout.

        Args:
            member_id: Member's ID
            isbn: Book's ISBN

        Returns:
            bool: True if successful
        """
        member = self.find_member(member_id)
        if not member:
            print(f"Member {member_id} not found")
            return False
        
        book = self.find_book_by_isbn(isbn)
        if not book:
            print(f"Book with ISBN {isbn} not found")
            return False
        
        return member.borrow_book(book)
    
    def return_book(self, member_id: str, isbn: str) -> bool:
        """
        Process book return.

        Args:
            member_id: Member's ID
            isbn: Book's ISBN

        Returns:
            bool: True if successful
        """
        member = self.find_member(member_id)
        if not member:
            print(f"Member {member_id} not found")
            return False
        
        book = self.find_book_by_isbn(isbn)
        if not book:
            print(f"Book with ISBN {isbn} not found")
            return False
        
        return member.return_book(book)
    
    # ============ REPORTING ============
    def list_available_books(self) -> List[Book]:
        """Get the list of available books."""
        return [book for book in self.books if book.available]
    
    def list_borrowed_books(self) -> List[Book]:
        """Get the list of borrowed books."""
        return [book for book in self.books if not book.available]
    
    def list_overdue_books(self) -> List[Book]:
        """Get the list of overdue books."""
        return [book for book in self.books if book.is_overdue()]
    
    def get_genres(self) -> List[str]:
        """Get the list of all unique genres."""
        return sorted(set(book.genre for book in self.books))
    
    def generate_report(self) -> str:
        """Generate a comprehensive library report."""
        total_books = len(self.books)
        available_books = len(self.list_available_books())
        borrowed_books = len(self.list_borrowed_books())
        overdue_books = len(self.list_overdue_books())

        total_members = len(self.members)
        active_members = (len([m for m in self.members if m.books_borrowed]))

        # Most popular books (most borrowed)
        popular_books = sorted(
            self.books,
            key=lambda b: sum(1 for m in self.members if b in m.books_borrowed) + (0 if b.available else 1),
            reverse=True
        ) [:5]

        # Member with most books
        top_borrowers = sorted(
            self.members,
            key=lambda m: m.total_borrowed,
            reverse=True
        )[:5]

        report = f"""
{'=' * 70}
{self.name.upper() + " - LIBRARY REPORT"}
{'=' * 70}

BOOK STATISTICS:
----------------
Total Books:        {total_books}
Available:          {available_books} ({available_books / total_books * 100 if total_books > 0 else 0:.1f}%)
Borrowed:           {borrowed_books} ({borrowed_books / total_books * 100 if total_books > 0 else 0:.1f}%)
Overdue:            {overdue_books}

Genres:             {', '.join(self.get_genres())}

MEMBER STATISTICS:
------------------
Total Members:      {total_members}
Active Borrowers:   {active_members}
Total Late Fees:    ${sum(m.late_fees for m in self.members):,.2f}

MOST POPULAR BOOKS:
-------------------
"""
        for i, book in enumerate(popular_books, 1):
            status = "Available" if book.available else "Borrowed"
            report += f"{i}.  {book.title} by {book.author} ({status})\n"
        
        report += "\nTOP BORROWERS:\n----------------\n"
        for i, member in enumerate(top_borrowers, 1):
            report  += f"{i}.  {member.name} - {member.total_borrowed} book(s) borrowed\n"
        
        if overdue_books > 0:
            report += "\n   OVERDUE BOOKS:\n---------------\n"
            for book in self.list_overdue_books():
                days_late = (datetime.now() - book.due_date).days
                report += f"- {book.title} (Borrowed by {book.borrowed_by.name}, {days_late} days late)\n"
        
        report += "=" * 70

        return report
    
    def generate_statistics(self) -> dict:
        """Generate library statistics as dictionary."""
        return {
            "total_books": len(self.books),
            "available_books": len(self.list_available_books()),
            "borrowed_books": len(self.list_borrowed_books()),
            "overdue_books": len(self.list_overdue_books()),
            "total_members": len(self.members),
            "active_members": len([m for m in self.members if m.books_borrowed]),
            "genres": self.get_genres(),
            "total_late_fees": sum(m.late_fees for m in self.members)
        }
    
    def __str__(self):
        """User-friendly string representation."""
        return f"{self.name} - {len(self.books)} books, {len(self.members)} members"
    
    def __repr__(self):
        """Developer-friendly representation"""
        return f"Library('{self.name}')"


# ====================================
# INTERACTIVE MENU SYSTEM
# ====================================

def print_menu():
    """Display main menu."""
    print("\n" + "=" * 70)
    print(f"{'LIBRARY MANAGEMENT SYSTEM':^70}")
    print("=" * 70)
    print("""
1. Add Book
2. Remove Book
3. Search Books
4. List All Books
5. List Available Books
6. List Borrowed Books
          
7. Add Member
8. Remove Member
9. Search Members
10. List All Members
          
11. Checkout Book
12. Return Book
          
13. Generate Report
14. View Overdue Books
          
0.  Exit
""")
    print("=" * 70)

def add_book_interactive(library: Library):
    """Interactive book addition."""
    print("\n--- ADD NEW BOOK ---")
    title = input("Title: ").strip().title()
    author = input("Author: ").strip().title()
    isbn = input("ISBN: ").strip()
    genre = input("Genre: ").strip().title()

    if title and author and isbn and genre:
        book = Book(title, author, isbn, genre)
        library.add_book(book)
    else:
        print("All field are required")

def search_books_interactive(library: Library):
    """Interactive book search."""
    print("\n--- SEARCH BOOKS ---")
    print("1. Search by Title")
    print("2. Search by Author")
    print("3. Search ISBN")
    print("4. Search by Genre")

    choice = input("\nChoice: ").strip()

    if choice == "1":
        title = input("Enter title: ").strip()
        results = library.find_book_by_title(title)
    elif choice == "2":
        author = input("Enter author: ").strip()
        results = library.find_books_by_author(author)
    elif choice == "3":
        isbn = input("Enter ISBN: ").strip()
        book = library.find_book_by_isbn(isbn)
        results = [book] if book else []
    elif choice == "4":
        genre = input("Enter genre: ").strip()
        results = library.find_books_by_genre(genre)
    else:
        print("Invalid choice, try again.")
        return
    
    if results:
        print(f"\nFound {len(results)} book(s):")
        for book in results:
            print(f"    {book}")
    else:
        print("No books found")

def add_member_interactive(library: Library):
    """Interactive member addition."""
    print("\n--- ADD NEW MEMBER ---")
    name = input("Name: ").strip().title()

    email = input("Email: ").strip()

    if name and email:
        member = Member(name, email)
        library.add_member(member)
    else:
        print("Name and email are required")

def checkout_book_interactive(library: Library):
    """Interactive book checkout."""
    print("\n--- CHECKOUT BOOK ---")
    member_id = input("Member ID: ").strip()
    isbn = input("Book ISBN: ").strip()

    library.checkout_book(member_id, isbn)


def return_book_interactive(library: Library):
    """Interactive book return."""
    print("\n--- RETURN BOOK ---")
    member_id = input("Member ID: ").strip()
    isbn = input("Book ISBN: ").strip()

    library.return_book(member_id, isbn)


# ====================================
# MAIN PROGRAM
# ====================================

def main():
    """Main program with interactive menu."""

    # Create library
    library = Library("City Public Library")

    # Add sample data
    print("\nInitializing library with sample data...")
    print("----------------------------------------")

    # Sample books
    books = [
        Book("To Kill a Mockingbird", "Harper Lee", "978-0061120084", "Fiction"),
        Book("1984", "George Orwell", "978-0451524935", "Fiction"),
        Book("The Great Gatsby", "F. Scott Fitzgerald", "978-0743273565", "Fiction"),
        Book("Python Crash Course", "Eric Matthes", "978-1593279288", "Technology"),
        Book("Clean Code", "Robert Martin", "978-0132350884", "Technology"),
        Book("Sapiens", "Yuval Noah Harari", "978-0062316097", "History"),
        Book("Educated", "Tara Westover", "978-0399590504", "Biography"),
    ]

    for book in books:
        library.add_book(book)

    # Sample members
    members = [
        Member("Alice Johnson", "alice@email.com"),
        Member("Bob Smith", "bob@email.com"),
        Member("Charlie Brown", "charlie@email.com"),
    ]

    for member in members:
        library.add_member(member)

    # Sample checkouts
    library.checkout_book("M0001", "978-0061120084")
    library.checkout_book("M0002", "978-0451524935")

    print("\nSample data loaded!")

    # Main loop
    while True:
        print_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_book_interactive(library)
        
        elif choice == "2":
            isbn = input("\nEnter ISBN of book to remove: ").strip()
            library.remove_book(isbn)

        elif choice == "3":
            search_books_interactive(library)

        elif choice == "4":
            print("\n--- ALL BOOKS ---")
            for book in library.books:
                print(f"    {book}")
                print(f"\nTotal: {len(library.books)} books")
        
        elif choice == "5":
            print("\n--- AVAILABLE BOOKS ----")
            available = library.list_available_books()
            for book in available:
                print(f"    {book}")
                print(f"\nTotal: {len(available)} available")

        elif choice == "6":
            print("\n--- BORROWED BOOKS ---")
            borrowed = library.list_borrowed_books()
            for book in borrowed:
                print(f"    {book} - Borrowed by {book.borrowed_by.name}")
            print(f"\nTotal: {len(borrowed)} borrowed")

        elif choice == "7":
            add_member_interactive(library)

        elif choice == "8":
            member_id = input("\nEnter Member ID to remove: ").strip()
            library.remove_member(member_id)

        elif choice == "9":
            name = input("\nEnter member name to search: ").strip()
            results = library.find_member_by_name(name)
            if results:
                print(f"\nFound {len(results)} member(s):")
                for member in results:
                    print(f"    {member}")
            else:
                print("No member found")
        
        elif choice == "10":
            print("\n--- ALL MEMBERS ---")
            for member in library.members:
                print(f"    {member}")
            print(f"\nTotal: {len(library.members)} member(s)")

        elif choice == "11":
            checkout_book_interactive(library)

        elif choice == "12":
            return_book_interactive(library)

        elif choice == "13":
            print(library.generate_report())

        elif choice == "14":
            overdue = library.list_overdue_books()
            if overdue:
                print("\n   OVERDUE BOOKS:")
                for book in overdue:
                    days_late = (datetime.now() - book.due_date).days
                    print(f"    - {book.title} (Borrowed by {book.borrowed_by.name}, {days_late} days late)")
            else:
                print("\nNo overdue books!")
        
        elif choice == "0":
            print("\n" + "=" * 70)
            print("Thank you for using the Library Management System!".center(70))
            print("=" * 70)
            break

        else:
            print("\nInvalid choice! Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()