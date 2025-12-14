from dataclasses import dataclass
from typing import Optional

from oop_chess.board import Board
from oop_chess.square import Square
from oop_chess.enums import Color, CastlingRight


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

    @classmethod
    def starting_setup(cls) -> "GameState":
        return cls.from_fen(cls.STARTING_FEN)

    @classmethod
    def from_fen(cls, fen: str) -> "GameState":
        fen_parts = fen.split()
        if len(fen_parts) != 6:
            raise ValueError("Invalid FEN format: Must contain 6 fields.")

        board = Board.from_fen(fen_parts[0])
        active_color = Color(fen_parts[1])
        castling_rights = tuple(CastlingRight.from_fen(fen_parts[2]))
        en_passant = None if fen_parts[3] == "-" else Square.from_coord(fen_parts[3])

        try:
            halfmove_clock = int(fen_parts[4])
            fullmove_count = int(fen_parts[5])
        except ValueError:
            raise ValueError("FEN halfmove and fullmove must be int.")

        return cls(
            board,
            active_color,
            castling_rights,
            en_passant,
            halfmove_clock,
            fullmove_count,
        )

    @property
    def fen(self) -> str:
        """Serializes the state to FEN."""
        placement = self.board.fen
        active = self.turn.value

        rights_str = "".join([r.value for r in self.castling_rights]) or "-"

        ep = str(self.ep_square) if self.ep_square else "-"
        hm = str(self.halfmove_clock)
        fm = str(self.fullmove_count)

        return f"{placement} {active} {rights_str} {ep} {hm} {fm}"

    def __hash__(self):
        return hash(self.fen)

