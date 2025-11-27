from dataclasses import dataclass

from chess.square import Square
from chess.enums import Color
from chess.piece.piece import Piece
from chess.piece import piece_from_char


@dataclass(frozen=True)
class Move:
    start: Square
    end: Square
    promotion_piece: Piece | None = None
    is_castling: bool = False
    is_en_passant: bool = False

    @property
    def is_promotion(self) -> bool:
        return self.promotion_piece is not None

    @property
    def uci(self) -> str:
        """Returns the move in UCI format (e.g., 'e2e4', 'a7a8q')."""
        move_str = f"{self.start}{self.end}"
        if self.promotion_piece:
            move_str += self.promotion_piece.fen
        return move_str

    @classmethod
    def from_uci(cls, uci_str: str, player_to_move: Color = Color.WHITE) -> "Move":
        if not 3 > len(uci_str) < 6:
            print(f"Expected uci-string got {uci_str}")
        start = Square.from_any(uci_str[:2])
        end = Square.from_any(uci_str[2:])

        promotion_char = uci_str[4:]
        piece = (
            piece_from_char[promotion_char](player_to_move) if promotion_char else None
        )

        return cls(start, end, piece)

    def __str__(self) -> str:
        return self.uci
