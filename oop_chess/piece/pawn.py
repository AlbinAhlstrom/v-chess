from oop_chess.square import Square
from oop_chess.enums import Color, Direction
from oop_chess.piece.piece import Piece


class Pawn(Piece):
    """Pawn piece representation.

    Moves forward one square, or two squares if it has not yet moved.
    Diagonal captures and en passant is implemented in Board.legal_moves.
    """

    MAX_STEPS = 1
    FIRST_MOVE_MAX_STEPS = 2

    @property
    def moveset(self) -> set[Direction]:
        if self.color == Color.WHITE:
            return Direction.up_straight_or_diagonal()
        else:
            return Direction.down_straight_or_diagonal()

    @property
    def start_rank(self) -> int:
        return 6 if self.color == Color.WHITE else 1

    @property
    def is_on_first_or_last_row(self) -> bool:
        """Return true if not on first or last rank."""
        return not 0 < self.square.row < 7

    @property
    def direction(self) -> Direction:
        if self.color == Color.WHITE:
            return Direction.UP
        else:
            return Direction.DOWN

    @property
    def promotion_row(self) -> int:
        return 0 if self.color == Color.WHITE else 7

    @property
    def capture_squares(self) -> list[Square]:
        return [square for square in self.theoretical_moves if square.col != self.square.col]

    def max_steps(self, direction: Direction) -> int:
        """Allow moving two squares forward on first move."""
        if direction == self.direction and not self.has_moved:
            return self.FIRST_MOVE_MAX_STEPS
        else:
            return self.MAX_STEPS

    @property
    def theoretical_move_paths(self) -> list[list[Square]]:
        """Theoretical move paths adjusted to allow for castling."""
        return [direction.get_path(self.square, self.max_steps(direction)) for direction in self.moveset]

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
