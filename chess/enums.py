from enum import Enum, StrEnum

from chess.coordinate import Square


class Color(StrEnum):
    """Representation of piece/player color.

    Attributes:
        BLACK: Represents black pieces/player.
        WHITE: Represents white pieces/player.
    """

    BLACK = "b"
    WHITE = "w"

    @property
    def opposite(self):
        return Color.BLACK if self == Color.WHITE else Color.WHITE


class CastlingRight(StrEnum):
    """Represents the castling directions a player is allowed."""

    WHITE_SHORT = "K"
    BLACK_SHORT = "k"
    WHITE_LONG = "Q"
    BLACK_LONG = "q"

    @classmethod
    def short(cls, color: Color) -> CastlingRight:
        """Return short castling right by color"""
        if color == Color.WHITE:
            return cls.WHITE_SHORT
        return cls.BLACK_SHORT

    @classmethod
    def long(cls, color: Color) -> CastlingRight:
        """Return long castling right by color"""
        if color == Color.WHITE:
            return cls.WHITE_LONG
        return cls.BLACK_LONG

    @classmethod
    def from_fen(cls, fen_castling_string: str) -> list[CastlingRight]:
        if not fen_castling_string or fen_castling_string == "-":
            return []
        return [cls(char) for char in fen_castling_string]


class Direction(Enum):
    NONE = (0, 0)

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    UP_LEFT = (-1, -1)
    UP_RIGHT = (1, -1)
    DOWN_LEFT = (-1, 1)
    DOWN_RIGHT = (1, 1)

    L_RIGHT_UP = (2, -1)
    L_RIGHT_DOWN = (2, 1)
    L_LEFT_UP = (-2, -1)
    L_LEFT_DOWN = (-2, 1)
    L_UP_RIGHT = (1, -2)
    L_UP_LEFT = (-1, -2)
    L_DOWN_RIGHT = (1, 2)
    L_DOWN_LEFT = (-1, 2)

    def get_path(self, square: Square) -> list[Square]:
        """Get all squares in a direction."""
        possible_moves = []

        d_col, d_row = self.value

        for dist in range(1, 8):
            new_c = square.col + (d_col * dist)
            new_r = square.row + (d_row * dist)

            if 0 <= new_r < 8 and 0 <= new_c < 8:
                possible_moves.append(Square(new_r, new_c))
            else:
                break

        return possible_moves


class Moveset(Enum):
    NONE = [Direction.NONE]
    CUSTOM = []

    PAWN_WHITE_CAPTURE = [Direction.UP_LEFT, Direction.UP_RIGHT]
    PAWN_BLACK_CAPTURE = [Direction.DOWN_LEFT, Direction.DOWN_RIGHT]

    STRAIGHT = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
    DIAGONAL = [
        Direction.UP_LEFT,
        Direction.UP_RIGHT,
        Direction.DOWN_LEFT,
        Direction.DOWN_RIGHT,
    ]

    STRAIGHT_AND_DIAGONAL = STRAIGHT + DIAGONAL
    KNIGHT = [
        Direction.L_RIGHT_UP,
        Direction.L_RIGHT_DOWN,
        Direction.L_LEFT_UP,
        Direction.L_LEFT_DOWN,
        Direction.L_UP_RIGHT,
        Direction.L_UP_LEFT,
        Direction.L_DOWN_RIGHT,
        Direction.L_DOWN_LEFT,
    ]
