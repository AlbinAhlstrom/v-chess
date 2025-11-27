from dataclasses import dataclass

from chess.enums import Direction


@dataclass(frozen=True)
class Square:
    """Represents a coordinate on a chessboard.

    Allows for row and column access as well as algebraic notation.
    Index 0 for row corresponds to the 8th rank of the board.
    Index 0 for column corresponds to the A-file.
    """

    row: int
    col: int

    def __post_init__(self):
        if not 0 <= self.row < 8:
            raise ValueError(f"Invalid row {self.row}")
        if not 0 <= self.col < 8:
            raise ValueError(f"Invalid col {self.col}")

    @classmethod
    def from_str(cls, notation: str) -> "Square":
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
    def from_any(cls, coordinate: str | tuple | "Square") -> "Square":
        if isinstance(coordinate, cls):
            return coordinate
        elif isinstance(coordinate, str):
            return cls.from_str(coordinate)
        elif isinstance(coordinate, tuple):
            return cls(*coordinate)
        else:
            raise TypeError(f"Invalid coordinate type: {type(coordinate)}")

    def get_adjacent(self, direction: Direction) -> Square:
        """Return a new coordinate one step in a direction"""
        d_col, d_row = direction.value
        return self.from_any((self.row + d_row, self.col + d_col))

    def __str__(self):
        """Return algebraic notation."""
        return f"{chr(self.col + ord('a'))}{8 - self.row}"
