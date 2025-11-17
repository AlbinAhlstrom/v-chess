from chess.piece.rook import Rook
from chess.piece.knight import Knight
from chess.piece.bishop import Bishop
from chess.piece.queen import Queen
from chess.piece.king import King
from chess.piece.pawn import Pawn
from chess.piece.color import Color

from chess.board import Board
from chess.game import Game


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

    game = Game()
    while True:
        game.render()
        game.debug_move()


if __name__ == "__main__":
    main()
