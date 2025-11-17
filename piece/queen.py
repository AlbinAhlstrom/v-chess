from chess.piece.piece import Piece
from chess.piece.color import Color


class Queen(Piece):
    """Queen piece representation.

    Moves any number of squares, straight or diagonally.
    """

    def __str__(self):
        match self.color:
            case Color.WHITE:
                return "♕"
            case Color.BLACK:
                return "♛"

    @property
    def moves(self):
        return straight_moves(self) | diagonal_moves(self)

    @property
    def value(self):
        return 9
