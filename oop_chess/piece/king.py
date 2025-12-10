from math import inf

from oop_chess.piece.piece import Piece
from oop_chess.enums import Color, Direction
from oop_chess.square import Square


class King(Piece):
    """King piece representation.

    Moves one square in any direction.
    Special rules for castling and check are implemented in Board.legal_move.
    """

    moveset = Direction.straight_and_diagonal()
    MAX_STEPS = 1
    CASTLING_MAX_STEPS = 2

    def _max_steps(self, direction):
        """Allow moving two squares when castling."""
        if direction in (Direction.LEFT, Direction.RIGHT) and not self.has_moved:
            return self.CASTLING_MAX_STEPS
        else:
            return self.MAX_STEPS

    @property
    def theoretical_move_paths(self) -> list[list[Square]]:
        """Theoretical move paths adjusted to allow for castling."""
        return [direction.get_path(self.square, self._max_steps(direction)) for direction in self.moveset]

    @property
    def capture_squares(self) -> list[Square]:
        return [
            square
            for direction in self.moveset
            for square in direction.get_path(self.square, self.MAX_STEPS)
        ]

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
