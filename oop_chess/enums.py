from __future__ import annotations
from enum import Enum, StrEnum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oop_chess.square import Square


class StatusReason(StrEnum):
    VALID = "valid"
    NO_WHITE_KING = "no white king"
    NO_BLACK_KING = "no black king"
    TOO_MANY_KINGS = "too many kings"
    TOO_MANY_WHITE_PAWNS = "too many white pawns"
    TOO_MANY_BLACK_PAWNS = "too many black pawns"
    PAWNS_ON_BACKRANK = "pawns on back rank"
    TOO_MANY_WHITE_PIECES = "too many white pieces"
    TOO_MANY_BLACK_PIECES = "too many black pieces"
    INVALID_CASTLING_RIGHTS = "invalid castling rights"
    INVALID_EP_SQUARE = "invalid en passant square"
    OPPOSITE_CHECK = "inactive player left in check"
    TOO_MANY_CHECKERS = "more than 2 checkers"


class State(Enum):
    """The state of the game."""
    ONGOING = auto()
    CHECKMATE = auto()
    STALEMATE = auto()
    INSUFFICIENT_MATERIAL = auto()
    SEVENTYFIVE_MOVES = auto()
    FIVEFOLD_REPETITION = auto()
    FIFTY_MOVES = auto()
    THREEFOLD_REPETITION = auto()


class Color(StrEnum):
    """Piece/player color."""

    BLACK = "b"
    WHITE = "w"

    @property
    def opposite(self):
        return Color.BLACK if self == Color.WHITE else Color.WHITE

    def __str__(self):
        return "black" if self.value == "b" else "white"


class CastlingRight(StrEnum):
    """A players castling rights."""

    WHITE_SHORT = "K"
    BLACK_SHORT = "k"
    WHITE_LONG = "Q"
    BLACK_LONG = "q"

    @property
    def expected_rook_square(self) -> Square:
        from oop_chess.square import Square
        match self:
            case CastlingRight.WHITE_SHORT:
                return Square.from_str("h1")
            case CastlingRight.WHITE_LONG:
                return Square.from_str("a1")
            case CastlingRight.BLACK_SHORT:
                return Square.from_str("h8")
            case CastlingRight.BLACK_LONG:
                return Square.from_str("a8")

    @property
    def expected_king_square(self) -> Square:
        from oop_chess.square import Square
        match self:
            case CastlingRight.WHITE_SHORT | CastlingRight.WHITE_LONG:
                return Square.from_str("e1")
            case CastlingRight.BLACK_SHORT | CastlingRight.BLACK_LONG:
                return Square.from_str("e8")

    @property
    def color(self) -> Color:
        match self:
            case CastlingRight.WHITE_SHORT | CastlingRight.WHITE_LONG:
                return Color.WHITE
            case CastlingRight.BLACK_SHORT | CastlingRight.BLACK_LONG:
                return Color.BLACK

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
    """Directions a piece can move in.

    Enum values are tuples repersenting row and col from an initial square.
    (x, y) = (col_delta, row_delta)
    """
    NONE = (0, 0)

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    UP_LEFT = (-1, -1)
    UP_RIGHT = (1, -1)
    DOWN_LEFT = (-1, 1)
    DOWN_RIGHT = (1, 1)

    L_UP_LEFT = (-1, -2)
    L_UP_RIGHT = (1, -2)
    L_DOWN_LEFT = (-1, 2)
    L_DOWN_RIGHT = (1, 2)
    L_LEFT_UP = (-2, -1)
    L_LEFT_DOWN = (-2, 1)
    L_RIGHT_UP = (2, -1)
    L_RIGHT_DOWN = (2, 1)

    TWO_LEFT = (-2, 0)
    TWO_RIGHT = (2, 0)

    @classmethod
    def straight(cls) -> set[Direction]:
        return {cls.UP, cls.DOWN, cls.LEFT, cls.RIGHT}

    @classmethod
    def diagonal(cls) -> set[Direction]:
        return {cls.UP_LEFT, cls.DOWN_LEFT, cls.UP_RIGHT, cls.DOWN_RIGHT}

    @classmethod
    def straight_and_diagonal(cls) -> set[Direction]:
        return cls.straight() | cls.diagonal()

    @classmethod
    def two_straight_one_sideways(cls) -> set[Direction]:
        return {
            cls.L_UP_LEFT, cls.L_UP_RIGHT, cls.L_DOWN_LEFT, cls.L_DOWN_RIGHT,
            cls.L_LEFT_UP, cls.L_LEFT_DOWN, cls.L_RIGHT_UP, cls.L_RIGHT_DOWN,
        }

    @classmethod
    def up_straight_or_diagonal(cls) -> set[Direction]:
        return {cls.UP, cls.UP_LEFT, cls.UP_RIGHT}

    @classmethod
    def down_straight_or_diagonal(cls) -> set[Direction]:
        return {cls.DOWN, cls.DOWN_LEFT, cls.DOWN_RIGHT}

    @classmethod
    def two_left_or_right(cls) -> set[Direction]:
        return {cls.TWO_LEFT, cls.TWO_RIGHT}

    def get_path(self, square: Square, max_squares: int = 7) -> list[Square]:
        """Get all squares in a direction."""
        return list(self.take_step(square, max_squares))

    def take_step(self, start_square: Square, max_squares: int):
        """
        Generator that yields squares in a specified direction from a start square.
        Stops when the board edge is reached or max_squares is hit.
        """
        from oop_chess.square import Square

        d_col, d_row = self.value

        for dist in range(1, max_squares + 1):
            new_c = start_square.col + (d_col * dist)
            new_r = start_square.row + (d_row * dist)

            if 0 <= new_r < 8 and 0 <= new_c < 8:
                yield Square(new_r, new_c)
            else:
                break
