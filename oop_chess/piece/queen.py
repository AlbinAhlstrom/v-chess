from dataclasses import dataclass
from oop_chess.piece.piece import Piece
from oop_chess.enums import Color, Direction


@dataclass(frozen=True)
class Queen(Piece):
    """Queen piece representation.

    Moves any number of squares, straight or diagonally.
    """



    moveset = Direction.straight_and_diagonal()

    def __str__(self):
        match self.color:
            case Color.WHITE:
                return "♕"
            case Color.BLACK:
                return "♛"

    @property
    def value(self):
        return 9

    @property
    def fen(self):
        return "Q" if self.color == Color.WHITE else "q"
