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
    """Represents the state of a chess game at a specific point in time.

    Attributes:
        board: The current board configuration.
        turn: The color of the player whose turn it is.
        castling_rights: Available castling rights.
        ep_square: The en passant target square, if any.
        halfmove_clock: Number of halfmoves since the last capture or pawn move.
        fullmove_count: The number of the full move.
        rules: The ruleset being used.
        repetition_count: Number of times this position has occurred.
        explosion_square: The square where an explosion occurred (Atomic chess).
    """
    board: Board
    turn: Color
    castling_rights: tuple[CastlingRight, ...]
    ep_square: Optional[Square]
    halfmove_clock: int
    fullmove_count: int
    rules: "Rules"
    repetition_count: int = 1
    explosion_square: Optional[Square] = None

    STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    EMPTY_BOARD_FEN = "8/8/8/8/8/8/8/8 w KQkq - 0 1"

    @classmethod
    def starting_setup(cls) -> "GameState":
        """Creates a GameState with the standard starting position."""
        return state_from_fen(cls.STARTING_FEN)

    @classmethod
    def from_fen(cls, fen: str) -> "GameState":
        """Creates a GameState from a FEN string."""
        return state_from_fen(fen)

    @classmethod
    def empty(cls) -> "GameState":
        """Creates a GameState with an empty board."""
        return state_from_fen(cls.EMPTY_BOARD_FEN)

    @cached_property
    def fen(self) -> str:
        """The FEN string representation of the game state."""
        return state_to_fen(self)

    def __hash__(self):
        """Returns the hash of the FEN string."""
        return hash(self.fen)


@dataclass(frozen=True)
class ThreeCheckGameState(GameState):
    """GameState for Three-Check Chess.
    
    Attributes:
        checks: Tuple (white_checks, black_checks) tracking checks given.
    """
    checks: Tuple[int, int] = (0, 0)


@dataclass(frozen=True)
class CrazyhouseGameState(GameState):
    """GameState for Crazyhouse Chess.
    
    Attributes:
        pockets: Tuple (white_pocket, black_pocket) tracking available drop pieces.
    """
    pockets: Tuple[Tuple["Piece", ...], Tuple["Piece", ...]] = ((), ())