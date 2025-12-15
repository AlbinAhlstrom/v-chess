from dataclasses import dataclass, field
from oop_chess.enums import Color, Direction
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

    def __init__(self, *args) -> None:
        """Initialize a square from a variety of types.

        Allowed types are:
        - row, col: individual args
        - tuple[int, int]
        - str: valid SAN string
        - Square: re-initialization
        - None: represents the None-square: row,col=(-1, -1)
        """
        _row: int
        _col: int

        if not args or args[0] is None:
            _row, _col = -1, -1
        elif len(args) == 2:
            if not (isinstance(args[0], int) and isinstance(args[1], int)):
                raise TypeError("Individual arguments must be (row: int, col: int).")
            _row, _col = args[0], args[1]
        elif len(args) == 1:
            arg = args[0]
            if isinstance(arg, Square):
                _row, _col = arg.row, arg.col
            elif isinstance(arg, str):
                _row, _col = self._parse_from_san(arg)
            elif isinstance(arg, tuple) and len(arg) == 2:
                if not isinstance(arg[0], int) or not isinstance(arg[1], int):
                    raise TypeError("When a tuple is provided, its elements must be integers (row, col).")
                _row, _col = arg[0], arg[1]
            else:
                raise TypeError(f"Invalid single argument type: {type(arg)}")
        else:
            raise TypeError(f"Invalid number of arguments: {len(args)}")

        object.__setattr__(self, 'row', _row)
        object.__setattr__(self, 'col', _col)
        if self.is_valid(self.row, self.col) or self.is_none_square:
            return
        raise ValueError(f"Invalid Square: row={self.row}, col={self.col}")

    @property
    def is_none_square(self) -> bool:
        return self.row == -1 and self.col == -1

    @staticmethod
    def is_valid(row: int, col: int) -> bool:
        """Check if row and col are within the 0-7 range."""
        return 0 <= row < 8 and 0 <= col < 8

    def is_promotion_row(self, player: Color) -> bool:
        """Return True if square is the promotion row for given player."""
        return self.row == 0 if player == Color.WHITE else self.row == 7

    def get_step(self, direction: Direction) -> Square:
        """
        Return the resulting Square if a step in 'direction' is on the board.
        Returns None otherwise.
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
        """Return a new coordinate one step in a direction.

        NOTE: This method assumes the result is a valid square and is typically
        used when you are certain the move is within bounds, or when you are
        iterating over all possible directions (where validity is checked
        by the Square constructor/post_init).
        """
        d_col, d_row = direction.value
        new_row, new_col = self.row + d_row, self.col + d_col

        if not Square.is_valid(new_row, new_col):
            return Square(-1, -1)

        return Square(new_row, new_col)

    def is_adjacent_to(self, square: 'Square', moveset: set[Direction] = Direction.straight_and_diagonal()):
        adjacent_squares = [self.adjacent(direction) for direction in moveset]
        return square in adjacent_squares

    def __str__(self):
        """Return algebraic notation."""
        if self.is_none_square:
            return "NoneSquare"
        return f"{chr(self.col + ord('a'))}{8 - self.row}"

Coordinate: TypeAlias = str | tuple | Square


