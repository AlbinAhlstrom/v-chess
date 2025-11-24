from chess.piece.sliding_piece import SlidingPiece
from chess.piece.color import Color
from chess.move_utils import Moveset


class Bishop(SlidingPiece):
    """Bishop piece representation.

    Moves any number of squares diagonally.
    """

    moveset = Moveset.DIAGONAL

    def __str__(self):
        match self.color:
            case Color.WHITE:
                return "♗"
            case Color.BLACK:
                return "♝"

    @property
    def value(self):
        return 3

    @property
    def char(self):
        return "B" if self.color == Color.WHITE else "b"
