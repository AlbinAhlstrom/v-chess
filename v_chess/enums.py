from __future__ import annotations
from enum import Enum, StrEnum
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from v_chess.square import Square


def _v(name: str, members: dict[str, str]) -> StrEnum:
    return StrEnum(name, members)


class BaseLegalityReason(StrEnum):
    @classmethod
    def load(cls, variant: str) -> type[StrEnum]:
        if "Board" in cls.__name__:
            key, config_dict = "board", BOARD_DISCREPANCIES
        elif "Move" in cls.__name__:
            key, config_dict = "move", MOVE_DISCREPANCIES
        else:
            key, config_dict = "game_over", GAMEOVER_DISCREPANCIES

        members = {m.name: m.value for m in cls}
        [members.pop(r, None) for r in STANDARD_REMOVALS.get(key, [])]

        if variant == "Standard":
            return _v(f"Standard{cls.__name__}", members)

        changes = config_dict.get(variant, {})

        if "add" in changes:
            for add_key in changes["add"]:
                if add_key in cls.__members__:
                    members[add_key] = cls[add_key].value
                elif isinstance(changes["add"], dict):
                    members[add_key] = changes["add"][add_key]

        if "remove" in changes:
            [members.pop(r, None) for r in changes["remove"]]

        return _v(f"{variant}{cls.__name__}", members)


class BoardLegalityReason(BaseLegalityReason):
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
    KINGS_ADJACENT = "kings cannot be adjacent"
    KING_IN_CHECK = "king in check"


class MoveLegalityReason(BaseLegalityReason):
    NO_PIECE = "no piece moved."
    WRONG_COLOR = "wrong piece color"
    NO_CASTLING_RIGHT = "no right for castling"
    CASTLING_FROM_CHECK = "cannot castle while in check."
    CASTLING_THROUGH_CHECK = "cannot castle through or into attacked square."
    NOT_IN_MOVESET = "move not in piece moveset."
    OWN_PIECE_CAPTURE = "can't capture own piece."
    FORWARD_PAWN_CAPTURE = "cant capture forwards with pawn."
    PAWN_DIAGONAL_NON_CAPTURE = "diagonal pawn move requires a capture."
    NON_PROMOTION = "pawns must promote when reaching last row."
    PATH_BLOCKED = "path is blocked."
    EARLY_PROMOTION = "can only promote on the last row."
    KING_PROMOTION = "can't promote to king."
    KING_LEFT_IN_CHECK = "king left in check"
    LEGAL = "move is legal"
    MANDATORY_CAPTURE = "mandatory capture available."
    CASTLING_DISABLED = "castling disabled in this variant"
    KING_EXPLODED = "king exploded"
    GIVES_CHECK = "move gives check"


class GameOverReason(BaseLegalityReason):
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    REPETITION = "repetition"
    FIFTY_MOVE_RULE = "50 move rule"
    MUTUAL_AGREEMENT = "mutual agreement"
    TIMEOUT = "timeout"
    ONGOING = "ongoing"
    ALL_PIECES_CAPTURED = "all pieces captured"
    INSUFFICIENT_MATERIAL = "insufficient material"
    KING_ON_HILL = "king on hill"
    THREE_CHECKS = "three checks"
    KING_EXPLODED = "king exploded"
    KING_TO_EIGHTH_RANK = "king to eighth rank"
    SURRENDER = "surrender"
    ABORTED = "aborted"


STANDARD_REMOVALS = {
    "board": ["KINGS_ADJACENT", "KING_IN_CHECK"],
    "move": ["MANDATORY_CAPTURE", "CASTLING_DISABLED", "KING_EXPLODED", "GIVES_CHECK"],
    "game_over": ["ALL_PIECES_CAPTURED", "KING_ON_HILL", "THREE_CHECKS", "KING_EXPLODED", "KING_TO_EIGHTH_RANK"]
}


BOARD_DISCREPANCIES = {
    "Antichess": {"remove": ["NO_WHITE_KING", "NO_BLACK_KING", "INVALID_CASTLING_RIGHTS", "OPPOSITE_CHECK", "TOO_MANY_CHECKERS"]},
    "Atomic": {"add": ["KINGS_ADJACENT"]},
    "Horde": {"remove": ["NO_WHITE_KING", "PAWNS_ON_BACKRANK"]},
    "RacingKings": {"add": ["KING_IN_CHECK"], "remove": ["INVALID_CASTLING_RIGHTS", "OPPOSITE_CHECK", "TOO_MANY_CHECKERS"]},
}


MOVE_DISCREPANCIES = {
    "Antichess": {
        "add": ["MANDATORY_CAPTURE", "CASTLING_DISABLED"],
        "remove": ["KING_LEFT_IN_CHECK", "NO_CASTLING_RIGHT", "CASTLING_FROM_CHECK", "CASTLING_THROUGH_CHECK"]
    },
    "Atomic": {"add": ["KING_EXPLODED"]},
    "RacingKings": {
        "add": ["GIVES_CHECK", "CASTLING_DISABLED", "KING_LEFT_IN_CHECK"],
        "remove": ["NO_CASTLING_RIGHT", "CASTLING_FROM_CHECK", "CASTLING_THROUGH_CHECK"]
    },
}


GAMEOVER_DISCREPANCIES = {
    "KingOfTheHill": {"add": ["KING_ON_HILL"]},
    "ThreeCheck": {"add": ["THREE_CHECKS"]},
    "Antichess": {"add": ["ALL_PIECES_CAPTURED"], "remove": ["CHECKMATE"]},
    "Atomic": {"add": ["KING_EXPLODED"]},
    "Horde": {"add": ["ALL_PIECES_CAPTURED"]},
    "RacingKings": {"add": ["KING_TO_EIGHTH_RANK"], "remove": ["CHECKMATE"]},
}


class Color(StrEnum):
    """Represents a piece or player color."""

    BLACK = "b"
    WHITE = "w"

    @property
    def opposite(self) -> Color:
        """Returns the opposite color."""
        return Color.BLACK if self == Color.WHITE else Color.WHITE

    def __str__(self):
        """Returns the full name of the color."""
        return "black" if self.value == "b" else "white"


class CastlingRight(StrEnum):
    """Represents a player's castling rights."""

    WHITE_SHORT = "K"
    BLACK_SHORT = "k"
    WHITE_LONG = "Q"
    BLACK_LONG = "q"
    NONE = "-"

    WA = "A"; WB = "B"; WC = "C"; WD = "D"; WE = "E"; WF = "F"; WG = "G"; WH = "H"
    BA = "a"; BB = "b"; BC = "c"; BD = "d"; BE = "e"; BF = "f"; BG = "g"; BH = "h"

    @property
    def expected_rook_square(self) -> Square:
        """Returns the square where the rook is expected to be for this right."""
        from v_chess.square import Square
        if self == CastlingRight.WHITE_SHORT: return Square("h1")
        if self == CastlingRight.WHITE_LONG: return Square("a1")
        if self == CastlingRight.BLACK_SHORT: return Square("h8")
        if self == CastlingRight.BLACK_LONG: return Square("a8")
        if self == CastlingRight.NONE: return Square(None)

        val = self.value
        col = ord(val.lower()) - ord('a')
        row = 7 if val.isupper() else 0
        return Square(row, col)

    @property
    def expected_king_square(self) -> Square:
        """Returns the square where the king is expected to be for this right."""
        from v_chess.square import Square
        if self.value.isupper():
            return Square("e1")
        if self.value.islower():
            return Square("e8")
        return Square(None)

    @property
    def color(self) -> Color:
        """Returns the color associated with this castling right."""
        if self == CastlingRight.NONE:
            raise ValueError("CastlingRight.NONE has no associated color")
        return Color.WHITE if self.value.isupper() else Color.BLACK

    @classmethod
    def short(cls, color: Color) -> CastlingRight:
        """Returns the short castling right for the given color."""
        return cls.WHITE_SHORT if color == Color.WHITE else cls.BLACK_SHORT

    @classmethod
    def long(cls, color: Color) -> CastlingRight:
        """Returns the long castling right for the given color."""
        return cls.WHITE_LONG if color == Color.WHITE else cls.BLACK_LONG

    @classmethod
    def from_fen(cls, fen_castling_string: str) -> tuple[CastlingRight, ...]:
        """Parses a FEN castling string into a tuple of CastlingRight objects.

        Args:
            fen_castling_string: The castling part of a FEN string.

        Returns:
            A tuple of CastlingRight instances.
        """
        if not fen_castling_string or fen_castling_string == "-":
            return tuple()
        rights = []
        for char in fen_castling_string:
            try: rights.append(cls(char))
            except ValueError: pass
        return tuple(rights)


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
        """Returns the set of orthogonal directions."""
        return {cls.UP, cls.DOWN, cls.LEFT, cls.RIGHT}

    @classmethod
    def diagonal(cls) -> set[Direction]:
        """Returns the set of diagonal directions."""
        return {cls.UP_LEFT, cls.DOWN_LEFT, cls.UP_RIGHT, cls.DOWN_RIGHT}

    @classmethod
    def straight_and_diagonal(cls) -> set[Direction]:
        """Returns the set of all 8 standard directions."""
        return cls.straight() | cls.diagonal()

    @classmethod
    def two_straight_one_sideways(cls) -> set[Direction]:
        """Returns the set of directions a knight moves in."""
        return {
            cls.L_UP_LEFT, cls.L_UP_RIGHT, cls.L_DOWN_LEFT, cls.L_DOWN_RIGHT,
            cls.L_LEFT_UP, cls.L_LEFT_DOWN, cls.L_RIGHT_UP, cls.L_RIGHT_DOWN,
        }

    @classmethod
    def up_straight_or_diagonal(cls) -> set[Direction]:
        """Returns the set of forward (white) pawn directions."""
        return {cls.UP, cls.UP_LEFT, cls.UP_RIGHT}

    @classmethod
    def down_straight_or_diagonal(cls) -> set[Direction]:
        """Returns the set of forward (black) pawn directions."""
        return {cls.DOWN, cls.DOWN_LEFT, cls.DOWN_RIGHT}

    @classmethod
    def two_left_or_right(cls) -> set[Direction]:
        """Returns the directions for a king's castling move."""
        return {cls.TWO_LEFT, cls.TWO_RIGHT}

    def get_path(self, square: Square, max_squares: int = 7) -> list[Square]:
        """Returns all squares in this direction from a starting square.

        Uses an internal cache for performance.

        Args:
            square: The starting square.
            max_squares: Maximum number of squares to look ahead.

        Returns:
            A list of Squares in the path.
        """
        if not hasattr(self.__class__, "_PATH_CACHE"):
            self.__class__._PATH_CACHE = {}

        cache_key = (self, square.index, max_squares)
        if cache_key in self.__class__._PATH_CACHE:
            return self.__class__._PATH_CACHE[cache_key]

        path = list(self.take_step(square, max_squares))
        self.__class__._PATH_CACHE[cache_key] = path
        return path

    def take_step(self, start_square: Square, max_squares: int):
        """Generator that yields squares in this direction.

        Args:
            start_square: The square to start from.
            max_squares: Maximum number of steps to take.

        Yields:
            Squares in the specified direction.
        """

        from v_chess.square import Square

        d_col, d_row = self.value

        for dist in range(1, max_squares + 1):
            new_c = start_square.col + (d_col * dist)
            new_r = start_square.row + (d_row * dist)

            if 0 <= new_r < 8 and 0 <= new_c < 8:
                yield Square(new_r, new_c)
            else:
                break

    def shift(self, bb: int) -> int:
        """Shifts a bitboard in this direction.

        Handles board boundaries to prevent wrap-around.

        Args:
            bb: The bitboard to shift.

        Returns:
            The shifted bitboard.
        """
        d_col, d_row = self.value
        shift_amt = d_row * 8 + d_col

        FILE_A = 0x0101010101010101
        FILE_H = 0x8080808080808080

        if d_col == 1: # Right
            return (bb & ~FILE_H) << 1
        elif d_col == -1: # Left
            return (bb & ~FILE_A) >> 1
        elif d_col == 2: # Two Right
            return (bb & ~FILE_H & ~(FILE_H >> 1)) << 2
        elif d_col == -2: # Two Left
            return (bb & ~FILE_A & ~(FILE_A << 1)) >> 2

        if shift_amt > 0:
            return (bb << shift_amt) & 0xFFFFFFFFFFFFFFFF
        elif shift_amt < 0:
            return (bb >> -shift_amt) & 0xFFFFFFFFFFFFFFFF
        return bb

    def get_ray_mask(self, square_index: int) -> int:
        """Returns a bitmask of the ray in this direction.

        Args:
            square_index: The starting square index.

        Returns:
            A bitmask representing the ray.
        """
        if not hasattr(self.__class__, "_RAY_MASKS"):
            self.__class__._RAY_MASKS = {}

        cache_key = (self, square_index)
        if cache_key in self.__class__._RAY_MASKS:
            return self.__class__._RAY_MASKS[cache_key]

        d_col, d_row = self.value
        row, col = divmod(square_index, 8)
        mask = 0

        r, c = row + d_row, col + d_col
        while 0 <= r < 8 and 0 <= c < 8:
            mask |= (1 << (r * 8 + c))
            r += d_row
            c += d_col

        self.__class__._RAY_MASKS[cache_key] = mask
        return mask
