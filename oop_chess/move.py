from dataclasses import dataclass
from typing import TYPE_CHECKING

from oop_chess.piece.pawn import Pawn
from oop_chess.piece.king import King
from oop_chess.square import Square
from oop_chess.enums import Color
from oop_chess.piece.piece import Piece
from oop_chess.piece import piece_from_char

if TYPE_CHECKING:
    from oop_chess.game import Game


@dataclass(frozen=True)
class Move:
    start: Square
    end: Square
    promotion_piece: Piece | None = None

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

    def get_san(self, game: "Game") -> str:
        """Returns the Standard Algebraic Notation (SAN) string for the move."""
        piece = game.board.get_piece(self.start)
        if piece is None:
            return self.uci

        # Castling
        if isinstance(piece, King) and abs(self.start.col - self.end.col) == 2:
            if self.end.col > self.start.col:
                return "O-O"
            else:
                return "O-O-O"

        san = ""
        piece_char = str(piece).upper()
        
        if not isinstance(piece, Pawn):
            san += piece_char

        # Disambiguation
        candidates = []
        # Find all pieces of the same type and color
        same_pieces = game.board.get_pieces(type(piece), piece.color)
        for p in same_pieces:
            if p.square == self.start:
                continue
            # Check if this piece can also move to the target square
            # We construct a temporary move
            candidate_move = Move(p.square, self.end, self.promotion_piece)
            if game.is_move_legal(candidate_move):
                candidates.append(p)

        if candidates:
            # Need disambiguation
            # 1. File if different
            file_distinct = True
            for c in candidates:
                if c.square.col == self.start.col:
                    file_distinct = False
                    break
            
            # 2. Rank if different (or if file not distinct)
            rank_distinct = True
            for c in candidates:
                if c.square.row == self.start.row:
                    rank_distinct = False
                    break

            if file_distinct:
                san += str(self.start).lower()[0]
            elif rank_distinct:
                san += str(self.start).lower()[1]
            else:
                san += str(self.start).lower()

        # Capture
        target = game.board.get_piece(self.end)
        is_en_passant = isinstance(piece, Pawn) and self.start.col != self.end.col and target is None
        
        if target is not None or is_en_passant:
            if isinstance(piece, Pawn):
                san += str(self.start).lower()[0] # Pawn capture requires file
            san += "x"
        
        san += str(self.end).lower()

        if self.promotion_piece:
            san += "=" + str(self.promotion_piece).upper()

        return san

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

    @classmethod
    def from_san_castling(cls, san_str: str, game: "Game") -> "Move":
        color = game.board.player_to_move
        if san_str == "O-O":
            if color == Color.WHITE:
                move = cls.from_uci("e1g1")
            else:
                move =  cls.from_uci("e8g8")
        else:
            if color == Color.WHITE:
                move = cls.from_uci("e1c1")
            else:
                move = cls.from_uci("e8c8")
        return move

    @classmethod
    def from_san_move(cls, san_str: str, game: "Game") -> "Move":
        """Parses a Standard Algebraic Notation string into a Move object.

        Args:
            san_str: The move string (e.g., "Nf3", "exd5").
            game: The current game state.

        Returns:
            The corresponding legal Move object.

        Raises:
            ValueError: If the move is ambiguous, illegal, or the format is invalid.
        """
        clean_san = san_str.replace("x", "").replace("+", "").replace("#", "").replace("(", "").replace(")", "")

        promotion_piece = None
        if "=" in clean_san:
            clean_san, promotion_char = clean_san.split("=")
            promotion_piece = piece_from_char[promotion_char](
                game.board.player_to_move
            )
        elif clean_san and clean_san[-1].isalpha() and clean_san[-1] in piece_from_char:
            # Handle implicit promotion (e.g., "a8Q")
            promotion_char = clean_san[-1]
            if promotion_char.upper() in ["Q", "R", "B", "N"]:
                clean_san = clean_san[:-1]
                promotion_piece = piece_from_char[promotion_char](
                    game.board.player_to_move
                )

        end_square = Square.from_str(clean_san[-2:])
        piece_indicator = clean_san[:-2]

        if piece_indicator and piece_indicator[0].isupper():
            piece_type = piece_from_char[piece_indicator[0]]
            disambiguation = piece_indicator[1:]
        else:
            piece_type = Pawn
            disambiguation = piece_indicator

        candidates = game.board.get_pieces(piece_type, game.board.player_to_move)

        if disambiguation:
            if disambiguation.isalpha():
                col = ord(disambiguation) - ord("a")
                candidates = [p for p in candidates if p.square.col == col]
            elif disambiguation.isdigit():
                row = 8 - int(disambiguation)
                candidates = [p for p in candidates if p.square.row == row]
            elif len(disambiguation) == 2:
                col = ord(disambiguation[0]) - ord("a")
                row = 8 - int(disambiguation[1])
                candidates = [p for p in candidates if p.square.col == col and p.square.row == row]

        legal_moves = [
            Move(piece.square, end_square, promotion_piece)
            for piece in candidates
            if game.is_move_legal(Move(piece.square, end_square, promotion_piece))
        ]

        if len(legal_moves) != 1:
            raise ValueError(f"San {san_str} is ambiguous or illegal. Found {len(legal_moves)} matches.")

        return legal_moves[0]

    @classmethod
    def from_san(cls, san_str: str, game: "Game") -> "Move":
        if san_str in ("O-O", "O-O-O"):
            return cls.from_san_castling(san_str, game)

        return cls.from_san_move(san_str, game)

    def __str__(self) -> str:
        return self.uci
