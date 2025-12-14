from math import inf
from dataclasses import dataclass

from oop_chess.piece.piece import Piece
from oop_chess.enums import Color, Direction


@dataclass(frozen=True)
class King(Piece):
    """King piece representation.

    Moves one square in any direction.
    """
    MAX_STEPS = 1

    @property
    def moveset(self):
        return Direction.straight_and_diagonal()

    def __str__(self):
        match self.color:
            case Color.WHITE:
                return "♔"
            case Color.BLACK:
                return "♚"

    @property
    def value(self):
        return inf

    @property
    def fen(self):
        return "K" if self.color == Color.WHITE else "k"
