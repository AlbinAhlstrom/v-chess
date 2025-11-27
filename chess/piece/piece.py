from abc import ABC, abstractmethod
from itertools import chain

from chess.coordinate import Square
from chess.enums import Color, Direction, Moveset


class Piece(ABC):
    """Abstract base class for chess pieces.

    Subclasses must implement 'moves' and 'value' properties, and '__str__'.

    Attributes:
        color: Piece color
        square: Current position on the board, None if captured
        has_moved: True if piece has moved from starting position.
    """

    MOVESET: Moveset = Moveset.NONE
    MAX_SQUARES: int = 7

    def __init__(
        self, color: Color, square: Square | None = None, has_moved: bool = False
    ):
        self.color = color
        self.square = square
        self.has_moved = has_moved

    def __init_subclass__(cls, **kwargs):
        """Require that subclasses define class variable MOVESET."""
        super().__init_subclass__(**kwargs)
        if cls.MOVESET == Moveset.NONE:
            raise NotImplementedError(
                f"Class {cls.__name__} must define class variable MOVESET."
            )

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
        """Array of coordinates reachable when moving in all directions"""
        if self.square == None:
            raise AttributeError("No square.")

        paths = [direction.get_path(self.square) for direction in self.MOVESET.value]
        return [path[: self.MAX_SQUARES + 1] for path in paths]

    @property
    def theoretical_moves(self) -> list[Square]:
        """All moves legal on an empty board"""
        return list(chain.from_iterable(self.theoretical_move_paths))
