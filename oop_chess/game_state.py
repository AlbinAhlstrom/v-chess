from dataclasses import dataclass
from typing import Optional

from oop_chess.board import Board
from oop_chess.square import Square
from oop_chess.enums import Color, CastlingRight
from oop_chess.fen_helpers import state_from_fen, state_to_fen


@dataclass(frozen=True)
class GameState:
    """The Context (Snapshot).

    Represents the state of the game at a specific point in time.
    Immutable.
    """
    board: Board
    turn: Color
    castling_rights: tuple[CastlingRight, ...]
    ep_square: Optional[Square]
    halfmove_clock: int
    fullmove_count: int

    STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    EMPTY_BOARD_FEN = "8/8/8/8/8/8/8/8 w KQkq - 0 1"

    @classmethod
    def starting_setup(cls) -> "GameState":
        return state_from_fen(cls.STARTING_FEN)

    @classmethod
    def from_fen(cls, fen: str) -> "GameState":
        return state_from_fen(fen)

    @classmethod
    def empty(cls) -> "GameState":
        return state_from_fen(cls.EMPTY_BOARD_FEN)

    @property
    def fen(self) -> str:
        return state_to_fen(self)

    def __hash__(self):
        return hash(self.fen)

