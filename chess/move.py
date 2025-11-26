from dataclasses import dataclass

from chess.coordinate import Coordinate
from chess.piece.piece import Piece


@dataclass(frozen=True)
class Move:
    start: Coordinate
    end: Coordinate
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
    def from_uci(cls, uci_string, board) -> "Move":
        start = board.get_square(uci_string[:2])
        end = board.get_square(uci_string[2:])
        move = board.get_move(start, end)
        return move

    def __str__(self) -> str:
        return self.uci
