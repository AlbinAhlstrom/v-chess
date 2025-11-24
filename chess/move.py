from dataclasses import dataclass
from typing import Optional

from chess.square import Square
from chess.piece.pawn import Pawn
from chess.piece.piece import Piece


@dataclass(frozen=True)
class Move:
    start: Square
    end: Square
    piece: Piece
    target_piece: Optional[Piece] = None
    was_first_move: bool = False
    promotion_piece: Optional[Piece] = None
    is_castling: bool = False

    @property
    def is_promotion(self) -> bool:
        return self.promotion_piece is not None

    @property
    def is_capture(self) -> bool:
        return self.target_piece is not None

    @property
    def is_double_pawn_push(self) -> bool:
        from chess.piece.pawn import Pawn

        return isinstance(self.piece, Pawn) and abs(self.start.row - self.end.row) == 2

    @property
    def is_en_passant(self) -> bool:
        from chess.piece.piece import Piece

        return (
            isinstance(self.piece, Pawn)
            and self.target_piece is None
            and self.start.col != self.end.col
        )

    @classmethod
    def from_uci_string(cls, uci_string, board) -> "Move":
        start = board.get_square(uci_string[:2])
        end = board.get_square(uci_string[2:])
        move = board.get_move(start, end)
        return move
