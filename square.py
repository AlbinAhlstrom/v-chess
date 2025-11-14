from dataclasses import dataclass
from typing import Optional

from pieces import Piece


class Square:
    """Represents a square on the chessboard.

    Attributes:
        coord: The coordinate of the square being represented.
        piece: The piece currently on the square (if any).
    """

    def __init__(self, coordinate: Coordinate, piece: Optional[Piece] = None):
        self.coordinate = coordinate
        self.piece = piece

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

    def add_piece(piece: Piece):
        self.piece = piece
        piece.position = self.coord

    def remove_piece():
        self.piece = None
        piece.position = None


class Coordinate:
    """Represents a coordinate on a chessboard.

    Allows for row and column access as well as algebraic notation.
    Index 0 for row corresponds to the 8th rank of the board.
    Index 0 for column corresponds to the A-file.
    """

    def __init__(self, row: int, col: int):
        """Initialize a coordinate by row and column
        Attributes:
            row: Row index (0-7) => algebraic (8-1).
            col: Column index (0-7) => algebraic (A-H).
        """
        if not 0 <= row < 8:
            raise ValueError(f"Invalid row {row}")
        if not 0 <= col < 8:
            raise ValueError(f"Invalid col {col}")

        self.row = row
        self.col = col

    def __eq__(self, other: Coordinate) -> bool:
        """Check if two coordinates are equal.

        Args:
            other: Coordinate to compare to.

        Returns:
            bool: True if row and col attributes match, else False
        """
        return self.row == other.row and self.col == other.col

    def __repr__(self):
        return f"Coordinate(row={self.row}, col={self.col})"

    def __hash__(self):
        return hash((self.row, self.col))

    def __str__(self):
        return f"{chr(self.col + ord('a'))}{8 - self.row}"
