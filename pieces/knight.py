from board import Color
from pieces import Piece


class Knight(Piece):
    def __str__(self):
        match self.color:
            case Color.WHITE:
                return "♘"
            case Color.BLACK:
                return "♞"

    @property
    def value(self):
        return 3
