from typing import TypeVar
from itertools import chain

from oop_chess.move import Move
from oop_chess.piece import piece_from_char
from oop_chess.enums import Color, CastlingRight, Direction, StatusReason
from oop_chess.piece.pawn import Pawn
from oop_chess.piece.king import King
from oop_chess.piece.piece import Piece
from oop_chess.piece.rook import Rook
from oop_chess.piece.knight import Knight
from oop_chess.square import Coordinate, NoSquare, Square


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

    def get_piece(self, coordinate: Coordinate) -> Piece | None:
        return self.board.get(Square.from_coord(coordinate))

    def set_piece(self, piece: Piece, square: str | tuple | Square):
        square = Square.from_coord(square)
        self.board[square] = piece

    def remove_piece(self, coordinate: Coordinate) -> Piece | None:
        square = Square.from_coord(coordinate)
        return self.board.pop(square, None)

    def move_piece(self, piece: Piece, start: Square, end: Square):
        """Moves a piece on the board. Does not handle capture logic or rules."""
        self.set_piece(piece, end)
        self.remove_piece(start)

    def get_pieces(
        self, piece_type: type[T] = Piece, color: Color | None = None
    ) -> list[T]:
        pieces = [piece for piece in self.board.values() if piece]
        pieces = [piece for piece in pieces if isinstance(piece, piece_type)]
        if color is not None:
            pieces = [piece for piece in pieces if piece.color.value == color.value]
        return pieces

    def is_attacking(self, piece: Piece, square: Square, piece_square: Square) -> bool:
        if isinstance(piece, (Knight)):
            return square in piece.capture_squares(piece_square)
        else:
            return square in self.unblocked_paths(piece, piece.capture_paths(piece_square))

    def is_under_attack(self, square: Square, by_color: Color) -> bool:
        """Check if square is attacked by the given color."""
        for piece_square, piece in self.board.items():
            if piece and piece.color == by_color:
                if self.is_attacking(piece, square, piece_square):
                    return True
        return False

    def is_check(self, color: Color) -> bool:
        """Check if the King of the given color is under attack."""
        king_sq = None
        for sq, piece in self.board.items():
            if isinstance(piece, King) and piece.color == color:
                king_sq = sq
                break

        if king_sq is None:
            return False

        return self.is_under_attack(king_sq, color.opposite)

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

    def unblocked_paths(self, piece: Piece, paths: list[list[Square]]) -> list[Square]:
        """Return all unblocked squares in a piece's moveset"""
        return list(chain.from_iterable([self.unblocked_path(piece, path) for path in paths]))

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

