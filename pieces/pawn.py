from board import Color, Coordinate
from pieces import Piece


class Pawn(Piece):
    """Pawn piece representation.

    Moves forward one square, or two squares if it has not yet moved.
    Diagonal captures and en passant is implemented in Board.legal_moves.
    """

    def __str__(self):
        match self.color:
            case Color.WHITE:
                return "♙"
            case Color.BLACK:
                return "♟"

    def moves(self):
        pos = self.position
        match self.color:
            case Color.WHITE:
                move_offsets = (-1,) if self.has_moved else (-1, -2)
            case Color.BLACK:
                move_offsets = (1,) if self.has_moved else (1, 2)

        return {Coordinate(pos.row + move, pos.col) for move in move_offsets}

    @property
    def value(self):
        return 1
