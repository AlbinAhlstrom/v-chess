from typing import TypeVar
from itertools import chain

from chess.move import Move
from chess.piece import piece_from_char
from chess.enums import Color, CastlingRight, Direction
from chess.piece.pawn import Pawn
from chess.piece.king import King
from chess.piece.piece import Piece
from chess.piece.rook import Rook
from chess.square import Square


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
        en_passant_square: Square | None,
        halfmove_clock: int,
        fullmove_count: int,
    ):
        self.board: dict[Square, Piece | None] = board
        self.player_to_move = player_to_move
        self.castling_rights = castling_rights
        self.en_passant_square = en_passant_square
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
    def is_legal(self) -> tuple[bool, str]:
        """Return True if board state is legal.

        Rules:
        - Must have exactly 1 king of each color.
        - Inactive players king can't be attacked.
        - Both color pawns are disallowed from ranks 1 and 8. (Below start and on promotion square)
        - Halfmove clock can not surpass 50.

        # TODO:
        - Castling rights must be reflected in positions of king and rook.
        - Maximum 8 pawns, 9 queens and 10 rooks, bishops and knights per side.
        - Each promoted piece has to result in 1 fewer pawn present.
        - En passant square must be on rank 3 or 6.
        - En passant square must be behind a pawn of correct color.
        """
        white_kings = self.get_pieces(King, Color.WHITE)
        black_kings = self.get_pieces(King, Color.BLACK)

        if not len(white_kings) == 1 and len(black_kings) == 1:
            return False, "Invalid king amount."

        if self.inactive_player_in_check:
            return False, f"Inactive player in check. ({self.player_to_move.opposite})"

        if any([pawn.square.row in [0,7] for pawn in self.get_pieces(Pawn, Color.WHITE)]):
            return False, "Pawn found on disallowed row."

        if self.halfmove_clock > 50:
            return False, "More than 50 moves since pawn move or capture."

        return True, "Board state is legal."

    def is_under_attack(self, square: Square, by_color: Color) -> bool:
        """Check if square is attacked by the given color."""
        attackers = self.get_pieces(color=by_color)
        return any([square in self.unblocked_paths(piece) for piece in attackers])

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
        pieces = [piece for piece in self.pieces if isinstance(piece, piece_type)]
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
        """Update piece positions and FEN state variables.

        Assumes that the move is pseudo-legal and legal.
        """
        piece = self.get_piece(move.start)

        if piece is None:
            raise ValueError(f"No piece found at start coord: {move.start}.")
        if piece.square is None:
            raise ValueError(f"Piece {piece} has no square.")

        is_castling = isinstance(piece, King) and abs(move.start.col - move.end.col) == 2

        self.halfmove_clock += 1
        if self.is_pawn_move(move) or self.is_capture(move):
            self.halfmove_clock = 0

        if self.player_to_move == Color.BLACK:
            self.fullmove_count += 1

        self.move_piece(piece, move.end)

        if move.is_en_passant:
            direction = Direction.DOWN if piece.color == Color.WHITE else Direction.UP
            captured_coordinate = piece.square.adjacent(direction)
            self.remove_piece(captured_coordinate)

        if is_castling:
            self._execute_castling_rook_move(move.end)

        if move.is_promotion:
            self.board[move.end] = move.promotion_piece
            move.promotion_piece.square = move.end

        self.en_passant_square = self._update_en_passant_square(move)
        self._update_castling_rights(piece, move.start)
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
        if self.is_pawn_move(move) and abs(move.start.row - move.end.row) > 1:
            en_passant_square = piece.square.adjacent(direction)
            return en_passant_square
        return None

    def remove_castling_rights(self, rights: set | CastlingRight):
        if isinstance(rights, CastlingRight):
            rights = {rights}
        for castling_right in rights:
            if castling_right in self.castling_rights:
                self.castling_rights.remove(castling_right)


    def _update_castling_rights(self, moved_piece: Piece, start: Square):

        short = CastlingRight.short(moved_piece.color)
        long = CastlingRight.long(moved_piece.color)
        is_rook_on_start_rank = isinstance(moved_piece, Rook) and (start.row == 0 or start.row == 7)
        rook_squares = {str(rook.square) for rook in self.get_pieces(Rook)}
        king_squares = {str(king.square) for king in self.get_pieces(King)}
        remove_rights = {
            "e1": {CastlingRight.WHITE_SHORT, CastlingRight.WHITE_LONG},
            "e8": {CastlingRight.BLACK_SHORT, CastlingRight.BLACK_LONG},
            "a1": {CastlingRight.WHITE_LONG},
            "a8": {CastlingRight.BLACK_LONG},
            "h1": {CastlingRight.WHITE_SHORT},
            "h8": {CastlingRight.BLACK_SHORT},
        }
        for square in remove_rights:
            castling_rights = remove_rights[square]
            if not square in rook_squares | king_squares:
                for castling_right in castling_rights:
                    if castling_right in self.castling_rights:
                        self.castling_rights.remove(castling_right)

        if (is_rook_on_start_rank and start.col == 7) or isinstance(moved_piece, King):
            if short in self.castling_rights:
                self.castling_rights.remove(short)

        if (is_rook_on_start_rank and start.col == 0) or isinstance(moved_piece, King):
            if long in self.castling_rights:
                self.castling_rights.remove(long_right)

    def move_piece(self, piece: Piece, end: Square):
        if piece.square is None:
            raise ValueError("Piece has no square.")

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

        fen_en_passant = str(self.en_passant_square) if self.en_passant_square else "-"

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

    def is_pawn_move(self, move: Move) -> bool:
        return isinstance(self.get_piece(move.start), Pawn)

    def is_capture(self, move: Move) -> bool:
        return self.get_piece(move.end) is not None or move.is_en_passant
