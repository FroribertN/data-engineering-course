"""
PROGRAM: Student Grade Calculator
---------------------------------------
PURPOSE:
    Collects a student's name and scores for five subjects.
    The program calculates the average score, assigns a
    letter grade, determines pass or fail status, and
    provides performance-based remarks.

FUNCTIONALITY:
    1. Prompts the user to enter the student's name.
    2. Prompts the user to enter scores (0-100) for five subjects.
    3. Calculates the average of the five subject scores.
    4. Determines the letter grade based on the average:
        - A: 90-100
        - B: 80-89
        - C: 70-79
        - D: 60-69
        - F: Below 60
    5. Determines pass or fail status (passing mark = 60).
    6. Displays remarks based on overall performance:
        - 90 and above: "Excellent work!"
        - 80-89: "Great job!"
        - 70-79: "Good effort!"
        - 60-69: "You passed, but there's room for improvement"
        - Below 60: "You need to work harder"

BONUS FEATURES:
    - Checks each individual subject score.
    - If any score is below 40, displays:
    "Warning: You failed [subject_name]"

OBJECTIVES:
    - Use conditional statements (if/elif/else) for grading logic.
    - Validate numeric input to ensure values are within range.
    - Produce clear and user-friendly output.
"""


# --- GLOBAL CONSTANTS ---
PASSING_AVERAGE = 60.0
SUBJECT_FAIL_THRESHOLD = 40.0

# 1. Header Display
print("=" * 60)
print("STUDENT GRADE CALCULATOR".center(60))
print("=" * 60)

# 2. Data Collection
student_name = input("\nEnter student name: ").strip().title()

try:
    # Collect individual subject scores
    math_score    = float(input("Enter Math score: "))
    science_score = float(input("Enter Science score: "))
    english_score = float(input("Enter English score: "))
    history_score = float(input("Enter History score: "))
    art_score     = float(input("Enter Art score: "))

    # 3. Calculations
    total_score = math_score + science_score + english_score + history_score + art_score
    average_score = total_score / 5

    # 4. Grading and remark logic using if/elif/else
    if average_score >= 90:
        letter_grade = "A"
        remark = "Excellent work!"
    elif average_score >= 80:
        letter_grade = "B"
        remark = "Great Job!"
    elif average_score >= 70:
        letter_grade = "C"
        remark = "Good effort!"
    elif average_score >= 60:
        letter_grade = "D"
        remark = "You passed but there is room for improvement."
    else:
        letter_grade = "F"
        remark = "You need to work harder."
    
    # 5. Pass/fail determination
    if average_score >= PASSING_AVERAGE:
        status = "PASSED"
    else:
        status = "FAILED"
    
    # --- DISPLAY RESULTS ---
    print("\n" + "=" * 60)
    print(f"REPORT CARD")
    print("-" * 60)
    print(f"Student:           {student_name}")
    print(f"Average Score:     {average_score:.2f}%")
    print(f"Letter Grade:      {letter_grade}")
    print(f"Academic Status:   {status}")
    print(f"Remark:            {remark}")
    print("-" * 60)

    # 6. BONUS: Individual subject warning
    print("\n[ SUBJECT ALERTS ]")

    # Check each subject for a score below the failure threshold
    has_warnings = False

    if math_score < SUBJECT_FAIL_THRESHOLD:
        print(f"Warning: You failed Math (Score: {math_score})")
        has_warnings = True
    if science_score < SUBJECT_FAIL_THRESHOLD:
        print(f"Warning: You failed Science (Score: {science_score})")
        has_warnings = True
    if english_score < SUBJECT_FAIL_THRESHOLD:
        print(f"Warning: You failed English (Score: {english_score})")
        has_warnings = True
    if history_score < SUBJECT_FAIL_THRESHOLD:
        print(f"Warning: You failed History (Score: {history_score})")
        has_warnings = True
    if art_score < SUBJECT_FAIL_THRESHOLD:
        print(f"Warning: You failed Art (Score: {art_score})")
    
    if not has_warnings:
        print("All individual subjects meet the minimum requirement.")
    
    print("=" * 60)
except ValueError:
    print("\n[!] ERROR: Please enter valid numeric numbers for subject scores.")