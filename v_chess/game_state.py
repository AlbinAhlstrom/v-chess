from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING, Tuple
from functools import cached_property

from v_chess.board import Board
from v_chess.square import Square
from v_chess.enums import Color, CastlingRight
from v_chess.fen_helpers import state_from_fen, state_to_fen

if TYPE_CHECKING:
    from v_chess.rules.core import Rules
    from v_chess.piece import Piece


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
    rules: "Rules"
    repetition_count: int = 1

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

    @cached_property
    def fen(self) -> str:
        return state_to_fen(self)

    def __hash__(self):
        return hash(self.fen)


@dataclass(frozen=True)
class ThreeCheckGameState(GameState):
    """GameState for Three-Check Chess.
    
    Tracks the number of times each side has given check.
    checks[0] = checks by White (against Black King)
    checks[1] = checks by Black (against White King)
    """
    checks: Tuple[int, int] = (0, 0)


@dataclass(frozen=True)
class CrazyhouseGameState(GameState):
    """GameState for Crazyhouse Chess.
    
    Tracks captured pieces available for dropping.
    pockets[0] = White's pocket (captured Black pieces, converted to White)
    pockets[1] = Black's pocket (captured White pieces, converted to Black)
    """
    pockets: Tuple[Tuple["Piece", ...], Tuple["Piece", ...]] = ((), ())