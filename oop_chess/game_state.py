from dataclasses import dataclass
from typing import Optional

from oop_chess.board import Board
from oop_chess.move import Move
from oop_chess.square import Square
from oop_chess.enums import Color, CastlingRight, StatusReason, Direction
from oop_chess.piece import King, Pawn, Rook


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

        board = Board.from_fen_part(fen_parts[0])
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
        placement = self.board.fen_part
        active = self.turn.value

        rights_str = "".join([r.value for r in self.castling_rights]) or "-"

        ep = str(self.ep_square) if self.ep_square else "-"
        hm = str(self.halfmove_clock)
        fm = str(self.fullmove_count)

        return f"{placement} {active} {rights_str} {ep} {hm} {fm}"

    def __hash__(self):
        return hash(self.fen)

    def apply_move(self, move: Move) -> "GameState":
        """Returns a new GameState with the move applied."""
        new_board = self.board.copy()

        piece = new_board.get_piece(move.start)
        if piece is None:
            raise ValueError(f"No piece found at start coord: {move.start}.")

        target = new_board.get_piece(move.end)

        is_castling = isinstance(piece, King) and abs(move.start.col - move.end.col) == 2
        is_pawn_move = isinstance(piece, Pawn)
        is_en_passant = is_pawn_move and move.end == self.ep_square
        is_capture = target is not None or is_en_passant

        new_halfmove_clock = self.halfmove_clock + 1
        if is_pawn_move or is_capture:
            new_halfmove_clock = 0

        new_fullmove_count = self.fullmove_count
        if self.turn == Color.BLACK:
            new_fullmove_count += 1

        new_board.move_piece(piece, move.start, move.end)

        if is_en_passant:
            direction = Direction.DOWN if piece.color == Color.WHITE else Direction.UP
            captured_coordinate = move.end.adjacent(direction)
            new_board.remove_piece(captured_coordinate)

        if is_castling:
            rook_col = 0 if move.end.col == 2 else 7
            rook_coord = Square(move.end.row, rook_col)
            rook = new_board.get_piece(rook_coord)
            if rook:
                direction = Direction.RIGHT if move.end.col == 2 else Direction.LEFT
                end_coord = move.end.adjacent(direction)
                new_board.move_piece(rook, rook_coord, end_coord)

        if move.promotion_piece is not None:
            new_board.set_piece(move.promotion_piece, move.end)

        new_castling_rights = set(self.castling_rights)

        def revoke_rights(color: Color):
            to_remove = [r for r in new_castling_rights if r.color == color]
            for r in to_remove: new_castling_rights.discard(r)

        def revoke_rook_right(square: Square):
            to_remove = [r for r in new_castling_rights if r.expected_rook_square == square]
            for r in to_remove: new_castling_rights.discard(r)

        if isinstance(piece, King):
            revoke_rights(piece.color)

        if isinstance(piece, Rook):
            revoke_rook_right(move.start)

        if isinstance(target, Rook):
            revoke_rook_right(move.end)

        new_ep_square = None
        direction = Direction.DOWN if piece.color == Color.WHITE else Direction.UP
        if isinstance(piece, Pawn) and abs(move.start.row - move.end.row) > 1:
            new_ep_square = move.end.adjacent(direction)

        return GameState(
            board=new_board,
            turn=self.turn.opposite,
            castling_rights=tuple(sorted(new_castling_rights, key=lambda x: x.value)),
            ep_square=new_ep_square,
            halfmove_clock=new_halfmove_clock,
            fullmove_count=new_fullmove_count
        )

    @property
    def is_legal(self) -> bool:
        return self.status == StatusReason.VALID

    @property
    def status(self) -> StatusReason:
        """Return status of the state."""
        white_kings = self.board.get_pieces(King, Color.WHITE)
        black_kings = self.board.get_pieces(King, Color.BLACK)
        white_pawns = self.board.get_pieces(Pawn, Color.WHITE)
        black_pawns = self.board.get_pieces(Pawn, Color.BLACK)
        white_non_pawns = [piece for piece in self.board.get_pieces(color=Color.WHITE) if not isinstance(piece, Pawn)]
        black_non_pawns = [piece for piece in self.board.get_pieces(color=Color.BLACK) if not isinstance(piece, Pawn)]
        white_piece_max = 16 - len(white_pawns)
        black_piece_max = 16 - len(black_pawns)

        pawns_on_backrank = []
        for sq, piece in self.board.board.items():
             if isinstance(piece, Pawn) and (sq.row == 0 or sq.row == 7):
                 pawns_on_backrank.append(piece)

        is_ep_square_valid = self.ep_square is None or self.ep_square.row in (2, 5)

        if len(white_kings) < 1:
            return StatusReason.NO_WHITE_KING
        if len(black_kings) < 1:
            return StatusReason.NO_BLACK_KING
        if len(white_kings + black_kings) > 2:
            return StatusReason.TOO_MANY_KINGS
        if len(white_pawns) > 8:
            return StatusReason.TOO_MANY_WHITE_PAWNS
        if len(black_pawns) > 8:
            return StatusReason.TOO_MANY_BLACK_PAWNS
        if pawns_on_backrank:
            return StatusReason.PAWNS_ON_BACKRANK
        if len(white_non_pawns) > white_piece_max:
            return StatusReason.TOO_MANY_WHITE_PIECES
        if len(black_non_pawns) > black_piece_max:
            return StatusReason.TOO_MANY_BLACK_PIECES
        if self.invalid_castling_rights:
            return StatusReason.INVALID_CASTLING_RIGHTS
        if not is_ep_square_valid:
            return StatusReason.INVALID_EP_SQUARE
        if self.inactive_player_in_check:
            return StatusReason.OPPOSITE_CHECK
        return StatusReason.VALID

    @property
    def inactive_player_in_check(self) -> bool:
        return self.board.is_check(self.turn.opposite)

    @property
    def invalid_castling_rights(self) -> list[CastlingRight]:
        invalid = []
        for right in self.castling_rights:
            king = self.board.get_piece(right.expected_king_square)
            rook = self.board.get_piece(right.expected_rook_square)
            if not (isinstance(king, King) and king.color == right.color):
                invalid.append(right)
                continue
            if not (isinstance(rook, Rook) and rook.color == right.color):
                invalid.append(right)
                continue
        return invalid
