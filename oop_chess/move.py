from dataclasses import dataclass

from oop_chess.square import Square
from oop_chess.enums import Color
from oop_chess.piece.piece import Piece
from oop_chess.piece import piece_from_char


@dataclass(frozen=True)
class Move:
    start: Square
    end: Square
    promotion_piece: Piece | None = None
    is_castling: bool = False
    is_en_passant: bool = False

    @property
    def is_vertical(self) -> bool:
        return self.start.col == self.end.col

    @property
    def is_horizontal(self) -> bool:
        return self.start.row == self.end.row

    @property
    def is_diagonal(self) -> bool:
        return abs(self.start.col - self.end.col) == abs(self.start.row - self.end.row)

    @property
    def uci(self) -> str:
        """Returns the move in UCI format (e.g., 'e2e4', 'a7a8q')."""
        move_str = f"{self.start}{self.end}"
        if self.promotion_piece:
            move_str += self.promotion_piece.fen
        return move_str

    @staticmethod
    def is_uci_valid(uci_str: str):
        try:
            if not 3 < len(uci_str) < 6:
                return False
            Square.from_coord(uci_str[:2])
            Square.from_coord(uci_str[2:4])
            if len(uci_str) == 5:
                return uci_str[4] in piece_from_char.keys()
            return True
        except Exception as e:
            print(e)
            return False

    @classmethod
    def from_uci(cls, uci_str: str, player_to_move: Color = Color.WHITE) -> "Move":
        if not cls.is_uci_valid(uci_str):
            raise ValueError(f"Invalid move: {uci_str}")
        start = Square.from_coord(uci_str[:2])
        end = Square.from_coord(uci_str[2:4])

        promotion_char = uci_str[4:]
        piece = (
            piece_from_char[promotion_char](player_to_move) if promotion_char else None
        )

        return cls(start, end, piece)

    def __str__(self) -> str:
        return self.uci
