from dataclasses import dataclass

from v_chess.piece.piece import Piece
from v_chess.enums import Color, Direction


@dataclass(frozen=True)
class Rook(Piece):
    """Rook piece representation.

    Moves any number of squares horizontally or vertically.
    """
    @property
    def moveset(self):
        return Direction.straight()

    def __str__(self) -> str:
        match self.color:
            case Color.WHITE:
                return "♖"
            case Color.BLACK:
                return "♜"

    @property
    def value(self):
        return 5

    @property
    def fen(self):
        return "R" if self.color == Color.WHITE else "r"

