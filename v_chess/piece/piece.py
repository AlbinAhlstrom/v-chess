from __future__ import annotations
from abc import ABC, abstractmethod
from itertools import chain
from dataclasses import dataclass

from v_chess.square import Square
from v_chess.enums import Color, Direction


@dataclass(frozen=True)
class Piece(ABC):
    """Abstract base class for chess pieces.

    Subclasses must implement 'moves' and 'value' properties, and '__str__'.

    Attributes:
        color: Piece color
    """
    color: Color
    MAX_STEPS = 7

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

    def theoretical_move_paths(self, start: Square) -> list[list[Square]]:
        """List of squares reachable when moving in all directions in moveset."""
        return [direction.get_path(start, self.MAX_STEPS) for direction in self.moveset]

    def theoretical_moves(self, start: Square) -> list[Square]:
        """All moves legal on an empty board"""
        return list(chain.from_iterable(self.theoretical_move_paths(start)))

    def capture_paths(self, start: Square) -> list[list[Square]]:
        """List of squares in a line from start square that are under attack by the piece."""
        return self.theoretical_move_paths(start)

    def capture_squares(self, start: Square) -> list[Square]:
        return list(chain.from_iterable(self.capture_paths(start)))

