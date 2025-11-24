from abc import ABC, abstractproperty, abstractmethod

from .piece import Piece
from chess.move_utils import Direction


class SlidingPiece(Piece):
    @abstractproperty
    def moveset() -> list[Direction]: ...

    @property
    def lines(self):
        return self.get_lines(self.moveset)

    @property
    def moves(self):
        return {square for line in self.lines for square in line}
