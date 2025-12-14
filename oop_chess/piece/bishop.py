from dataclasses import dataclass
from oop_chess.piece.piece import Piece
from oop_chess.enums import Color, Direction


@dataclass(frozen=True)
class Bishop(Piece):
    """Bishop piece representation.

    Moves any number of squares diagonally.
    """

    moveset = Direction.diagonal()

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
    def fen(self):
        return "B" if self.color == Color.WHITE else "b"