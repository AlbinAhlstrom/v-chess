from typing import TypeVar
from itertools import chain

from oop_chess.piece import piece_from_char
from oop_chess.enums import Color
from oop_chess.piece.pawn import Pawn
from oop_chess.piece.king import King
from oop_chess.piece.piece import Piece
from oop_chess.piece.rook import Rook
from oop_chess.piece.knight import Knight
from oop_chess.square import Coordinate, Square


T = TypeVar("T", bound=Piece)


class Board:
    """Represents the spatial configuration of pieces (The Database).

    It answers queries about piece locations and paths.
    It does NOT know about game state (turn, castling rights, etc.).
    """



    STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    EMPTY_FEN = "8/8/8/8/8/8/8/8 w - - 0 1"

    def __init__(self, pieces: dict[Square, Piece] = None):
        self.board: dict[Square, Piece] = pieces if pieces else {}

    @classmethod
    def empty(cls) -> "Board":
        return cls()

    @classmethod
    def starting_setup(cls) -> "Board":
        return cls.from_fen(cls.STARTING_FEN)

    @classmethod
    def from_fen(cls, fen: str) -> "Board":
        """Parses the piece placement part of a FEN string."""

        fen_part = fen.split()[0]
        return cls.from_fen_part(fen_part)

    @classmethod
    def from_fen_part(cls, fen_board: str) -> "Board":
        """Parses just the piece placement part of a FEN string."""
        board: dict[Square, Piece] = {}
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
        return cls(board)

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

    @property
    def fen_part(self) -> str:
        """Generates the piece placement part of FEN."""
        fen_rows = (self._get_fen_row(row) for row in range(8))
        return "/".join(fen_rows)

    def __str__(self):

        return self.fen_part

    def copy(self) -> "Board":
        return Board(self.board.copy())
