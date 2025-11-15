from abc import ABC, abstractmethod
from dataclass import dataclass
from enum import Enum

from chess.square import Square
from chess.pieces import Color


@dataclass
class Piece(ABC):
    """Abstract base class for chess pieces.

    Subclasses must implement 'moves' and 'value' properties, and '__str__'.

    Attributes:
        color: Piece color
        position: Current position on the board.
        has_moved: True if piece has moved from starting position.
    """

    color: Color
    position: Square
    has_moved: bool = False

    @property
    @abstractmethod
    def moves(self, board: Board) -> list[Square]:
        """Return all theoretically possible moves for the piece.

        Returns a list of coordinates that would be possible to move
        to if the piece was on an empty board.
        Legality of moves are checked by the legal_move method in Board.

        This method should not account for:
        - Check
        - Friendly or opponent pieces blocking the way
        - Promotion
        - Castling
        - Pawn captures
        - En passant

        Args:
            board: Current state of the board.

        Returns:
            List of coordinates the piece can move to.
        """
        pass

    @property
    @abstractmethod
    def value(self) -> int:
        """Return the conventional point value of the piece."""
        pass

    @abstractmethod
    def __str__(self):
        pass

    def __repr__(self):
        # TODO: Return proper repr once board representation is implemented
        return self.__str__()
