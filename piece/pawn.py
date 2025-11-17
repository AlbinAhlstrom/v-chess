from chess.square import Square
from chess.piece.piece import Piece
from chess.piece.color import Color


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
    def moves(self):
        pass

        print(self.color)
        if self.color.value == 1:
            move_offsets = (-1,) if self.has_moved else (-1, -2)
        elif self.color.value == 0:
            move_offsets = (1,) if self.has_moved else (1, 2)
        else:
            raise AttributeError(f"Invalid piece {color=}")

        return {
            Square(self.square.row + move, self.square.col)
            for move in move_offsets
            if 0 <= pos.row + move < 8
        }

    @property
    def value(self):
        return 1
