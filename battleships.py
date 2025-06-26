import random
import os

def create_board(size):
    return [['~' for _ in range(size)] for _ in range(size)]

def print_board(board, hide_ships=False):
    color_map = {
        '~': '\033[94m~\033[0m',  # Blue water
        'S': '\033[92mS\033[0m',  # Green ship
        'X': '\033[91mX\033[0m',  # Red hit
        'O': '\033[90mO\033[0m'   # Grey miss
    }
    size = len(board)
    columns = "    " + "   ".join(chr(65 + i) if i < 26 else f"({i})" for i in range(size))
    print(columns)
    print("   " + "+___" * size + "+")
    for i, row in enumerate(board):
        display_row = [color_map[cell] if not hide_ships or cell in ('X', 'O') else color_map['~'] for cell in row]
        print(f"{i + 1:2} | " + " | ".join(display_row) + " |")
        print("   " + "+___" * size + "+")

def place_ships(board, num_ships):
    size = len(board)
    ships = []
    while len(ships) < num_ships:
        x, y = random.randint(0, size - 1), random.randint(0, size - 1)
        if board[x][y] == '~':
            board[x][y] = 'S'
            ships.append((x, y))
    return ships

def get_player_move(previous_moves, size):
    while True:
        try:
            move = input("Enter your attack coordinates (e.g., A1, B3) or type 'give up' to surrender: ").upper()
            if move == "GIVE UP":
                return None, None
            if len(move) < 2 or not move[0].isalpha() or not move[1:].isdigit():
                raise ValueError
            x = int(move[1:]) - 1
            y = ord(move[0]) - 65
            if x < 0 or y < 0 or x >= size or y >= size:
                print("Coordinates out of bounds. Try again.")
                continue
            if (x, y) in previous_moves:
                print("You've already attacked this spot. Choose another.")
                continue
            previous_moves.add((x, y))
            return x, y
        except ValueError:
            print("Invalid input. Use format like A1, B2, etc.")

def get_ai_move(size, previous_ai_moves):
    while True:
        x, y = random.randint(0, size - 1), random.randint(0, size - 1)
        if (x, y) not in previous_ai_moves:
            previous_ai_moves.add((x, y))
            return x, y

def make_move(board, x, y, powerup=False):
    hits = [(x, y)]
    if powerup:
        hits.extend([(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)])

    for hit_x, hit_y in hits:
        if 0 <= hit_x < len(board) and 0 <= hit_y < len(board):
            if board[hit_x][hit_y] == 'S':
                board[hit_x][hit_y] = 'X'  # Hit
            elif board[hit_x][hit_y] == '~':
                board[hit_x][hit_y] = 'O'  # Miss

def update_tracking_board(tracking_board, target_board, x, y, powerup=False):
    hits = [(x, y)]
    if powerup:
        hits += [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]

    for hit_x, hit_y in hits:
        if 0 <= hit_x < len(target_board) and 0 <= hit_y < len(target_board):
            if target_board[hit_x][hit_y] == 'X':
                tracking_board[hit_x][hit_y] = 'X'
            elif target_board[hit_x][hit_y] == 'O':
                tracking_board[hit_x][hit_y] = 'O'

def check_winner(board):
    return all(cell != 'S' for row in board for cell in row)

def count_remaining_ships(board):
    return sum(row.count('S') for row in board)

def battleship_game():
    games_played = 0
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("⚓ Welcome to Battleship!")
        mode = input("Choose game mode - '5x5' or '10x10'(enter 5 or 10): ").strip()
        if mode == '5':
            size, num_ships, powerups = 5, 5, 0
        elif mode == '10':
            size, num_ships, powerups = 10, 10, 2
        else:
            print("Invalid choice. Please enter 5 or 10.")
            continue

        player_board = create_board(size)
        ai_board = create_board(size)
        ai_tracking_board = create_board(size)

        place_ships(player_board, num_ships)
        place_ships(ai_board, num_ships)

        previous_player_moves = set()
        previous_ai_moves = set()

        print("Your board:")
        print_board(player_board)

        while True:
            print("\n🧭 Your turn!")
            use_powerup = False
            if powerups > 0:
                choice = input(f"You have {powerups} powerup(s) left. Use one? (y/n): ").strip().lower()
                if choice == 'y':
                    use_powerup = True
                    powerups -= 1

            x, y = get_player_move(previous_player_moves, size)
            if x is None and y is None:
                print("You surrendered! Revealing AI's ships:")
                print_board(ai_board, hide_ships=False)
                break

            make_move(ai_board, x, y, powerup=use_powerup)
            update_tracking_board(ai_tracking_board, ai_board, x, y, powerup=use_powerup)

            print("\n📍 Your tracking board (AI):")
            print_board(ai_tracking_board)

            remaining_ai_ships = count_remaining_ships(ai_board)
            remaining_player_ships = count_remaining_ships(player_board)
            print(f"🚢 AI's remaining ships: {remaining_ai_ships} | Your remaining ships: {remaining_player_ships}")
            print("________________________________________________________")

            if check_winner(ai_board):
                print("🎉 Congratulations! You sank all AI ships!")
                break

            print("\n🤖 AI's turn!")
            x, y = get_ai_move(size, previous_ai_moves)
            make_move(player_board, x, y)

            print("\n📌 Your board:")
            print_board(player_board)

            remaining_ai_ships = count_remaining_ships(ai_board)
            remaining_player_ships = count_remaining_ships(player_board)
            print(f"🚢 AI's remaining ships: {remaining_ai_ships} | Your remaining ships: {remaining_player_ships}")
            print("________________________________________________________")

            if check_winner(player_board):
                print("😞 AI wins! Better luck next time.")
                break

        games_played += 1
        again = input("\nDo you want to play again? (y/n): ").strip().lower()
        if again != 'y':
            print(f"Thanks for playing! You played {games_played} game(s). Goodbye.")
            break

if __name__ == "__main__":
    battleship_game()