"""
PROGRAM: Compound Interest Analysis
-----------------------------------------------------
PURPOSE:
    A financial utility to calculate and compare investment growth 
    under Compound vs. Simple Interest models.

FORMULAS:
    - Compound Interest: A = P(1 + r/n)^(nt)
    - Simple Interest:   A = P(1 + rt)

"""

import sys

# --- GLOBAL CONSTANTS ---
DAYS_PER_YEAR = 365
MONTHS_PER_YEAR = 12
QUARTERS_PER_YEAR = 4

# Header Display
print("=" * 70)
print("FINANCIAL GROWTH ANALYSER".center(70))
print("=" * 70)

try:
    # --- DATA COLLECTION ---
    print("\n[ INPUT PARAMETERS ]")
    initial_principal = float(input("Initial Investment Amount ($): "))
    annual_rate_percent = float(input("Annual Interest Rate (%): "))
    investment_years = float(input("Investment Period (Years): "))

    print("\nCompounding Frequency Options:")
    print("1. Annually  (1x/yr)")
    print("2. Quarterly (4x/yr)")
    print("3. Monthly   (12x/yr)")
    print("4. Daily     (365x/yr)")
    
    frequency_selection = input("Select Frequency (1-4): ").strip()

    # Mapping Selection to Descriptive Names and Frequencies
    frequency_map = {
        '1': ("Annually", 1),
        '2': ("Quarterly", QUARTERS_PER_YEAR),
        '3': ("Monthly", MONTHS_PER_YEAR),
        '4': ("Daily", DAYS_PER_YEAR)
    }

    # Default logic for invalid input
    frequency_label, compound_frequency = frequency_map.get(frequency_selection, ("Monthly", MONTHS_PER_YEAR))
    
    # --- COMPUTATIONAL LOGIC ---
    annual_rate_decimal = annual_rate_percent / 100

    # Compound Interest Calculation
    # A = P(1 + r/n)^(nt)
    final_compound_balance = initial_principal * (1 + annual_rate_decimal / compound_frequency) ** (compound_frequency * investment_years)
    total_compound_interest = final_compound_balance - initial_principal

    # Simple Interest Calculation (For Benchmarking)
    # A = P(1 + rt)
    final_simple_balance = initial_principal * (1 + annual_rate_decimal * investment_years)
    total_simple_interest = final_simple_balance - initial_principal

    # Comparative Metrics
    compound_advantage = total_compound_interest - total_simple_interest
    total_percentage_gain = (total_compound_interest / initial_principal) * 100

    # --- RESULTS SUMMARY ---
    print("\n" + "=" * 70)
    print("INVESTMENT PERFORMANCE SUMMARY".center(70))
    print("=" * 70)
    
    print(f"{'Investment Principal:':<25} ${initial_principal:,.2f}")
    print(f"{'Interest Rate:':<25} {annual_rate_percent}%")
    print(f"{'Duration:':<25} {investment_years} Years")
    print(f"{'Compounding Logic:':<25} {frequency_label} ({compound_frequency} iterations/year)")
    
    print("-" * 70)
    print(f"{'FINAL COMPOUND BALANCE:':<25} ${final_compound_balance:,.2f}")
    print(f"{'Interest Earned:':<25} ${total_compound_interest:,.2f}")
    print(f"{'Total Percentage Gain:':<25} {total_percentage_gain:.2f}%")
    
    print("-" * 70)
    print(f"{'Simple Interest Bench:':<25} ${final_simple_balance:,.2f}")
    print(f"{'Compound Advantage:':<25} ${compound_advantage:,.2f} extra earned")
    print("-" * 70)

    # --- FREQUENCY COMPARISON TABLE ---
    print("\n" + "=" * 70)
    print("IMPACT OF COMPOUNDING FREQUENCY".center(70))
    print("=" * 70)
    print(f"{'Frequency':<15} | {'Final Balance':<20} | {'Interest Earned':<20}")
    print("-" * 70)

    for label, freq in [("Annually", 1), ("Quarterly", 4), ("Monthly", 12), ("Daily", 365)]:
        bal = initial_principal * (1 + annual_rate_decimal / freq) ** (freq * investment_years)
        interest = bal - initial_principal
        print(f"{label:<15} | ${bal:>19,.2f} | ${interest:>19,.2f}")

    # --- YEAR-BY-YEAR PROJECTION ---
    print("\n" + "=" * 70)
    print("ANNUAL GROWTH PROJECTION".center(70))
    print("=" * 70)
    print(f"{'Year':<6} | {'Year-End Balance':<20} | {'Annual Interest':<18} | {'Total Gain':<18}")
    print("-" * 72)

    previous_year_balance = initial_principal

    # Handle full years
    for year in range(1, int(investment_years) + 1):
        current_year_balance = initial_principal * (1 + annual_rate_decimal / compound_frequency) ** (compound_frequency * year)
        interest_this_year = current_year_balance - previous_year_balance
        cumulative_gain = current_year_balance - initial_principal
        
        print(f"{year:<6} | ${current_year_balance:>19,.2f} | ${interest_this_year:>17,.2f} | ${cumulative_gain:>17,.2f}")
        previous_year_balance = current_year_balance

    # Handle final fractional period (if applicable)
    if investment_years % 1 != 0:
        interest_final_period = final_compound_balance - previous_year_balance
        cumulative_gain_final = final_compound_balance - initial_principal
        print(f"{investment_years:<6} | ${final_compound_balance:>19,.2f} | ${interest_final_period:>17,.2f} | ${cumulative_gain_final:>17,.2f}")

    print("=" * 70)
    print("ANALYSIS COMPLETE".center(70))
    print("=" * 70)

except ValueError:
    print("\n[CRITICAL ERROR]: Invalid numerical input. Calculation aborted.")
    sys.exit()