"""
PROGRAM: Basic Inheritance
-------------------------------

Create an inheritance hierarchy for a school system:

1. Person (Base Class)
   - Attributes: name, age, email
   - Methods: get_info(), send_email(message)

2. Student (inherits Person)
   - Additional attributes: student_id, grades (list)
   - Override get_info() to include student_id
   - Methods: add_grade(grade), get_average()

3. Teacher (inherits Person)
   - Additional attributes: employee_id, subject, salary
   - Override get_info() to include employee_id and subject
   - Methods: give_raise(amount)

4. Principal (inherits Teacher)
   - Additional attribute: school_name
   - Override get_info() to include school name
   - Methods: approve_budget(amount)

Test all classes and their inherited methods!
"""

# ================================
# 1. PERSON (Base Class) - Parent
# ================================

class Person:
    """
    Base class representing a person in the school system.

    Attributes:
        name: Person's full name
        age: Age in years
        email: Contact email address
    """
    def __init__(self, name: str, age: int, email: str):
        self.name = name
        self.age = age
        self.email = email
    
    def get_info(self) -> str:
        """Returnsa formatted string of the person's basic details."""
        return f"Name: {self.name}, Age: {self.age}, Email: {self.email}"
    
    def send_email(self, message: str):
        """Simulates sending an email."""
        print(f"Send to {self.email}: {message}")


# ================================
# 2. STUDENT (Inherits Person)
# ================================

class Student(Person):
    """Represents a student, inheriting from Person."""
    def __init__(self, name: str, age: int, email: str, student_id: str):
        super().__init__(name, age, email)  # Pass data up to Person
        self.student_id = student_id
        self.grades = []
    
    def add_grade(self, grade: float):
        """Add a new grade to the student's list."""
        self.grades.append(grade)

    def get_average(self) -> float:
        """Calculates the average grade."""
        return sum(self.grades) / len(self.grades) if self.grades else 0.0
    
    def get_info(self) -> str:
        """Overrides parent method to include Student ID."""
        base_info = super().get_info()
        return f"{base_info}, Student ID: {self.student_id}"
    

# ================================
# 3. TEACHER (Inherits Person)
# ================================

class Teacher(Person):
    """Represents a teacher, inheriting from Person."""
    def __init__(self, name: str, age: int, email:str, employee_id: str, subject: str, salary: float):
        super().__init__(name, age, email)  # Pass data up to Person
        self.employee_id = employee_id
        self.subject = subject
        self.salary = salary

    def give_raise(self, amount: float):
        """Increases the teacher's salary."""
        self.salary += amount

    def get_info(self):
        """Overrides parent method to include Employee ID and Subject."""
        base_info = super().get_info()
        return f"{base_info}, Emp ID: {self.employee_id}, Subject: {self.subject}"
    

# ================================
# 4. PRINCIPLE (Inherits Teacher)
# ================================

class Principal(Teacher):
    """Represents a principal, inheriting from Teacher."""
    def __init__(self, name: str, age: int, email:str, employee_id: str, subject: str, salary: float, school_name: str):
        super().__init__(name, age, email, employee_id, subject, salary)
        self.school_name = school_name

    def approve_budget(self, amount: float):
        """Approves a school budget."""
        print(f"Principal {self.name} approved a budget of ${amount:,.2f} for {self.school_name}.")

    def get_info(self) -> str:
        """Overrides Teach method to include the School Name."""
        base_info = super().get_info()
        return f"{base_info}, School: {self.school_name}"
    

# ================================
#           TESTING
# ================================

# Create a Student
print("\nStudent - Alice")
print("-" * 15)
s1 = Student("Alice", 16, "alice@school.com", "S101")
s1.add_grade(90)
s1.add_grade(80)
print(s1.get_info())
print(f"Average: {s1.get_average()}")

# Create a Teacher
print("\nTeacher - Mr. Smith".center(20))
print("-" * 19)
t1 = Teacher("Mr. Smith", 45, "smith@school.com", "T500", "Python 101", 55000)
t1.give_raise(5000)
print(t1.get_info())
print(f"New Salary: ${t1.salary}")

# Create a Principal
print("\nPrincipal - Dr. Banner".center(20))
print("-" * 22)
p1 = Principal("Dr. Banner", 50, "banner@school.com", "P001", "Leadership", 95000, "Avengers Academy")
print(p1.get_info())
p1.approve_budget(15000)
p1.send_email("Meeting at 9 AM.") # Testing inherited method from the very top (Person)