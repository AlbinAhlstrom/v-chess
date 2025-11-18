from chess.square import Coordinate
from chess.piece.piece import Piece
from chess.piece.color import Color
from chess.square import Coordinate


class Pawn(Piece):
    """Pawn piece representation.

    Moves forward one square, or two squares if it has not yet moved.
    Diagonal captures and en passant is implemented in Board.legal_moves.
    """

    def __str__(self):
        match self.color:
            case Color.WHITE:
                return "♙"
            case Color.BLACK:
                return "♟"

    @property
    def direction(self) -> int:
        return -1 if self.color.value == 1 else 1

    @property
    def moves(self):
        steps = [self.direction]
        if not self.has_moved:
            steps += [2 * self.direction]

        forward = {
            Coordinate(self.square.row + step, self.square.col)
            for step in steps
            if 0 <= self.square.row + step < 8 and 0 <= self.square.col < 8
        }

        capture_cols = (self.square.col - 1, self.square.col + 1)
        captures = {
            Coordinate(self.square.row + self.direction, col)
            for col in capture_cols
            if 0 <= self.square.row + self.direction < 8 and 0 <= col < 8
        }
        return captures | forward

    @property
    def value(self):
        return 1

    @property
    def en_passant_square(self) -> Coordinate:
        return Coordinate(self.square.row - self.direction, self.square.col)
