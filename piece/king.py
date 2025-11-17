from math import inf

from .piece import Piece, Color
from chess.square import Square


class King(Piece):
    """King piece representation.

    Moves one square in any direction.
    Special rules for castling and check are implemented in Board.legal_move.
    """

    def __str__(self):
        match self.color:
            case Color.WHITE:
                return "♔"
            case Color.BLACK:
                return "♚"

    @property
    def moves(self):
        row, col = self.square.row, self.square.col

        return {
            Square((r, c))
            for r in range(row - 1, row + 2)
            for c in range(col - 1, col + 2)
            if 0 <= r < 8 and 0 <= c < 8 and (r, c) != (row, col)
        }

    @property
    def value(self):
        return inf
