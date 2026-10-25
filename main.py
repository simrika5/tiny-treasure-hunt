
import random

GRID_SIZE = 5
MAX_ATTEMPTS = 7
POINTS_PER_WIN = 100


def print_grid():
    print("\n   " + " ".join(str(i) for i in range(1, GRID_SIZE + 1)))
    for row in range(1, GRID_SIZE + 1):
        print(f"{row}  " + " ".join(["⬜"] * GRID_SIZE))


def get_distance(row, col, treasure_row, treasure_col):
    return abs(row - treasure_row) + abs(col - treasure_col)


def play_game():
    treasure_row = random.randint(1, GRID_SIZE)
    treasure_col = random.randint(1, GRID_SIZE)
    attempts_left = MAX_ATTEMPTS
    guessed = set()

    print("\n💎 Welcome to Tiny Treasure Hunt!")
    print("Find the hidden treasure on the 5x5 grid.")
    print(f"You have {MAX_ATTEMPTS} attempts. Good luck!")

    while attempts_left > 0:
        print_grid()
        print(f"\nAttempts left: {attempts_left}")

        try:
            row = int(input("Choose a row (1-5): "))
            col = int(input("Choose a column (1-5): "))
        except ValueError:
            print("Please enter valid whole numbers!")
            continue

        if not (1 <= row <= GRID_SIZE and 1 <= col <= GRID_SIZE):
            print("Coordinates must be between 1 and 5.")
            continue

        if (row, col) in guessed:
            print("You already searched there. Try another spot!")
            continue

        guessed.add((row, col))
        attempts_left -= 1

        if (row, col) == (treasure_row, treasure_col):
            score = max(
                10, POINTS_PER_WIN - (MAX_ATTEMPTS - attempts_left - 1) * 15
            )
            print("\n🎉 YOU FOUND THE TREASURE! 💎")
            print(f"Your score: {score}")
            return score

        distance = get_distance(
            row, col, treasure_row, treasure_col
        )

        if distance <= 1:
            print("🔥 Burning hot! The treasure is very close!")
        elif distance <= 3:
            print("🌤️ Getting warmer!")
        else:
            print("🥶 Cold! Search somewhere else.")

    print("\n💀 Game over! You ran out of attempts.")
    print(
        f"The treasure was at row {treasure_row}, "
        f"column {treasure_col}."
    )
    return 0


def main():
    total_score = 0

    while True:
        total_score += play_game()
        print(f"\n🏆 Total score: {total_score}")

        again = input("\nPlay again? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing! Happy treasure hunting! 💎")
            break


if __name__ == "__main__":
    main()

