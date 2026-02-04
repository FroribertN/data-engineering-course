"""
PROGRAM: Temperature Converter
---------------------------------------
PURPOSE: 
    Convert temperatures between Celsius, Fahrenheit, and Kelvin 
    while validating against absolute zero limits.

REQUIREMENTS:
    - User menu for selection (1-4).
    - Validation for physical temperature boundaries.
    - Result output formatted to two decimal places.
"""

# --- GLOBAL CONSTANTS (Thermodynamic Limits) ---
ABSOLUTE_ZERO_CELSIUS = -273.15
ABSOLUTE_ZERO_FAHRENHEIT = -459.67
ABSOLUTE_ZERO_KELVIN = 0.0

# Header Display
print('=' * 50)
print('TEMPERATURE CONVERTER'.center(50))
print('=' * 50)

# 1. Display Conversion Menu
print('\nPlease select a conversion option:')
print('1. Celsius to Fahrenheit and Kelvin')
print('2. Fahrenheit to Celsius and Kelvin')
print('3. Kelvin to Celsius and Fahrenheit')
print('4. Comprehensive Report (Convert given value to all scales)')

try:
    # 2. Capture and validate user menu selection
    menu_selection = int(input('\nEnter choice (1-4): '))

    if 1 <= menu_selection <= 4:
        
        # 3. Handle Targeted Conversions (Options 1, 2, and 3)
        if menu_selection == 1:
            input_celsius = float(input('Enter temperature in Celsius: '))
            if input_celsius < ABSOLUTE_ZERO_CELSIUS:
                print(f'Error: Temperature is below Absolute Zero ({ABSOLUTE_ZERO_CELSIUS}°C)')
            else:
                fahrenheit_result = (input_celsius * 9/5) + 32
                kelvin_result = input_celsius + 273.15
                print(f'\nResults for {input_celsius:.2f}°C:')
                print(f'- Fahrenheit: {fahrenheit_result:.2f}°F')
                print(f'- Kelvin:     {kelvin_result:.2f}K')

        elif menu_selection == 2:
            input_fahrenheit = float(input('Enter temperature in Fahrenheit: '))
            if input_fahrenheit < ABSOLUTE_ZERO_FAHRENHEIT:
                print(f'Error: Temperature is below Absolute Zero ({ABSOLUTE_ZERO_FAHRENHEIT}°F)')
            else:
                celsius_result = (input_fahrenheit - 32) * 5/9
                kelvin_result = celsius_result + 273.15
                print(f'\nResults for {input_fahrenheit:.2f}°F:')
                print(f'- Celsius: {celsius_result:.2f}°C')
                print(f'- Kelvin:  {kelvin_result:.2f}K')

        elif menu_selection == 3:
            input_kelvin = float(input('Enter temperature in Kelvin: '))
            if input_kelvin < ABSOLUTE_ZERO_KELVIN:
                print(f'Error: Temperature is below Absolute Zero ({ABSOLUTE_ZERO_KELVIN}K)')
            else:
                celsius_result = input_kelvin - 273.15
                fahrenheit_result = (celsius_result * 9/5) + 32
                print(f'\nResults for {input_kelvin:.2f}K:')
                print(f'- Celsius:    {celsius_result:.2f}°C')
                print(f'- Fahrenheit: {fahrenheit_result:.2f}°F')

        # 4. Handle Comprehensive Analysis (Option 4)
        elif menu_selection == 4:
            print('\nSelect Input Scale:\n1. Celsius\n2. Fahrenheit\n3. Kelvin')
            scale_type = int(input('Choice: '))
            source_value = float(input('Enter temperature value: '))

            # Initialize variables for the final report
            final_c, final_f, final_k = None, None, None

            if scale_type == 1 and source_value >= ABSOLUTE_ZERO_CELSIUS:
                final_c = source_value
                final_f = (source_value * 9/5) + 32
                final_k = source_value + 273.15
            elif scale_type == 2 and source_value >= ABSOLUTE_ZERO_FAHRENHEIT:
                final_f = source_value
                final_c = (source_value - 32) * 5/9
                final_k = final_c + 273.15
            elif scale_type == 3 and source_value >= ABSOLUTE_ZERO_KELVIN:
                final_k = source_value
                final_c = source_value - 273.15
                final_f = (final_c * 9/5) + 32
            else:
                print('\n[!] Error: Invalid scale or value below Absolute Zero.')

            if final_c is not None:
                print('\n--- COMPREHENSIVE SCALE REPORT ---')
                print(f'Celsius:    {final_c:.2f}°C')
                print(f'Fahrenheit: {final_f:.2f}°F')
                print(f'Kelvin:     {final_k:.2f}K')
                print('-' * 34)

    else:
        print('\n[!] Selection Error: Please choose a valid menu number (1-4).')

except ValueError:
    print('\n[!] Data Error: Numeric values are required for this utility.')

print('\n' + '=' * 50)
print('TERMINATING CONVERTER UTILITY'.center(50))
print('=' * 50)