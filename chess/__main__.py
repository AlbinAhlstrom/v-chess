from chess.board import Board
from chess.move import Move


def make_move(uci_str: str, board: Board):
    move = Move.from_uci(uci_str)
    board.make_move(move)


def render(board: Board):
    grid = [[board.get_piece((r, c)) or 0 for c in range(8)] for r in range(8)]
    for row in grid:
        print([f"{piece}" for piece in row])


def main():
    """Set up and print the initial chess board.

    This function initializes an 8x8 chess board with all pieces in their
    standard starting positions. It prints the board layout using unicode
    characters for pieces and 0 for empty squares.

    printed output:
        [♜, ♞, ♝, ♛, ♚, ♝, ♞, ♜]
        [♟, ♟, ♟, ♟, ♟, ♟, ♟, ♟]
        [0, 0, 0, 0, 0, 0, 0, 0]
        [0, 0, 0, 0, 0, 0, 0, 0]
        [0, 0, 0, 0, 0, 0, 0, 0]
        [0, 0, 0, 0, 0, 0, 0, 0]
        [♙, ♙, ♙, ♙, ♙, ♙, ♙, ♙]
        [♖, ♘, ♗, ♕, ♔, ♗, ♘, ♖]
    """

    board = Board.starting_setup()
    while True:
        render(board)
        print(f"Player to move: {board.player_to_move}")
        uci_str = input("Enter a move: ")
        make_move(uci_str, board)


if __name__ == "__main__":
    main()
