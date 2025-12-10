from typing import TypeVar
from itertools import chain

from oop_chess.move import Move
from oop_chess.piece import piece_from_char
from oop_chess.enums import Color, CastlingRight, Direction, StatusReason
from oop_chess.piece.pawn import Pawn
from oop_chess.piece.king import King
from oop_chess.piece.piece import Piece
from oop_chess.piece.rook import Rook
from oop_chess.square import Square


T = TypeVar("T", bound=Piece)


class Board:
    """Represents the current state of a chessboard."""

    STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    EMPTY_FEN = "8/8/8/8/8/8/8/8 w - - 0 1"

    def __init__(
        self,
        board: dict[Square, Piece | None],
        player_to_move: Color,
        castling_rights: list[CastlingRight],
        ep_square: Square | None,
        halfmove_clock: int,
        fullmove_count: int,
    ):
        self.board = board
        self.player_to_move = player_to_move
        self.castling_rights = castling_rights
        self.ep_square = ep_square
        self.halfmove_clock = halfmove_clock
        self.fullmove_count = fullmove_count

    @classmethod
    def starting_setup(cls) -> Board:
        return cls.from_fen(cls.STARTING_FEN)

    @classmethod
    def empty(cls) -> Board:
        return cls.from_fen(cls.EMPTY_FEN)

    def get_piece(self, coordinate: str | tuple | Square) -> Piece | None:
        return self.board.get(Square.from_any(coordinate))

    def set_piece(self, piece: Piece, square: str | tuple | Square):
        square = Square.from_any(square)
        self.board[square] = piece
        piece.square = square

    def remove_piece(self, coordinate: str | tuple | Square) -> None:
        square = Square.from_any(coordinate)
        piece_on_square = self.get_piece(square)
        if piece_on_square is None:
            return
        self.board[square] = None
        piece_on_square.square = None

    def switch_active_player(self):
        self.player_to_move = self.player_to_move.opposite

    @property
    def is_legal(self) -> bool:
        return self.status == StatusReason.VALID

    @property
    def status(self) -> StatusReason:
        """Return True if board state is legal."""
        white_kings = self.get_pieces(King, Color.WHITE)
        black_kings = self.get_pieces(King, Color.BLACK)
        white_pawns = self.get_pieces(Pawn, Color.WHITE)
        black_pawns = self.get_pieces(Pawn, Color.BLACK)
        white_non_pawns = [piece for piece in self.get_pieces(color=Color.WHITE) if not isinstance(piece, Pawn)]
        black_non_pawns = [piece for piece in self.get_pieces(color=Color.BLACK) if not isinstance(piece, Pawn)]
        white_piece_max = 16 - len(white_pawns)
        black_piece_max = 16 - len(black_pawns)
        pawns_on_backrank = [piece for piece in self.get_pieces(Pawn) if piece.is_on_first_or_last_row]
        print([str(p) for p in pawns_on_backrank])
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
            return StatusReason.INVALID_EP_SQUARE

        if not is_ep_square_valid:
            return StatusReason.INVALID_EP_SQUARE

        if self.inactive_player_in_check:
            return StatusReason.OPPOSITE_CHECK

        return StatusReason.VALID

    def is_under_attack(self, square: Square, by_color: Color) -> bool:
        """Check if square is attacked by the given color."""
        attackers = self.get_pieces(color=by_color)
        for piece in attackers:
            if isinstance(piece, Pawn):
                if square in piece.capture_squares:
                    return True
            elif square in self.unblocked_paths(piece):
                return True
        return False

    def player_in_check(self, color: Color) -> bool:
        king = self.get_pieces(King, color)[0]
        if king.square is None:
            raise AttributeError("King not found on board.")
        return self.is_under_attack(king.square, color.opposite)

    @property
    def current_player_in_check(self) -> bool:
        return self.player_in_check(self.player_to_move)

    @property
    def inactive_player_in_check(self) -> bool:
        return self.player_in_check(self.player_to_move.opposite)

    def _execute_castling_rook_move(self, target_coord: Square):
        self.update_castling_rights()
        rook_col = 0 if target_coord.col == 2 else 7
        rook_coord = Square.from_any((target_coord.row, rook_col))
        rook = self.get_piece(rook_coord)

        if rook is None:
            raise AttributeError(f"Expected rook on {rook_coord} found None.")

        direction = Direction.RIGHT if target_coord.col == 2 else Direction.LEFT
        end_coord = target_coord.adjacent(direction)

        self.move_piece(rook, end_coord)

    def get_pieces(
        self, piece_type: type[T] = Piece, color: Color | None = None
    ) -> list[T]:
        pieces = [piece for piece in self.board.values() if piece]
        pieces = [piece for piece in pieces if isinstance(piece, piece_type)]
        if color is not None:
            pieces = [piece for piece in pieces if piece.color.value == color.value]
        return pieces

    @property
    def pieces(self, color=None) -> list[Piece]:
        return [piece for piece in self.board.values() if piece]

    @property
    def current_players_pieces(self) -> list[Piece]:
        return self.get_pieces(color=self.player_to_move)

    @property
    def opponent_pieces(self):
        return self.get_pieces(color=self.player_to_move.opposite)

    def make_move(self, move: Move) -> None:
        piece = self.get_piece(move.start)

        if piece is None:
            raise ValueError(f"No piece found at start coord: {move.start}.")

        is_castling = isinstance(piece, King) and abs(move.start.col - move.end.col) == 2
        is_capture = self.get_piece(move.end) is not None or move.is_en_passant
        is_pawn_move = isinstance(piece, Pawn)

        self.halfmove_clock += 1
        if is_pawn_move or is_capture:
            self.halfmove_clock = 0

        self.move_piece(piece, move.end)

        if move.is_en_passant:
            direction = Direction.DOWN if piece.color == Color.WHITE else Direction.UP
            captured_coordinate = piece.square.adjacent(direction)
            self.remove_piece(captured_coordinate)

        if is_castling:
            try:
                self._execute_castling_rook_move(move.end)
            except AttributeError as e:
                print(f"Board.make_move: AttributeError during castling: {e}")
                print(f"Board.make_move: Current board FEN: {self.fen}")
                print(f"Board.make_move: Move that triggered error: {move}")
                raise e # Re-raise the exception after printing context

        if move.is_promotion:
            self.board[move.end] = move.promotion_piece
            move.promotion_piece.square = move.end

        self.ep_square = self._update_en_passant_square(move)
        self.switch_active_player()

    def unblocked_path(self, piece: Piece, path: list[Square]) -> list[Square]:
        try:
            stop_index = next(
                i for i, coord in enumerate(path) if self.get_piece(coord) is not None
            )
        except StopIteration:
            return path

        target_piece = self.get_piece(path[stop_index])

        if target_piece and target_piece.color != piece.color:
            return path[: stop_index + 1]
        else:
            return path[:stop_index]

    def unblocked_paths(self, piece: Piece) -> list[Square]:
        """Return all unblocked squares in a piece's moveset"""
        unblocked_paths = [
            self.unblocked_path(piece, path) for path in piece.theoretical_move_paths
        ]
        return list(chain.from_iterable(unblocked_paths))

    def _update_en_passant_square(self, move: Move):
        piece = self.get_piece(move.end)
        if piece is None or piece.square is None:
            raise ValueError("Invalid piece at move end.")
        direction = Direction.DOWN if piece.color == Color.WHITE else Direction.UP
        if isinstance(piece, Pawn) and abs(move.start.row - move.end.row) > 1:
            ep_square = piece.square.adjacent(direction)
            return ep_square
        return None

    @property
    def invalid_castling_rights(self) -> list[CastlingRight]:
        invalid_rights = []
        for castling_right in self.castling_rights:
            rook = self.get_piece(castling_right.expected_rook_square)
            king = self.get_piece(castling_right.expected_king_square)

            rook_valid = rook is not None and isinstance(rook, Rook) and not rook.has_moved
            king_valid = king is not None and isinstance(king, King) and not king.has_moved
            colors_valid = rook.color == king.color == castling_right.color

            if not all((rook_valid, king_valid, colors_valid)):
                invalid_rights.append(castling_right)

        return invalid_rights

    def update_castling_rights(self):
        for castling_right in self.invalid_castling_rights:
            self.castling_rights.remove(castling_right)

    def move_piece(self, piece: Piece, end: Square):
        start = piece.square
        self.set_piece(piece, end)
        self.remove_piece(start)
        piece.square = end
        piece.has_moved = True

    @property
    def fen(self) -> str:
        """Generates the FEN string representing the current board state."""
        fen_piece_placement = self._get_piece_placement_fen()
        fen_active_color = self.player_to_move.value

        fen_castling = "".join([r.value for r in self.castling_rights]) or "-"

        fen_en_passant = str(self.ep_square) if self.ep_square else "-"

        fen_halfmove_clock = str(self.halfmove_clock)
        fen_fullmove_number = str(self.fullmove_count)

        return " ".join(
            [
                fen_piece_placement,
                fen_active_color,
                fen_castling,
                fen_en_passant,
                fen_halfmove_clock,
                fen_fullmove_number,
            ]
        )

    @classmethod
    def from_fen(cls, fen: str) -> "Board":
        fen_parts = fen.split()
        if len(fen_parts) != 6:
            raise ValueError("Invalid FEN format: Must contain 6 fields.")

        board = cls._get_board_from_fen(fen_parts[0])
        active_color = Color(fen_parts[1])
        castling_rights = CastlingRight.from_fen(fen_parts[2])
        en_passant = None if fen_parts[3] == "-" else Square.from_any(fen_parts[3])

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

    @staticmethod
    def _get_board_from_fen(fen_board) -> dict[Square, Piece | None]:
        board: dict[Square, Piece | None] = {
            Square(r, c): None for r in range(8) for c in range(8)
        }
        fen_rows = fen_board.split("/")
        for row, fen_row in enumerate(fen_rows):
            empty_squares = 0
            for col, char in enumerate(fen_row):
                if char.isdigit():
                    empty_squares += int(char) - 1
                else:
                    is_white = char.isupper()
                    piece_color = Color.WHITE if is_white else Color.BLACK
                    piece_type = piece_from_char.get(char)
                    if piece_type is None:
                        raise ValueError(f"Invalid piece in FEN: {char}")
                    piece = piece_type(piece_color)
                    coord = Square(row, col + empty_squares)
                    board[coord] = piece
                    piece.square = coord
        return board

    def _get_fen_row(self, row) -> str:
        empty_squares = 0
        fen_row_string = ""
        for col in range(8):
            coord = Square(row, col)
            piece = self.board.get(coord)

            if piece is None:
                empty_squares += 1
                continue

            if empty_squares > 0:
                fen_row_string += str(empty_squares)
                empty_squares = 0

            fen_row_string += piece.fen

        if empty_squares > 0:
            fen_row_string += str(empty_squares)
        return fen_row_string

    def _get_piece_placement_fen(self) -> str:
        fen_rows = (self._get_fen_row(row) for row in range(8))
        return "/".join(fen_rows)

    def print(self):
        """Print the chess board.

        Draws a unicode based 2d-list representing the board state.
        printed output example:
            [♜, ♞, ♝, ♛, ♚, ♝, ♞, ♜]
            [♟, ♟, ♟, ♟, ♟, ♟, ♟, ♟]
            [0, 0, 0, 0, 0, 0, 0, 0]
            [0, 0, 0, 0, 0, 0, 0, 0]
            [0, 0, 0, 0, 0, 0, 0, 0]
            [0, 0, 0, 0, 0, 0, 0, 0]
            [♙, ♙, ♙, ♙, ♙, ♙, ♙, ♙]
            [♖, ♘, ♗, ♕, ♔, ♗, ♘, ♖]
        """
        grid = [[self.get_piece((r, c)) or 0 for c in range(8)] for r in range(8)]
        for row in grid:
            print([f"{piece}" for piece in row])

    def __str__(self):
        return self.fen

