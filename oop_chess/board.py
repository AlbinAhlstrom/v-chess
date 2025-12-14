from typing import TypeVar

from oop_chess.fen_helpers import board_from_fen, get_fen_board_row
from oop_chess.enums import Color
from oop_chess.piece.piece import Piece
from oop_chess.square import Coordinate, Square


T = TypeVar("T", bound=Piece)


class Board:
    """Represents the spatial configuration of pieces (The Database).

    It answers queries about piece locations and paths.
    It does NOT know about game state (turn, castling rights, etc.).
    """
    STARTING_POSITION_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
    EMPTY_BOARD_FEN = "8/8/8/8/8/8/8/8"

    def __init__(self, pieces: dict[Square, Piece] | str = {}):
        if isinstance(pieces, str):
            self.board = board_from_fen(pieces)
        elif isinstance(pieces, dict):
            self.board = pieces if pieces else {}

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

    @classmethod
    def empty(cls) -> "Board":
        return board_from_fen(cls.EMPTY_BOARD_FEN)

    @classmethod
    def starting_setup(cls):
        board_from_fen(cls.STARTING_POSITION_FEN)


    @property
    def fen(self) -> str:
        """Generates the piece placement part of FEN."""
        fen_rows = (get_fen_board_row(row) for row in range(8))
        return "/".join(fen_rows)

    def __str__(self):
        return self.fen

    def copy(self) -> "Board":
        return Board(self.board.copy())

