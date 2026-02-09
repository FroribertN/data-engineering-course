"""
PROGRAM: Basic Class Implementation
-------------------------------------

Create the following classes:

1. Rectangle
   - Attributes: width, height
   - Methods:
     - area(): return width * height
     - perimeter(): return 2 * (width + height)
     - is_square(): return True if width == height

2. Student
   - Attributes: name, student_id, grades (list)
   - Methods:
     - add_grade(grade): add grade to list
     - get_average(): return average of grades
     - get_letter_grade(): return A/B/C/D/F based on average
     - display_info(): print student information

3. Temperature
   - Attributes: celsius
   - Methods:
     - to_fahrenheit(): return temperature in Fahrenheit
     - to_kelvin(): return temperature in Kelvin
     - is_freezing(): return True if below 0°C
     - is_boiling(): return True if 100°C or above

Test each class thoroughly!
"""
# 1. Rectangle Class
class Rectangle:
    def __init__(self, width: float, height:float):
        self.width = width
        self.height = height
    
    def area(self) -> float:
        return self.width * self.height
    
    def perimeter(self) -> float:
        return 2 * (self.width + self.height)
    
    def is_square(self) -> bool:
        return self.width  == self.height

# 2. Student Class
class Student:
    def __init__(self, name: str, student_id: str):
        self.name = name
        self.student_id = student_id
        self.grades = []

    def add_grade(self, grade: float):
        self.grades.append(grade)
    
    def get_average(self) -> float:
        if not self.grades:
            return 0.0
        return sum(self.grades) / len(self.grades)
    
    def get_letter_grade(self) -> str:
        avg = self.get_average()
        if avg >= 90:
            return 'A'
        if avg >= 80:
            return 'B'
        if avg >= 70:
            return 'C'
        if avg >= 60:
            return 'D'
        return 'F'
    
    def display_info(self):
        print(f"Student: {self.name} ({self.student_id})")
        print(f"Average: {self.get_average():.1f} | Grade: {self.get_letter_grade()}")

# 3. Temperature Class
class Temperature:
    def __init__(self, celsius: float):
        self.celsius = celsius

    def to_fahrenheit(self) -> float:
        return (self.celsius * 9/5) + 32
    
    def to_kelvin(self) -> float:
        return self.celsius + 273.15
    
    def is_freezing(self) -> bool:
        return self.celsius < 0
    
    def is_boiling(self) -> bool:
        return self.celsius >= 100
    

# =======================================
# TESTING
# =======================================

# Testing Rectangle
print("\n-------- Rectangle Test --------")
rect1 = Rectangle(10, 5)
rect2 = Rectangle(7, 7)
print(f"Area (10x5): {rect1.area()}")
print(f"Is 7x7 Square: {rect2.is_square()}")

# Testing Student
print("\n-------- Student Test --------")
alice = Student("Alice", "S001")
alice.add_grade(95)
alice.add_grade(88)
alice.add_grade(79)
alice.display_info()

# Testing Temperature
print("\n-------- Temperature Test --------")
water = Temperature(100)
ice = Temperature(-5)
print(f"100°C to Kelvin: {water.to_kelvin()}") # 373.15
print(f"Is 100°C boiling?: {water.is_boiling()}") # True
print(f"Is -5°C freezing?: {ice.is_freezing()}") # Tru