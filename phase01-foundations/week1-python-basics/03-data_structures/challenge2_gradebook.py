"""
PROGRAM: Student Grade Book System 
--------------------------------------
Create a program that manages student grades using dictionaries.

Each student should have:
- Name
- Student ID
- Grades (list of scores)
- Average (calculated)

MENU:
1. Add new student
2. Add grade to student
3. View student information
4. View all students
5. Calculate class average
6. Find top student
7. Exit

Use a dictionary where:
- Key: Student ID
- Value: Dictionary with student info

"""

# --- INITIALIZATION ---
gradebook = {}

def display_menu():
    width = 60
    print("\n" + "=" * width)
    print("STUDENT GRADE BOOK SYSTEM".center(width))
    print("=" * width)
    print("1. Add New Student")
    print("2. Add Grade to Student")
    print("3. View Student Information")
    print("4. View All Students")
    print("5. Calculate Class Average")
    print("6. Find Top Student")
    print("7. Exit")
    print("-" * width)

# --- MAIN LOOP ---
while True:
    display_menu()
    choice = input("Select an option: ").strip()

    # 1.. Add new student
    if choice == "1":
        student_id = input("Enter Student ID: ").strip().upper()
        if student_id in gradebook:
            print("ERROR: A student with this ID already exists.")
        else:
            name = input("Enter Student Name: ").strip().title()
            gradebook[student_id] = {
                "name": name,
                "grades": [],
                "average": 0.0
            }
            print(f"Student '{name}' added successfully.")
    
    # 2. Add grade to student
    elif choice == "2":
        student_id = input("Enter Student ID: ").strip().upper()
        if student_id in gradebook:
            try:
                grade = float(input("Enter grade: "))
                if 0 <= grade <= 100:
                    gradebook[student_id]["grades"].append(grade)

                    # Recalculate average
                    current_grades = gradebook[student_id]["grades"]
                    gradebook[student_id]["average"] = sum(current_grades) / len(current_grades)
                    print(f"Grade {grade} added to {gradebook[student_id]['name']}.")
                else:
                    print("ERROR: Grade must be between 0 and 100.")
            except ValueError:
                print("ERROR: Please enter a numeric value.")
        else:
            print("ERROR: Student ID not found.")
    
    # 3. View student information
    elif choice == "3":
        student_id = input("Enter Student ID: ").strip().upper()
        if student_id in gradebook:
            info = gradebook[student_id]
            print(f"\n==== Student Information ====")
            print(f"Name:     {info['name']}")
            print(f"ID:       {student_id}")
            print(f"Grades:   {info['grades']}")
            print(f"Average:  {info['average']:.2f}")
        else:
            print("ERROR: Student ID not found.")
    
    # 4. View all students
    elif choice == "4":
        if not gradebook:
            print(f"\nThe gradebook is currently empty.")
        else:
            print(f"\n{'ID':10} | {'Name':<25} | {'Average':<10}")
            print("-" * 60)
            for s_id, info in gradebook.items():
                print(f"{s_id:<10} | {info["name"]:<25} | {info["average"]:<10.2f}")

    # 5. Calculate class average
    elif choice == "5":
        if not gradebook:
            print("\nNo students in record.")
        else:
            all_averages = [info["average"] for info in gradebook.values()]
            class_avg = sum(all_averages) / len(all_averages)
            print(f"\nClass Average Across {len(gradebook)} Students: {class_avg:.2f}")

    # 6. Find top student
    elif choice == "6":
        if not gradebook:
            print("\nNo students in record.")
        else:
            # Find the student with the maximum average
            top_id = max(gradebook, key = lambda s_id: gradebook[s_id]["average"])
            top_student = gradebook[top_id]
            print(f"\nTop Performer: {top_student['name']} ({top_id})")
            print(f"Highest Average: {top_student['average']:.2f}")
    
    # 7. Exit
    elif choice == "7":
        print("\nExiting Grade Book System. Goodbye!")
        break

    else:
        print("ERROR: Invalid selection. Please choose 1-7.")
    
    input("\nPress Enter to continue...")