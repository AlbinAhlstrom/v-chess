from dataclasses import dataclass, field

from chess.square import Square
from chess.piece import Piece
from chess.piece.pawn import Pawn


@dataclass(frozen=True)
class Move:
    start: Square
    end: Square
    promotion_piece: Piece = None
    is_en_passant: bool = False
    is_castling: bool = False

    piece: Piece = field(init=False)
    target_piece: Optional[Piece] = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "piece", self.start.piece)
        object.__setattr__(self, "target_piece", self.end.piece)

    @property
    def is_promotion(self) -> bool:
        return self.promotion_piece is not None

    @property
    def is_capture(self) -> bool:
        return self.piece_captured is not None or self.is_en_passant

    @property
    def is_double_pawn_push(self) -> bool:
        print(f"{isinstance(self.piece, Pawn)=}")
        print(f"{self.start.row - self.end.row=}")
        return isinstance(self.piece, Pawn) and abs(self.start.row - self.end.row) == 2
