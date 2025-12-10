from abc import ABC, abstractmethod
from itertools import chain

from oop_chess.square import NoSquare, Square
from oop_chess.enums import Color, Direction


class Piece(ABC):
    """Abstract base class for chess pieces.

    Subclasses must implement 'moves' and 'value' properties, and '__str__'.

    Attributes:
        color: Piece color
        square: Current position on the board
        has_moved: True if piece has moved from starting position.
    """
    MAX_STEPS = 7

    def __init__(self, color: Color, square: Square = NoSquare, has_moved: bool = False):
        self.color = color
        self.square = square
        self.has_moved = has_moved

    @property
    def start_rank(self) -> int:
        return 7 if self.color == Color.WHITE else 0

    @property
    @abstractmethod
    def moveset(self) -> set[Direction]:
        """Return the directions the piece can move in."""
        ...

    @property
    @abstractmethod
    def value(self) -> int | float:
        """Return the conventional point value of the piece."""
        ...

    @abstractmethod
    def __str__(self) -> str:
        """Return a unicode symbol for text based visualization."""
        ...

    @property
    @abstractmethod
    def fen(self) -> str:
        """Return the FEN character matching the piece type."""
        ...

    @property
    def css_class(self):
        return f"{self.color}-{self.__class__.__name__.lower()}"

    @property
    def theoretical_move_paths(self) -> list[list[Square]]:
        """List of squares reachable when moving in all directions in moveset."""
        return [direction.get_path(self.square, self.MAX_STEPS) for direction in self.moveset]

    @property
    def theoretical_moves(self) -> list[Square]:
        """All moves legal on an empty board"""
        return list(chain.from_iterable(self.theoretical_move_paths))

    @property
    def capture_squares(self) -> list[Square]:
        return self.theoretical_moves
