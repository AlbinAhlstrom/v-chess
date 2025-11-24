from chess.square import Coordinate
from chess.piece.piece import Piece
from chess.piece.color import Color


class Knight(Piece):
    """Knight piece representation.

    Moves two squares in one direction and one square perpendicular.
    """

    def __str__(self):
        match self.color:
            case Color.WHITE:
                return "♘"
            case Color.BLACK:
                return "♞"

    @property
    def moves(self):
        offsets = (-2, -1, 1, 2)
        return {
            Coordinate(self.square.row + row_offset, self.square.col + column_offset)
            for row_offset in offsets
            for column_offset in offsets
            if abs(row_offset) != abs(column_offset)
            and 0 <= self.square.row + row_offset < 8
            and 0 <= self.square.col + column_offset < 8
        }

    @property
    def value(self):
        return 3

    @property
    def char(self):
        return "N" if self.color == Color.WHITE else "n"
