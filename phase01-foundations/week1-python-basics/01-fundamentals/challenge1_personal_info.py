"""
PROGRAM: Personal Information & Health Calculator
---------------------------------------------------
PURPOSE:
    This script serves as a data processing tool to convert basic user 
    demographics and biometrics into various chronological and physical units.

REQUIREMENTS:
    - Input: First/Last name (str), Age (int), Height (float), Weight (float).
    - Logic: Use standardized conversion constants (365 days/year, 3.28084 ft/m).
    Logic: BMI calculation [Weight (kg) / (Height^2 (m))] and status categorization.
    - Validation: Implement type casting for numeric inputs.
    - Output: Utilize f-string interpolation for high-precision formatting.

EXPECTED DISPLAY:
    - A categorized report detailing Chronology, Physical Dimensions, and a Health Assessment status.
"""

def get_bmi_category(bmi):
    # Categorizes BMI score based on standard WHO  health intervals
    if bmi <=0: 
        return "Invalid input"
    elif bmi < 18.5:        
        return "Underweight"
    elif bmi < 25:
        return "Healthy Weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def main():
    #--- HEADER DISPLAY ---
    width = 45
    print("=" * width)
    print("BIOMETRIC DATA ANALYSIS REPORT".center(width))
    print('=' * width)

    #--- DATA COLLECTION & VALIDATION ---
    # Collecting user identity strings
    first_name = input("Enter first name: ").strip().title()
    last_name = input("Enter last name: ").strip().title()
    full_name = f"{first_name} {last_name}"

    # Collecting and validating numeric biometric data
    try:
        age = int(input("Enter current age (years): "))
        height_m = float(input("Enter height in metres: "))
        weight_kg = float(input("Enter weight in kilograms: "))
    except ValueError as a:
        print("\nERROR: Invalid input. Please enter numeric values")
        return
    
    #--- COMPUTATIONAL LOGIC ---
    # Age Calculations: Chronological conversions (standard 365-day year model)
    age_months = age * 12
    age_days = age * 365
    age_hours = age_days * 24

    #Physical dimension conversions
    height_cm = height_m * 100
    height_ft = height_m * 3.28084

    # Health Metrics
    bmi_score = weight_kg / (height_m ** 2)
    bmi_status = get_bmi_category(bmi_score)

    #--- DATA PRESENTATION ---
    print(f"\nReport Generated for: {full_name}")
    print("-" * width)

    # Chronology Data
    print(f"{'Chronology':<20} | {'Metric'}")
    print(f"{'-'*20}-+-{'-'*20}")
    print(f"{'Age in Months':<20} | {age_months:,}")
    print(f"{'Age in Days':<20} | {age_days:,}")
    print(f"{'Age in Hours':<20} | {age_hours:,}")

    # Physical Data
    print(f"\n\n{'Physical Stats':<20} | {'Metric'}")
    print(f"{'-'*20}-+-{'-'*20}")
    print(f"{'Height (cm)':<20} | {height_cm:.2f} cm")
    print(f"{'Height (ft)':<20} | {height_ft:.2f} ft")
    print(f"{'Body Mass Index':<20} | {bmi_score:.2f}")
    print(f"{'Health Status':<20} | {bmi_status}")

    print("-" * width)
    print("End of Report\n")

if __name__ == "__main__":
    main()