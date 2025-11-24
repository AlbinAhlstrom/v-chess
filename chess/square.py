from dataclasses import dataclass
from string import ascii_lowercase
from typing import Optional, Literal


from dataclasses import dataclass
from typing import Optional


class Square:
    """Represents a square on the chessboard."""

    def __init__(
        self, coordinate: str | tuple | "Coordinate", piece: Optional["Piece"] = None
    ):
        self.coordinate = Coordinate.from_any(coordinate)
        self._piece = piece

    @property
    def piece(self):
        return self._piece

    @piece.setter
    def piece(self, piece):
        if piece is not None:
            piece.square = self
        self._piece = piece

    @property
    def row(self) -> int:
        return self.coordinate.row

    @property
    def col(self) -> int:
        return self.coordinate.col

    @property
    def is_occupied(self) -> bool:
        return self.piece is not None

    @property
    def is_empty(self) -> bool:
        return self.piece is None

    def __str__(self):
        """Return algebraic notation (e.g., 'e4')."""
        return str(self.coordinate)

    def __eq__(self, other: Square | Coordinate | str | tuple[int, int]):
        if isinstance(other, tuple):
            other = Coordinate.from_any(other)
        return str(self) == str(other)

    @classmethod
    def from_string(cls, notation: str) -> "Square":
        """Create a Square from an algebraic notation string (e.g., 'e4')."""
        return cls(Coordinate.from_str(notation))

    def add_piece(self, piece: "Piece"):
        self.piece = piece
        piece.square = self

    def remove_piece(self):
        if self.piece is not None:
            self.piece.square = None
        self.piece = None


@dataclass(frozen=True)
class Coordinate:
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
    def from_str(cls, notation: str) -> "Coordinate":
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
    def from_any(cls, coordinate: str | tuple | "Coordinate") -> "Coordinate":
        if isinstance(coordinate, cls):
            return coordinate
        elif isinstance(coordinate, str):
            return cls.from_str(coordinate)
        elif isinstance(coordinate, tuple):
            return cls(*coordinate)
        else:
            raise TypeError(f"Invalid coordinate type: {type(coordinate)}")

    def __str__(self):
        return f"{chr(self.col + ord('a'))}{8 - self.row}"
