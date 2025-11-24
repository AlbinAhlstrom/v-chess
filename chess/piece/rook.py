from chess.piece.sliding_piece import SlidingPiece
from chess.piece.color import Color
from chess.move_utils import Moveset


class Rook(SlidingPiece):
    """Rook piece representation.

    Moves any number of squares horizontally or vertically.
    """

    moveset = Moveset.STRAIGHT

    def __str__(self):
        match self.color:
            case Color.WHITE:
                return "♖"
            case Color.BLACK:
                return "♜"

    @property
    def value(self):
        return 5

    @property
    def char(self):
        return "R" if self.color == Color.WHITE else "r"
