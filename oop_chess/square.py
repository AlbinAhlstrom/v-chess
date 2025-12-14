from dataclasses import dataclass

from oop_chess.enums import Color, Direction
from typing import TypeAlias


@dataclass(frozen=True)
class Square:
    """Represents a coordinate on a chessboard.

    Allows for row and column access as well as algebraic notation.
    Index 0 for row corresponds to the 8th rank of the board.
    Index 0 for column corresponds to the A-file.
    """



    row: int
    col: int

    @property
    def is_none_square(self) -> bool:
        return self.row == -1 and self.col == -1

    def __post_init__(self):
        """Initial validation check, only be called by the constructor."""
        if self.is_valid(self.row, self.col) or self.is_none_square:
            return
        raise ValueError(f"Invalid Square {self}")

    @staticmethod
    def is_valid(row: int, col: int) -> bool:
        """Check if row and col are within the 0-7 range."""
        return 0 <= row < 8 and 0 <= col < 8

    def is_promotion_row(self, player: Color) -> bool:
        """Return True if square is the promotion row for given player."""
        return self.row == 0 if player == Color.WHITE else self.row == 7

    def get_step(self, direction: Direction) -> Square | None:
        """
        Return the resulting Square if a step in 'direction' is on the board.
        Returns None otherwise.
        """

        d_col, d_row = direction.value
        new_col, new_row = self.col + d_col, self.row + d_row

        if not Square.is_valid(self.row + d_row, self.col + d_col):
            return None

        return Square(new_row, new_col)

    @classmethod
    def from_str(cls, notation: str) -> Square:
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
        return cls(row, col)

    @classmethod
    def from_coord(cls, coordinate: Coordinate) -> "Square":
        if isinstance(coordinate, cls):
            return coordinate
        elif isinstance(coordinate, str):
            return cls.from_str(coordinate)
        elif isinstance(coordinate, tuple):
            return cls(*coordinate)
        else:
            raise TypeError(f"Invalid coordinate type: {type(coordinate)}")

    def adjacent(self, direction: Direction) -> Square:
        """Return a new coordinate one step in a direction.

        NOTE: This method assumes the result is a valid square and is typically
        used when you are certain the move is within bounds, or when you are
        iterating over all possible directions (where validity is checked
        by the Square constructor/post_init).
        """


        d_col, d_row = direction.value
        if not Square.is_valid(self.row + d_row, self.col + d_col):
            return NoSquare
        return self.__class__.from_coord((self.row + d_row, self.col + d_col))

    def is_adjacent_to(self, square: Square, moveset: set[Direction] = Direction.straight_and_diagonal()):
        adjacent_squares = [self.adjacent(direction) for direction in moveset]
        return square in adjacent_squares

    def __str__(self):
        """Return algebraic notation."""
        return f"{chr(self.col + ord('a'))}{8 - self.row}"


NoSquare = Square(-1, -1)
Coordinate: TypeAlias = str | tuple | Square
