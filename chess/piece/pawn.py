from itertools import chain
from chess.coordinate import Square
from chess.enums import Color, Direction, Moveset
from chess.piece.piece import Piece


class Pawn(Piece):
    """Pawn piece representation.

    Moves forward one square, or two squares if it has not yet moved.
    Diagonal captures and en passant is implemented in Board.legal_moves.
    """

    MOVESET = Moveset.CUSTOM
    MAX_SQUARES = 1

    @property
    def direction(self) -> Direction:
        if self.color == Color.WHITE:
            return Direction.UP
        else:
            return Direction.DOWN

    @property
    def capture_moveset(self) -> Moveset:
        if self.color == Color.WHITE:
            return Moveset.PAWN_WHITE_CAPTURE
        else:
            return Moveset.PAWN_BLACK_CAPTURE

    @property
    def max_squares_forward(self) -> int:
        return 1 if self.has_moved else 2

    @property
    def all_directions_array(self):
        """Array of coordinates reachable when moving in all directions"""
        captures = self.capture_moveset.value
        max = self.MAX_SQUARES
        max_forward = 1 if self.has_moved else 2

        forward = self._get_moves_in_direction(self.direction, max_forward)
        captures = [self._get_moves_in_direction(dir, max) for dir in captures]
        return [forward, *captures]

    @property
    def pseudo_legal_moves(self) -> list[Square]:
        """All moves legal on an empty board"""
        return list(chain.from_iterable(self.all_directions_array))

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
