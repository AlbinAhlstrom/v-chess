from pieces import Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook, Pawn
from chess.board import Board


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
    for row in board.board:
        row = [char or 0 for char in row]
        print(row)


if __name__ == "__main__":
    main()
