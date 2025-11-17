from dataclasses import dataclass
from string import ascii_lowercase
from typing import Optional, Literal


class Square:
    """Represents a square on the chessboard.

    Attributes:
        coordinate: The coordinate of the square being represented.
        piece: The piece currently on the square (if any).
    """

    def __init__(self, coordinate: str | tuple, piece: Optional["Piece"] = None):
        self.coordinate = Coordinate.from_str_or_tuple(coordinate)
        self.piece = piece

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
        return str(self.coord)

    @classmethod
    def from_string(cls, coord: str) -> Square:
        """Create a Coordinate from a string.

        Args:
            coord: A 2-character algebraic square string (e.g. 'e4').

        Returns:
            Coordinate: The corresponding board coordinate.

        Raises:
            ValueError: If the input is invalid.
        """
        if len(notation) != 2:
            raise ValueError(f"Invalid length of {coord=}")

        file_char = notation[0].lower()
        rank_char = notation[1]

        if file_char < "a" or file_char > "h":
            raise ValueError(f"Invalid file in {coord=}")

        if rank_char < "1" or rank_char > "8":
            raise ValueError(f"Invalid rank in {coord=}")

        col = ord(file_char) - ord("a")
        row = 8 - int(rank_char)

        return cls(row, col)

    def add_piece(self, piece: "Piece"):
        self.piece = piece
        piece.square = self

    def remove_piece(self):
        self.piece = None
        piece.square = None


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
            raise ValueError(f"Invalid row {row}")
        if not 0 <= self.col < 8:
            raise ValueError(f"Invalid col {col}")

    @classmethod
    def from_str(cls, notation: str):
        if len(notation) != 2:
            raise ValueError(f"Invalid length of {len(notation)=}")

        file_char = notation[0].lower()
        rank_char = notation[1]

        if file_char < "a" or file_char > "h":
            raise ValueError(f"Invalid file in {coord=}")
        if rank_char < "1" or rank_char > "8":
            raise ValueError(f"Invalid rank in {coord=}")

        col = ord(notation[0].lower()) - ord("a")
        row = 8 - int(notation[1])

        return cls(row, col)

    def __str__(self):
        return f"{chr(self.col + ord('a'))}{8 - self.row}"

    @classmethod
    def from_str_or_tuple(cls, coordinate: str | tuple):
        if isinstance(coordinate, str):
            return cls.from_str(coordinate)
        elif isinstance(coordinate, tuple):
            return cls(*coordinate)
        else:
            raise TypeError(f"Invalid {type(coordinate)=}")
