from chess.square import Square
from chess.enums import Color, Direction, Moveset
from chess.piece.piece import Piece


class Pawn(Piece):
    """Pawn piece representation.

    Moves forward one square, or two squares if it has not yet moved.
    Diagonal captures and en passant is implemented in Board.legal_moves.
    """

    MOVESET = Moveset.CUSTOM

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
    def capture_squares(self) -> list[Square]:
        if self.square is None:
            raise AttributeError("Can't capture using a piece with no square")

        valid_capture_squares = []
        for direction in self.capture_moveset.value:
            d_col, d_row = direction.value
            new_row = self.square.row + d_row
            new_col = self.square.col + d_col

            if Square.is_valid(new_row, new_col):
                valid_capture_squares.append(self.square.adjacent(direction))

        return valid_capture_squares

    @property
    def forward_squares(self) -> list[Square]:
        if self.square is None:
            raise AttributeError("Can't capture using a piece with no square")

        squares = [self.square.adjacent(self.direction)]
        if not self.has_moved and squares[0] is not None:
            squares += [squares[0].adjacent(self.direction)]
        return [sq for sq in squares if sq is not None]

    @property
    def theoretical_move_paths(self):
        """Array of coordinates reachable when moving in all directions"""
        return [self.forward_squares, [square for square in self.capture_squares]]

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
