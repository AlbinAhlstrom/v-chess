from chess.piece.piece import Piece
from chess.piece.color import Color
from chess.move_utils import Moveset


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
        return self.get_lines(Moveset.STRAIGHT_AND_DIAGONAL)

    @property
    def value(self):
        return 9
