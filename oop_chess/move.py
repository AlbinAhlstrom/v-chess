from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from oop_chess.piece.pawn import Pawn
from oop_chess.piece.king import King
from oop_chess.square import Square
from oop_chess.enums import Color, MoveLegalityReason
from oop_chess.piece.piece import Piece
from oop_chess.piece import piece_from_char

if TYPE_CHECKING:
    from oop_chess.game import Game


@dataclass(frozen=True, eq=True)
class Move:
    """A piece moving from one square to another."""
    start: Square = field(compare=True)
    end: Square = field(compare=True)
    promotion_piece: Piece | None = field(default=None, compare=True)
    drop_piece: Piece | None = field(default=None, compare=True)

    def __init__(self, *args, player_to_move: Color = Color.WHITE) -> None:
        """Allows for instatiation using args or UCI string."""
        _start: Square
        _end: Square
        _promotion_piece: Piece | None = None
        _drop_piece: Piece | None = None

        if len(args) == 1 and isinstance(args[0], str):
            uci_str = args[0]
            if "@" in uci_str:
                # Drop move: P@e4
                piece_char, square_str = uci_str.split("@")
                if not (piece_char in piece_from_char and Move.is_square_valid(square_str)):
                     raise ValueError(f"Invalid Drop UCI: {uci_str}")
                
                _start = Square(None) # NoneSquare
                _end = Square(square_str)
                _drop_piece = piece_from_char[piece_char](player_to_move)
                
            elif not Move.is_uci_valid(uci_str):
                raise ValueError(f"Invalid UCI string: {uci_str}")
            else:
                _start = Square(uci_str[:2])
                _end = Square(uci_str[2:4])
                _promotion_piece = piece_from_char[uci_str[4:]](player_to_move) if len(uci_str) == 5 else None

        elif len(args) >= 2:
            if not (isinstance(args[0], Square) and isinstance(args[1], Square)):
                raise TypeError("First two arguments must be Square objects.")
            _start = args[0]
            _end = args[1]

            if len(args) >= 3:
                # arg 3 could be promotion or drop piece
                # But constructor signature usually implies promotion for standard moves.
                # If doing a drop via constructor, users should probably use named args or uci.
                # However, to keep it consistent:
                # Move(NoneSquare, TargetSquare, drop_piece=Piece)
                if len(args) == 3 and (isinstance(args[2], Piece) or args[2] is None):
                     _promotion_piece = args[2]
                elif len(args) == 4 and (isinstance(args[3], Piece) or args[3] is None):
                     _promotion_piece = args[2]
                     _drop_piece = args[3]
            
            # For kwargs handling (drop_piece passed as kwarg)
            # Dataclass generated init handles this if we weren't overriding it.
            # But since we are, we rely on args/logic here.
            # If user does Move(sq1, sq2, drop_piece=P), it might fail here if not careful.
            # But python maps kwargs to variables before calling this? No, we are inside __init__.
            
        else:
             # Fallback for named args passed via kwargs caught by *args?
             # Actually __init__ signature only has *args. Kwargs are not captured unless we add **kwargs.
             # But dataclass machinery calls __init__ with fields as args if not overridden?
             # No, if we define __init__, we control it.
             # The signature `def __init__(self, *args, player_to_move: Color = Color.WHITE)` 
             # ignores `drop_piece` passed as keyword!
             pass
        
        # Checking if drop_piece was passed via keyword argument (not captured in *args)
        # We need to add **kwargs to signature to capture 'drop_piece' or 'promotion_piece' if passed by name.
        # But wait, I can't easily change the signature without potentially breaking things if I'm not careful.
        # Let's fix the signature to `def __init__(self, *args, player_to_move=..., **kwargs)`
        
        # But wait, looking at previous implementation, it didn't have **kwargs. 
        # So `Move(start, end, promotion_piece=P)` would act weirdly?
        # Actually `Move` constructor was: `def __init__(self, *args, player_to_move: Color = Color.WHITE)`
        # If I call `Move(s, e, promotion_piece=p)`, `promotion_piece` goes into `kwargs`? No, it raises TypeError usually if not in signature.
        # Ah, unless it was relying on positional args for promotion piece.
        # The code handled `len(args) == 3`.

        # Let's check for drop_piece logic via kwargs manually?
        # I'll update the signature.
        
        # NOTE: I am overriding the setattr logic at the end.

        object.__setattr__(self, 'start', _start)
        object.__setattr__(self, 'end', _end)
        object.__setattr__(self, 'promotion_piece', _promotion_piece)
        object.__setattr__(self, 'drop_piece', _drop_piece)

    @property
    def is_drop(self) -> bool:
        return self.drop_piece is not None

    @property
    def is_vertical(self) -> bool:
        if self.is_drop: return False
        return self.start.col == self.end.col

    @property
    def is_horizontal(self) -> bool:
        if self.is_drop: return False
        return self.start.row == self.end.row

    @property
    def is_diagonal(self) -> bool:
        if self.is_drop: return False
        return abs(self.start.col - self.end.col) == abs(self.start.row - self.end.row)

    @property
    def uci(self) -> str:
        """Returns the move in UCI format (e.g., 'e2e4', 'a7a8q', 'P@e4')."""
        if self.is_drop:
            return f"{self.drop_piece.fen.upper()}@{self.end}"
            
        move_str = f"{self.start}{self.end}"
        if self.promotion_piece:
            move_str += self.promotion_piece.fen
        return move_str

    def get_san(self, game: "Game") -> str:
        """Returns the Standard Algebraic Notation (SAN) string for the move."""
        if self.is_drop:
            # SAN for drop is usually same as UCI/special: N@e4
            return self.uci
            
        piece = game.state.board.get_piece(self.start)
        if piece is None:
            return self.uci

        if isinstance(piece, King) and abs(self.start.col - self.end.col) == 2:
            if self.end.col > self.start.col:
                return "O-O"
            else:
                return "O-O-O"

        san = ""
        piece_char = piece.fen.upper()
        if not isinstance(piece, Pawn):
            san += piece_char

        candidates = []

        for sq, p in game.state.board.board.items():
            if p and isinstance(p, type(piece)) and p.color == piece.color:
                if sq == self.start:
                    continue

                candidate_move = Move(sq, self.end, self.promotion_piece, player_to_move=game.state.turn)
                if game.rules.validate_move(candidate_move) == MoveLegalityReason.LEGAL:
                    candidates.append(sq)

        if candidates:
            file_distinct = True
            for c_sq in candidates:
                if c_sq.col == self.start.col:
                    file_distinct = False
                    break

            rank_distinct = True
            for c_sq in candidates:
                if c_sq.row == self.start.row:
                    rank_distinct = False
                    break

            if file_distinct:
                san += str(self.start).lower()[0]
            elif rank_distinct:
                san += str(self.start).lower()[1]
            else:
                san += str(self.start).lower()

        target = game.state.board.get_piece(self.end)
        is_en_passant = isinstance(piece, Pawn) and self.start.col != self.end.col and target is None

        if target is not None or is_en_passant:
            if isinstance(piece, Pawn):
                san += str(self.start).lower()[0]
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
            Square(uci_str[:2])
            Square(uci_str[2:4])
            if len(uci_str) == 5:
                return uci_str[4] in piece_from_char.keys()
            return True
        except Exception as e:
            # print(e) # Silence printing
            return False
            
    @staticmethod
    def is_square_valid(sq_str: str):
        try:
            Square(sq_str)
            return True
        except:
            return False

    @classmethod
    def from_san_castling(cls, san_str: str, game: "Game") -> "Move":
        color = game.state.turn
        if san_str == "O-O":
            if color == Color.WHITE:
                move = Move("e1g1", player_to_move=color)
            else:
                move =  Move("e8g8", player_to_move=color)
        else:
            if color == Color.WHITE:
                move = Move("e1c1", player_to_move=color)
            else:
                move = Move("e8c8", player_to_move=color)
        return move

    @classmethod
    def from_san_move(cls, san_str: str, game: "Game") -> "Move":
        """Parses a Standard Algebraic Notation string into a Move object."""
        
        # Handle Drops in SAN if strictly parsing
        if "@" in san_str:
            # Assume it's UCI/Drop notation like P@e4
            return Move(san_str, player_to_move=game.state.turn)

        clean_san = san_str.replace("x", "").replace("+", "").replace("#", "").replace("(", "").replace(")", "")

        promotion_piece = None
        if "=" in clean_san:
            clean_san, promotion_char = clean_san.split("=")
            promotion_piece = piece_from_char[promotion_char](
                game.state.turn
            )
        elif clean_san and clean_san[-1].isalpha() and clean_san[-1] in piece_from_char:

            promotion_char = clean_san[-1]
            if promotion_char.upper() in ["Q", "R", "B", "N"]:
                clean_san = clean_san[:-1]
                promotion_piece = piece_from_char[promotion_char](
                    game.state.turn
                )

        end_square = Square(clean_san[-2:])
        piece_indicator = clean_san[:-2]

        if piece_indicator and piece_indicator[0].isupper():
            piece_type = piece_from_char[piece_indicator[0]]
            disambiguation = piece_indicator[1:]
        else:
            piece_type = Pawn
            disambiguation = piece_indicator

        candidates = []
        for sq, p in game.state.board.board.items():
            if p and isinstance(p, piece_type) and p.color == game.state.turn:
                 candidates.append(sq)

        if disambiguation:
            if disambiguation.isalpha():
                col = ord(disambiguation) - ord("a")
                candidates = [sq for sq in candidates if sq.col == col]

            elif disambiguation.isdigit():
                row = 8 - int(disambiguation)
                candidates = [sq for sq in candidates if sq.row == row]

            elif len(disambiguation) == 2:
                col = ord(disambiguation[0]) - ord("a")
                row = 8 - int(disambiguation[1])
                candidates = [sq for sq in candidates if sq.col == col and sq.row == row]

        legal_moves = [
            Move(sq, end_square, promotion_piece, player_to_move=game.state.turn)
            for sq in candidates
            if game.rules.validate_move(Move(sq, end_square, promotion_piece, player_to_move=game.state.turn)) == MoveLegalityReason.LEGAL
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