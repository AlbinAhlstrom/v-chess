from dataclasses import dataclass

from chess.square import Square
from chess.piece import Piece


@dataclass(frozen=True)
class Move:
    start: Square
    end: Square
    promotion_piece: Piece = None
    is_en_passant: bool = False
    is_castling: bool = False
    is_double_pawn_push: bool = False

    @property
    def is_promotion(self) -> bool:
        return self.promotion_piece is not None

    @property
    def is_capture(self) -> bool:
        return self.piece_captured is not None or self.is_en_passant
