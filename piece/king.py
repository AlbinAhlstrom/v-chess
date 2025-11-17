from math import inf

from .piece import Piece, Color


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
        moves = straight_moves(self) | diagonal_moves(self)
        return limit_distance(self, moves, 1)

    @property
    def value(self):
        return inf
