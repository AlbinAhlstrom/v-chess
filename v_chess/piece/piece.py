from abc import ABC, abstractmethod
from itertools import chain
from dataclasses import dataclass

from v_chess.square import Square
from v_chess.enums import Color, Direction


@dataclass(frozen=True)
class Piece(ABC):
    """Abstract base class for all chess pieces.

    Attributes:
        color: The color of the piece.
        MAX_STEPS: The maximum number of squares the piece can move in one step.
    """
    color: Color
    MAX_STEPS = 7

    @property
    @abstractmethod
    def moveset(self) -> set[Direction]:
        """Returns the directions the piece can move in."""
        ...

    @property
    @abstractmethod
    def value(self) -> int | float:
        """Returns the conventional point value of the piece."""
        ...

    @abstractmethod
    def __str__(self) -> str:
        """Returns a unicode symbol for the piece."""
        ...

    @property
    @abstractmethod
    def fen(self) -> str:
        """Returns the FEN character representing the piece."""
        ...

    @property
    def css_class(self):
        """Returns the CSS class name for the piece."""
        return f"{self.color}-{self.__class__.__name__.lower()}"

    def theoretical_move_paths(self, start: Square) -> list[list[Square]]:
        """Returns reachable squares in each direction as separate paths.

        Args:
            start: The square the piece is moving from.

        Returns:
            A list of paths, where each path is a list of Squares.
        """
        return [direction.get_path(start, self.MAX_STEPS) for direction in self.moveset]

    def theoretical_moves(self, start: Square) -> list[Square]:
        """Returns all reachable squares on an empty board.

        Args:
            start: The square the piece is moving from.

        Returns:
            A list of reachable Squares.
        """
        return list(chain.from_iterable(self.theoretical_move_paths(start)))

    def capture_paths(self, start: Square) -> list[list[Square]]:
        """Returns all potentially attacked squares as separate paths.

        Args:
            start: The square the piece is attacking from.

        Returns:
            A list of attack paths.
        """
        return self.theoretical_move_paths(start)

    def capture_squares(self, start: Square) -> list[Square]:
        """Returns all potentially attacked squares.

        Args:
            start: The square the piece is attacking from.

        Returns:
            A list of attacked Squares.
        """
        return list(chain.from_iterable(self.capture_paths(start)))

