from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from v_chess.piece.pawn import Pawn
from v_chess.piece.king import King
from v_chess.square import Square
from v_chess.enums import Color, MoveLegalityReason
from v_chess.piece.piece import Piece
from v_chess.piece import piece_from_char

if TYPE_CHECKING:
    from v_chess.game import Game


@dataclass(frozen=True, eq=True)
class Move:
    """A piece moving from one square to another."""
    start: Square = field(compare=True)
    end: Square = field(compare=True)
    promotion_piece: Piece | None = field(default=None, compare=True)
    drop_piece: Piece | None = field(default=None, compare=True)

    def __init__(self, *args, player_to_move: Color = Color.WHITE, **kwargs) -> None:
        """Initializes a Move.

        Can be initialized with:
        1. A UCI string (e.g., 'e2e4', 'P@e4').
        2. start and end Square objects.

        Args:
            *args: Variable arguments (UCI string or start/end Squares).
            player_to_move: The color of the player moving (used for parsing context).
            **kwargs: Keyword arguments for 'promotion_piece' and 'drop_piece'.
        """
        _start: Square = Square(None)
        _end: Square = Square(None)
        _promotion_piece: Piece | None = kwargs.get('promotion_piece')
        _drop_piece: Piece | None = kwargs.get('drop_piece')

        if len(args) == 1 and isinstance(args[0], str):
            uci_str = args[0]
            if "@" in uci_str:
                # Drop move: P@e4
                piece_char, square_str = uci_str.split("@")
                if piece_char in piece_from_char and Move.is_square_valid(square_str):
                    _start = Square(None) # NoneSquare
                    _end = Square(square_str)
                    _drop_piece = piece_from_char[piece_char](player_to_move)
                else:
                     raise ValueError(f"Invalid Drop UCI: {uci_str}")

            elif not Move.is_uci_valid(uci_str):
                raise ValueError(f"Invalid UCI string: {uci_str}")
            else:
                _start = Square(uci_str[:2])
                _end = Square(uci_str[2:4])
                if len(uci_str) == 5:
                    _promotion_piece = piece_from_char[uci_str[4:]](player_to_move)

        elif len(args) >= 2:
            if not (isinstance(args[0], Square) and isinstance(args[1], Square)):
                # If they are not squares, maybe they are coordinate tuples?
                _start = Square(args[0])
                _end = Square(args[1])
            else:
                _start = args[0]
                _end = args[1]

            if len(args) >= 3 and _promotion_piece is None:
                if isinstance(args[2], Piece) or args[2] is None:
                     _promotion_piece = args[2]

            if len(args) >= 4 and _drop_piece is None:
                if isinstance(args[3], Piece) or args[3] is None:
                     _drop_piece = args[3]

        object.__setattr__(self, 'start', _start)
        object.__setattr__(self, 'end', _end)
        object.__setattr__(self, 'promotion_piece', _promotion_piece)
        object.__setattr__(self, 'drop_piece', _drop_piece)

    @property
    def is_drop(self) -> bool:
        """Whether the move is a drop move (placing a piece from reserve)."""
        return self.drop_piece is not None

    @property
    def is_vertical(self) -> bool:
        """Whether the move is along a file."""
        if self.is_drop: return False
        return self.start.col == self.end.col

    @property
    def is_horizontal(self) -> bool:
        """Whether the move is along a rank."""
        if self.is_drop: return False
        return self.start.row == self.end.row

    @property
    def is_diagonal(self) -> bool:
        """Whether the move is diagonal."""
        if self.is_drop: return False
        return abs(self.start.col - self.end.col) == abs(self.start.row - self.end.row)

    @property
    def uci(self) -> str:
        """The move in UCI format (e.g., 'e2e4', 'a7a8q', 'P@e4')."""
        if self.is_drop:
            return f"{self.drop_piece.fen.upper()}@{self.end}"

        move_str = f"{self.start}{self.end}"
        if self.promotion_piece:
            move_str += self.promotion_piece.fen
        return move_str

    def get_san(self, game: "Game") -> str:
        """Generates the Standard Algebraic Notation (SAN) for the move.

        Args:
            game: The game context, used to resolve ambiguity and checks.

        Returns:
            The SAN string (e.g., 'Nf3', 'O-O', 'exd5').
        """
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

        for sq, p in game.state.board.items():
            if p and isinstance(p, type(piece)) and p.color == piece.color:
                if sq == self.start:
                    continue

                candidate_move = Move(sq, self.end, self.promotion_piece, player_to_move=game.state.turn)
                if game.rules.validate_move(game.state, candidate_move) == MoveLegalityReason.LEGAL:
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
        """Validates if a string is a well-formed UCI move."""
        try:
            if "@" in uci_str:
                parts = uci_str.split("@")
                if len(parts) != 2: return False
                return parts[0] in piece_from_char and Move.is_square_valid(parts[1])

            if not 3 < len(uci_str) < 6:
                return False
            Square(uci_str[:2])
            Square(uci_str[2:4])
            if len(uci_str) == 5:
                return uci_str[4] in piece_from_char.keys()
            return True
        except Exception as e:
            return False

    @staticmethod
    def is_square_valid(sq_str: str):
        """Validates if a string represents a valid square (e.g., 'e4')."""
        try:
            Square(sq_str)
            return True
        except:
            return False

    @classmethod
    def from_san_castling(cls, san_str: str, game: "Game") -> "Move":
        """Creates a castling Move from a SAN string."""
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
        """Parses a Standard Algebraic Notation string into a Move object.

        Args:
            san_str: The move string in SAN.
            game: The game context for resolving the move.

        Returns:
            The corresponding Move object.

        Raises:
             ValueError: If the SAN string is ambiguous or illegal.
        """

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
        for sq, p in game.state.board.items():
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
            if game.rules.validate_move(game.state, Move(sq, end_square, promotion_piece, player_to_move=game.state.turn)) == MoveLegalityReason.LEGAL
        ]
        if len(legal_moves) != 1:
            raise ValueError(f"San {san_str} is ambiguous or illegal. Found {len(legal_moves)} matches.")

        return legal_moves[0]

    @classmethod
    def from_san(cls, san_str: str, game: "Game") -> "Move":
        """Creates a Move from a SAN string (including castling)."""
        if san_str in ("O-O", "O-O-O"):
            return cls.from_san_castling(san_str, game)

        return cls.from_san_move(san_str, game)

    def __str__(self) -> str:
        return self.uci