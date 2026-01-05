from dataclasses import dataclass

from v_chess.square import Square
from v_chess.enums import Color, Direction
from v_chess.piece.piece import Piece


@dataclass(frozen=True)
class Pawn(Piece):
    """Pawn piece representation.

    Moves forward one square.
    Double move and diagonal captures are handled by logic external to the basic moveset.
    """
    MAX_STEPS = 1

    @property
    def moveset(self) -> set[Direction]:
        if self.color == Color.WHITE:
            return Direction.up_straight_or_diagonal()
        else:
            return Direction.down_straight_or_diagonal()

    @property
    def direction(self) -> Direction:
        """Which direction the piece moves in (up for white and down for black)."""
        if self.color == Color.WHITE:
            return Direction.UP
        else:
            return Direction.DOWN

    @property
    def promotion_row(self) -> int:
        return 0 if self.color == Color.WHITE else 7

    def capture_paths(self, start: Square) -> list[list[Square]]:
        return [[sq] for sq in self.theoretical_moves(start) if sq.col != start.col]

    def __str__(self):
        match self.color:
            case Color.WHITE:
                return "♙"
            case Color.BLACK:
                return "♟"

    @property
    def value(self):
        return 1

    @property
    def fen(self):
        return "P" if self.color == Color.WHITE else "p"

