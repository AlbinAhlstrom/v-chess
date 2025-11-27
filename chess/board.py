from typing import TypeVar
from itertools import chain

from chess.move import Move
from chess.piece import piece_from_char
from chess.enums import Color, CastlingRight, Direction
from chess.piece.pawn import Pawn
from chess.piece.king import King
from chess.piece.piece import Piece
from chess.square import Square


T = TypeVar("T", bound=Piece)


class Board:
    """Represents the current state of a chessboard."""

    START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

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
    def starting_setup(cls) -> "Board":
        return cls.from_fen(cls.START_FEN)

    def get_piece(self, coordinate: str | tuple | Square) -> Piece | None:
        return self.board.get(Square.from_any(coordinate))

    def set_piece(self, piece: Piece | None, coordinate: str | tuple | Square):
        self.board[Square.from_any(coordinate)] = piece

    def remove_piece(self, target_coord: str | tuple | Square) -> None:
        self.set_piece(None, target_coord)

    def _execute_castling_rook_move(self, target_coord: Square):
        rook_col = 0 if target_coord.col == 2 else 7
        rook_coord = Square.from_any((target_coord.row, rook_col))
        rook = self.get_piece(rook_coord)

        if rook is None:
            raise AttributeError(f"Expected rook on {rook_coord} found None.")

        direction = Direction.RIGHT if target_coord.col == 2 else Direction.LEFT
        end_coord = target_coord.get_adjacent(direction)

        self.move_piece(rook, end_coord)

    def get_pieces(
        self, piece_type: type[T] = Piece, color: Color | None = None
    ) -> list[T]:
        pieces = [piece for piece in self.pieces if isinstance(piece, piece_type)]
        if color is not None:
            pieces = [piece for piece in pieces if piece.color == color]
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

        is_pawn_move = isinstance(piece, Pawn)
        is_capture = self.get_piece(move.end) is not None or move.is_en_passant

        self.halfmove_clock += 1
        if is_pawn_move or is_capture:
            self.halfmove_clock = 0

        if self.player_to_move == Color.BLACK:
            self.fullmove_count += 1

        self.move_piece(piece, move.end)

        if move.is_en_passant:
            direction = Direction.DOWN if piece.color == Color.WHITE else Direction.UP
            captured_coordinate = piece.square.get_adjacent(direction)
            self.remove_piece(captured_coordinate)

        if move.is_castling:
            self._execute_castling_rook_move(move.end)

        if move.is_promotion and move.promotion_piece is not None:
            self.board[move.end] = move.promotion_piece
            move.promotion_piece.square = move.end

        self.en_passant_square = self._update_en_passant_square(move, is_pawn_move)
        self._update_castling_rights(piece, move.start)
        self.player_to_move = self.player_to_move.opposite

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

    def pseudo_legal_end_squares(self, piece: Piece) -> list[Square]:
        unblocked_paths = [
            self.unblocked_path(piece, path) for path in piece.theoretical_move_paths
        ]
        return list(chain.from_iterable(unblocked_paths))

    def _update_en_passant_square(self, move: Move, is_pawn_move: bool):
        piece = self.get_piece(move.end)
        if piece is None or piece.square is None:
            raise ValueError("Invalid piece at move end.")
        direction = Direction.DOWN if piece.color == Color.WHITE else Direction.UP
        if is_pawn_move and abs(move.start.row - move.end.row) > 1:
            en_passant_square = piece.square.get_adjacent(direction)
            return en_passant_square
        return None

    def _update_castling_rights(self, moved_piece: Piece, start: Square):
        if isinstance(moved_piece, King):
            self.castling_rights.remove(CastlingRight.short(moved_piece.color))
            self.castling_rights.remove(CastlingRight.long(moved_piece.color))
        elif start.col == 7:
            self.castling_rights.remove(CastlingRight.short(moved_piece.color))
        elif start.col == 0:
            self.castling_rights.remove(CastlingRight.long(moved_piece.color))

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
