from __future__ import annotations
from typing import TypeVar

from oop_chess.fen_helpers import board_from_fen, get_fen_from_board
from oop_chess.enums import Color
from oop_chess.piece.piece import Piece
from oop_chess.square import Coordinate, Square
from oop_chess.bitboard import BitboardState


T = TypeVar("T", bound=Piece)


class Board:
    """Represents the spatial configuration of pieces (The Database).

    It answers queries about piece locations and paths.
    It does NOT know about game state (turn, castling rights, etc.).
    """
    STARTING_POSITION_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
    EMPTY_BOARD_FEN = "8/8/8/8/8/8/8/8"

    def __init__(self, pieces: dict[Square, Piece] | str = {}, _sync_bitboard=True):
        self.bitboard = BitboardState()

        if isinstance(pieces, str):
            self.board = board_from_fen(pieces)
        elif isinstance(pieces, dict):
            self.board = pieces if pieces else {}

        if _sync_bitboard:
            for sq, piece in self.board.items():
                self.bitboard.set_piece(sq.index, piece)

    def get_piece(self, coordinate: Coordinate) -> Piece | None:
        if isinstance(coordinate, Square):
            return self.board.get(coordinate)
        return self.board.get(Square(coordinate))

    def set_piece(self, piece: Piece, square: str | tuple | Square):
        if not isinstance(square, Square):
            square = Square(square)

        old_piece = self.board.get(square)
        if old_piece:
             self.bitboard.remove_piece(square.index, old_piece)

        self.board[square] = piece
        self.bitboard.set_piece(square.index, piece)

    def remove_piece(self, coordinate: Coordinate) -> Piece | None:
        if not isinstance(coordinate, Square):
            coordinate = Square(coordinate)

        piece = self.board.pop(coordinate, None)
        if piece:
            self.bitboard.remove_piece(coordinate.index, piece)
        return piece

    def move_piece(self, piece: Piece, start: Square, end: Square):
        """Moves a piece on the board. Does not handle capture logic or rules."""
        # We manually remove and set to ensure bitboard updates correct
        # remove_piece handles removing from bitboard
        # set_piece handles adding (and removing potential capture)

        self.remove_piece(start)
        self.set_piece(piece, end)

    def get_pieces(self, piece_type: type[T] = Piece, color: Color | None = None) -> list[T]:
        if piece_type == Piece and color is None:
             return list(self.board.values())

        if piece_type != Piece:
             mask = 0
             if color is not None:
                  mask = self.bitboard.pieces[color].get(piece_type, 0)
             else:
                  mask = self.bitboard.pieces[Color.WHITE].get(piece_type, 0) | \
                         self.bitboard.pieces[Color.BLACK].get(piece_type, 0)

             pieces = []
             temp_mask = mask
             while temp_mask:
                  idx = (temp_mask & -temp_mask).bit_length() - 1
                  sq = Square(divmod(idx, 8))
                  p = self.board.get(sq)
                  if p: pieces.append(p)
                  temp_mask &= temp_mask - 1
             return pieces

        pieces = [piece for piece in self.board.values() if piece]
        if color is not None:
            pieces = [piece for piece in pieces if piece.color == color]
        return pieces

    @classmethod
    def empty(cls) -> "Board":
        return cls(cls.EMPTY_BOARD_FEN)

    @classmethod
    def starting_setup(cls) -> "Board":
        return cls(cls.STARTING_POSITION_FEN)

    @property
    def fen(self) -> str:
        """Generates the piece placement part of FEN."""
        return get_fen_from_board(self)

    def __str__(self):
        return self.fen

    def copy(self) -> "Board":
        # Create new board with dictionary copy, skipping expensive initial sync
        new_board = Board(self.board.copy(), _sync_bitboard=False)
        # Fast copy of bitboard
        new_board.bitboard = self.bitboard.copy()
        return new_board

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
