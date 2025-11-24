from chess.piece.sliding_piece import SlidingPiece
from chess.piece.color import Color
from chess.move_utils import Moveset


class Queen(SlidingPiece):
    """Queen piece representation.

    Moves any number of squares, straight or diagonally.
    """

    moveset = Moveset.STRAIGHT_AND_DIAGONAL

    def __str__(self):
        match self.color:
            case Color.WHITE:
                return "♕"
            case Color.BLACK:
                return "♛"

    @property
    def value(self):
        return 9

    @property
    def char(self):
        return "Q" if self.color == Color.WHITE else "q"
