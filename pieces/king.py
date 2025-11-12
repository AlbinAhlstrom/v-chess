from math import inf

from board import Color
from pieces import Piece


class King(Piece):
    def __str__(self):
        match self.color:
            case Color.WHITE:
                return "♔"
            case Color.BLACK:
                return "♚"

    def moves():
        pass

    @property
    def value(self):
        return inf
