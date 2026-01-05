from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from .enums import Direction, Color
from typing import TypeAlias


@dataclass(frozen=True)
class Square:
    """Represents a square on a chessboard.

    Allows for row and column access
    Instantiable through and convertible to standard algebraic notation (SAN).
    Index 0 for row corresponds to the 8th rank of the board.
    Index 0 for column corresponds to the A-file.
    """
    row: int = field(compare=True)
    col: int = field(compare=True)

    _CACHE = {}

    def __new__(cls, *args) -> 'Square':
        """Creates a new Square instance.
        
        Uses a cache to ensure unique instances for each coordinate.

        Args:
            *args: Can be (row, col) integers, a SAN string (e.g., 'e4'),
                  a tuple (row, col), or another Square instance.

        Returns:
            The Square instance corresponding to the arguments.

        Raises:
            ValueError: If the arguments do not represent a valid square.
        """
        _row: int
        _col: int

        if not args or args[0] is None:
            _row, _col = -1, -1
        elif len(args) == 2:
            _row, _col = args[0], args[1]
        elif len(args) == 1:
            arg = args[0]
            if isinstance(arg, Square):
                return arg
            elif isinstance(arg, str):
                if len(arg) != 2: raise ValueError(f"Invalid length of {arg=}")
                file_char = arg[0].lower()
                rank_char = arg[1]
                if not ("a" <= file_char <= "h"):
                    raise ValueError(f"Invalid file char: {file_char}")
                if not rank_char.isdigit():
                    raise ValueError(f"Invalid rank char: {rank_char}")
                _col = ord(file_char) - ord("a")
                _row = 8 - int(rank_char)
            elif isinstance(arg, tuple) and len(arg) == 2:
                _row, _col = arg[0], arg[1]
            else:
                raise TypeError(f"Invalid single argument type: {type(arg)}")
        else:
            raise TypeError(f"Invalid number of arguments: {len(args)}")

        if (_row, _col) in cls._CACHE:
            return cls._CACHE[(_row, _col)]

        if not (cls.is_valid(_row, _col) or (_row == -1 and _col == -1)):
             raise ValueError(f"Invalid Square: row={_row}, col={_col}")

        instance = super().__new__(cls)
        object.__setattr__(instance, 'row', _row)
        object.__setattr__(instance, 'col', _col)
        cls._CACHE[(_row, _col)] = instance
        return instance

    def __init__(self, *args) -> None:
        """Handled by __new__ for caching."""
        pass

    @property
    def is_none_square(self) -> bool:
        """True if this is the special NoneSquare (representing no square)."""
        return self.row == -1 and self.col == -1

    @property
    def index(self) -> int:
        """Returns the bitboard index (0-63)."""
        return self.row * 8 + self.col

    @staticmethod
    def is_valid(row: int, col: int) -> bool:
        """Checks if the row and column are within the board boundaries (0-7)."""
        return 0 <= row < 8 and 0 <= col < 8

    def is_promotion_row(self, player: Color) -> bool:
        """Checks if the square is on the promotion rank for the given player."""
        return self.row == 0 if player == Color.WHITE else self.row == 7

    def get_step(self, direction: Direction) -> Square:
        """Returns the square one step in the given direction.

        Args:
             direction: The direction to step.

        Returns:
             The resulting Square, or a NoneSquare if off the board.
        """
        d_col, d_row = direction.value
        new_col, new_row = self.col + d_col, self.row + d_row

        if not Square.is_valid(new_row, new_col):
            return Square(-1, -1)

        return Square(new_row, new_col)

    def _parse_from_san(self, notation: str) -> tuple[int, int]:
        if len(notation) != 2:
            raise ValueError(f"Invalid length of {notation=}")

        file_char = notation[0].lower()
        rank_char = notation[1]

        if not ("a" <= file_char <= "h"):
            raise ValueError(f"Invalid file in {notation=}")
        if not ("1" <= rank_char <= "8"):
            raise ValueError(f"Invalid rank in {notation=}")

        col = ord(file_char) - ord("a")
        row = 8 - int(rank_char)
        return row, col

    def adjacent(self, direction: Direction) -> 'Square':
        """Returns a new coordinate one step in a direction.

        NOTE: This method assumes the result is a valid square and is typically
        used when you are certain the move is within bounds, or when you are
        iterating over all possible directions (where validity is checked
        by the Square constructor/post_init).

        Args:
            direction: The direction to move.

        Returns:
             The adjacent Square, or NoneSquare if off the board.
        """
        d_col, d_row = direction.value
        new_row, new_col = self.row + d_row, self.col + d_col

        if not Square.is_valid(new_row, new_col):
            return Square(-1, -1)

        return Square(new_row, new_col)

    def is_adjacent_to(self, square: 'Square', moveset: set[Direction] = Direction.straight_and_diagonal()):
        """Checks if this square is adjacent to another square."""
        adjacent_squares = [self.adjacent(direction) for direction in moveset]
        return square in adjacent_squares

    def __str__(self):
        """Returns the algebraic notation (e.g., 'e4')."""
        if self.is_none_square:
            return "NoneSquare"
        return f"{chr(self.col + ord('a'))}{8 - self.row}"

Coordinate: TypeAlias = str | tuple | Square


