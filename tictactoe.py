import math  # math.inf gives us "infinity" - a starting point that any real score will beat

# ============================================================
# THE BOARD
# ============================================================
# The board is just a list of 9 spaces, representing a 3x3 grid like this:
#
#   Index layout:        Example after some moves:
#   0 | 1 | 2               X |   | O
#   ---------               ---------
#   3 | 4 | 5                 | X |
#   ---------               ---------
#   6 | 7 | 8               O |   | X
#
# " " means the cell is empty.
board = [" " for _ in range(9)]

HUMAN = "X"
AI = "O"


def print_board():
    """Just displays the board nicely. No AI logic here — purely visual."""
    print()
    for i in range(3):
        row = board[i * 3: i * 3 + 3]
        print(" " + " | ".join(row))
        if i < 2:
            print("---+---+---")
    print()


def available_moves():
    """Returns a list of index numbers for every empty cell on the board."""
    return [i for i, cell in enumerate(board) if cell == " "]


def check_winner(b, player):
    """
    Checks if 'player' (either HUMAN or AI) has 3 in a row anywhere:
    across, down, or diagonally. Returns True/False.
    """
    win_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # the 3 rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # the 3 columns
        [0, 4, 8], [2, 4, 6]              # the 2 diagonals
    ]
    # Check each winning pattern - if all 3 cells in ANY pattern belong
    # to the same player, that player has won.
    return any(all(b[i] == player for i in combo) for combo in win_combinations)


def is_full(b):
    """True if there are no empty cells left (board is full = draw territory)."""
    return " " not in b


# ============================================================
# THE BRAIN OF THE AI: MINIMAX + ALPHA-BETA PRUNING
# ============================================================
#
# THE BIG IDEA:
# The AI doesn't follow fixed rules like "if corner is empty, take it."
# Instead, it imagines EVERY possible way the rest of the game could play
# out, assuming both players always play their best possible move.
# Then it picks whichever move leads to the best guaranteed result for itself.
#
# HOW IT "IMAGINES" THE FUTURE (RECURSION):
# This function calls ITSELF over and over, each time with one more move
# played on the board. Think of it like a chain of questions:
#   "If I play here, what's the opponent's best reply?"
#     -> "If they play there, what's MY best reply to that?"
#        -> "If I play there, what's THEIR best reply to that?"
#           ... and so on until the board is full or someone wins.
# Each "question" in that chain is just this same function being called
# again with a slightly more filled-in board. That's recursion.
#
# SCORING:
#   AI wins    -> score of  +1  (good for AI)
#   Human wins -> score of  -1  (bad for AI)
#   Draw       -> score of   0  (neutral)
#
# is_maximizing tells us whose turn it is in this imagined future:
#   True  -> AI's turn   -> AI wants the HIGHEST score possible
#   False -> Human's turn -> Human wants the LOWEST score possible
#   (This back-and-forth of "maximize / minimize" is where the name
#   "Minimax" comes from.)
#
# ALPHA-BETA PRUNING (the speed shortcut):
#   alpha = the best score the AI can already guarantee so far
#   beta  = the best (lowest) score the human can already guarantee so far
#   If at any point beta <= alpha, it means: "the opponent would never
#   actually let the game reach this branch" - so we stop exploring it
#   early. This doesn't change the final decision, it just saves time
#   by skipping branches that could never happen anyway.
def minimax(b, depth, is_maximizing, alpha, beta):
    # --- Base cases: the "end" of an imagined game, stop recursing ---
    if check_winner(b, AI):
        return 1
    if check_winner(b, HUMAN):
        return -1
    if is_full(b):
        return 0

    if is_maximizing:
        # It's the AI's imagined turn - try every empty cell,
        # play it temporarily, ask "what happens next?" (recursion),
        # then undo the move (this is called "backtracking").
        best_score = -math.inf
        for move in available_moves():
            b[move] = AI               # try the move
            score = minimax(b, depth + 1, False, alpha, beta)  # ask: what next?
            b[move] = " "               # undo the move (backtrack)
            best_score = max(best_score, score)
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break  # prune: opponent would avoid letting us reach here
        return best_score
    else:
        # It's the (imagined) human's turn - same idea, but they want
        # the LOWEST score, since a low score is bad for the AI.
        best_score = math.inf
        for move in available_moves():
            b[move] = HUMAN
            score = minimax(b, depth + 1, True, alpha, beta)
            b[move] = " "
            best_score = min(best_score, score)
            beta = min(beta, best_score)
            if beta <= alpha:
                break  # prune: AI would avoid letting the game reach here
        return best_score


def best_ai_move():
    """
    This is what actually gets called during the real game.
    It tries every possible move for the AI on the REAL board,
    uses minimax() to see how that move plays out in every imagined
    future, and picks whichever move scores the highest.
    """
    best_score = -math.inf
    move = None
    for i in available_moves():
        board[i] = AI
        # False = after AI's move, it's the human's turn next in the simulation
        score = minimax(board, 0, False, -math.inf, math.inf)
        board[i] = " "  # undo, since we were only testing this move
        if score > best_score:
            best_score = score
            move = i
    return move


# ============================================================
# HUMAN INPUT + GAME LOOP (no AI logic here, just normal Python)
# ============================================================
def get_human_move():
    """Asks the human for row and column, converts it to a board index (0-8)."""
    while True:
        try:
            row = int(input("Enter row (1-3): ")) - 1
            col = int(input("Enter column (1-3): ")) - 1
            index = row * 3 + col
            if row not in range(3) or col not in range(3):
                print("Please enter numbers between 1 and 3.")
            elif board[index] != " ":
                print("That cell is already taken. Try again.")
            else:
                return index
        except ValueError:
            print("Invalid input. Please enter numbers only.")


def play_game():
    print("Welcome to Tic-Tac-Toe!")
    print("You are 'X', the AI is 'O'.")
    print("This AI is unbeatable — best you can do is draw!")
    print_board()

    while True:
        # ---- Human's turn ----
        human_index = get_human_move()
        board[human_index] = HUMAN
        print_board()

        if check_winner(board, HUMAN):
            print("🎉 You won! (This shouldn't be possible against a perfect AI 👀)")
            break
        if is_full(board):
            print("It's a draw!")
            break

        # ---- AI's turn ----
        print("AI is thinking...")
        ai_index = best_ai_move()   # this is where minimax runs
        board[ai_index] = AI
        print_board()

        if check_winner(board, AI):
            print("🤖 AI wins! Better luck next time.")
            break
        if is_full(board):
            print("It's a draw!")
            break


if __name__ == "__main__":
    play_game()
