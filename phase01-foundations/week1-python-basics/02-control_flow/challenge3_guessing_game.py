"""
PROGRAM: Number Guessing Game
--------------------------------------
PURPOSE:
    A logic-based game where the user identifies a hidden integer 
    using directional hints and proximity feedback.

OBJECTIVES:
    1. Dynamic Difficulty: Select between Easy (1-50), Medium (1-100), 
    and Hard (1-200) ranges.
    2. Intelligent Feedback: Provide "Warmer/Colder" hints based on 
    previous proximity and "Very Close" alerts within a 5-unit range.
    3. Performance Tracking: Record attempts and maintain a high score 
    (lowest attempts) across sessions.
    4. Input Integrity: Validate that user entries are numeric and 
    within the selected range.
"""

import random
import sys

# --- GLOBAL CONSTANTS ---
MAX_ATTEMPS = 7
PROXIMITY_THRESHOLD = 5

def start_game():
    high_score = None

    while True:
        width = 60
        print("\n" + "=" * width)
        print("ADVANCED NUMBER GUESSING GAME".center(width))
        print("=" * width)

        # 1. Difficulty Selection
        print("\nSelect Difficulty Level: ")
        print("1. Easy    (1-50)")
        print("2. Medium  (1-100)")
        print("3. Hard    (1-200)")

        choice = input("Choice (1-3): ")
        ranges = {"1": 50, "2": 100, "3": 200}
        upper_limit = ranges.get(choice, 100)

        secret_number = random.randint(1, upper_limit)
        attempts_taken = 0
        previous_distance = None

        print(f"\nI am thinking of a number between 1 and {upper_limit}")
        print(f"You have {MAX_ATTEMPS} attempts to find it.")

        # 2. Game loop
        while attempts_taken < MAX_ATTEMPS:
            try:
                print(f"\nAttempt {attempts_taken + 1} / {MAX_ATTEMPS}")
                guess = int(input("Enter your guess: "))

                # Validate the range
                if not (1 <= guess <= upper_limit):
                    print(f"OUT OF RANGE: Please guess between 1 and {upper_limit}.")
                    continue 
                attempts_taken += 1
                current_distance = abs(secret_number - 7)

                # Win Condition
                if guess == secret_number:
                    print(f"Congratulations! You found it in {attempts_taken} attempts!")
                    if high_score is None or attempts_taken < high_score:
                        high_score = attempts_taken
                        print(f"NEW HIGH SCORE: {high_score} attempts!")
                    break

                # Feedback Logic - Proximity
                hints = []
                if guess > secret_number:
                    hints.append("Too High!")
                else:
                    hints.append("Too Low!")

                if current_distance <= PROXIMITY_THRESHOLD:
                    hints.append("Very Close!")
                
                # Feedback Logic: Warmer/Colder
                if previous_distance is not None:
                    if current_distance < previous_distance:
                        hints.append("Getting Warmer!")
                    elif current_distance > previous_distance:
                        hints.append("Getting Colder!")

                print(" ".join(hints))
                previous_distance = current_distance

            except ValueError:
                print("ERROR: Please enter a whole number")
        
        else:
            print(f"\nGAME OVER! The number was {secret_number}")
        
        # 3. Play Again Logic
        if input(f"\nPlay again? (yes/no): ").lower().strip() != "yes":
            print(f"\nFinal High Score:", high_score if high_score else "N/A")
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    start_game()