from board import Color, Coordinate
from pieces import Piece


class Pawn(Piece):
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
                move_offsets = (-1) if self.has_moved else (-1, -2)
            case Color.BLACK:
                move_offsets = (1) if self.has_moved else (1, 2)

        return {Coordinate(pos.row + move, pos.col) for move in move_offsets}

    @property
    def value(self):
        return 1
