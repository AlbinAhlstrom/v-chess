from math import inf

from chess.piece.piece import Piece
from chess.enums import Color, Direction
from chess.square import Square


class King(Piece):
    """King piece representation.

    Moves one square in any direction.
    Special rules for castling and check are implemented in Board.legal_move.
    """

    moveset = Direction.straight_and_diagonal()
    MAX_STEPS = 1


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
