from dataclasses import dataclass
from oop_chess.enums import Color, Direction
from oop_chess.piece.piece import Piece


@dataclass(frozen=True)
class Knight(Piece):
    """Knight piece representation.

    Moves two squares in one direction and one square perpendicular.
    """

    moveset = Direction.two_straight_one_sideways()
    MAX_STEPS = 1

    def __str__(self):
        match self.color:
            case Color.WHITE:
                return "♘"
            case Color.BLACK:
                return "♞"

    @property
    def value(self):
        return 3

    @property
    def fen(self):
        return "N" if self.color == Color.WHITE else "n"