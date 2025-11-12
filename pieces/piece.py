from abc import ABC, abstractmethod

from board import Color, Coordinate


class Piece(ABC):
    def __init__(self, color: Color, position: Coordinate):
        self.color = color
        self._position = position
        self.has_moved = False

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position: Coordinate):
        self._position = position

    @property
    @abstractmethod
    def moves(self, board: Board) -> list[Coordinate]:
        pass

    @property
    @abstractmethod
    def value(self) -> int:
        pass

    @abstractmethod
    def __str__(self):
        pass

    def __repr__(self):
        # TODO: Return proper repr once board representation is implemented
        return self.__str__()
