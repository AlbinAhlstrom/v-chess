from enum import Enum


class Color(Enum):
    """Representation of piece/player color.

    Attributes:
        BLACK: Represents black pieces/player.
        WHITE: Represents white pieces/player.
    """

    BLACK = 0
    WHITE = 1


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

    @property
    def algebraic_notation(self) -> str:
        """Return the squares corresponding algebraic notation."""
        return f"{chr(self.col + ord('a'))}{8 - self.row}"

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
        return self.algebraic_notation
