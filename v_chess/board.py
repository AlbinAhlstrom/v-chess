from __future__ import annotations
from typing import TypeVar, Generator, TYPE_CHECKING

from v_chess.fen_helpers import board_from_fen, get_fen_from_board
from v_chess.enums import Color
from v_chess.piece.piece import Piece
from v_chess.square import Coordinate, Square
from v_chess.bitboard import Bitboard

if TYPE_CHECKING:
    from v_chess.piece import Piece

T = TypeVar("T", bound=Piece)


class Board:
    """Represents the spatial configuration of pieces (The Database).

    It answers queries about piece locations and paths.
    It does NOT know about game state (turn, castling rights, etc.).
    """
    STARTING_POSITION_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
    EMPTY_BOARD_FEN = "8/8/8/8/8/8/8/8"

    def __init__(self, setup: Bitboard | str = EMPTY_BOARD_FEN):
        """Initializes the Board.

        Args:
            setup: A Bitboard object or a FEN string.
        """
        if isinstance(setup, Bitboard):
            self.bitboard = setup.copy()
        elif isinstance(setup, str):
            self.bitboard = Bitboard()
            initial_pieces = board_from_fen(setup)
            for sq, piece in initial_pieces.items():
                self.bitboard.set_piece(sq.index, piece)
        else:
            raise TypeError(f"setup must be Bitboard or str, not {type(setup)}")

    def get_piece(self, coordinate: Coordinate) -> Piece | None:
        """Gets the piece at a specific coordinate.

        Args:
            coordinate: The coordinate (Square or tuple/str) to check.

        Returns:
            The Piece at the coordinate, or None if empty.
        """
        if not isinstance(coordinate, Square):
            coordinate = Square(coordinate)

        p_type, color = self.bitboard.piece_at(coordinate.index)
        if p_type and color:
            return p_type(color)
        return None

    def set_piece(self, piece: Piece, square: str | tuple | Square):
        """Sets a piece at a specific square.

        Args:
            piece: The piece to place.
            square: The square to place the piece on.
        """
        if not isinstance(square, Square):
            square = Square(square)

        old_piece = self.get_piece(square)
        if old_piece:
             self.bitboard.remove_piece(square.index, old_piece)

        self.bitboard.set_piece(square.index, piece)

    def remove_piece(self, coordinate: Coordinate) -> Piece | None:
        """Removes a piece from a specific coordinate.

        Args:
            coordinate: The coordinate to remove the piece from.

        Returns:
            The removed Piece, or None if the square was empty.
        """
        if not isinstance(coordinate, Square):
            coordinate = Square(coordinate)

        piece = self.get_piece(coordinate)
        if piece:
            self.bitboard.remove_piece(coordinate.index, piece)
        return piece

    def move_piece(self, piece: Piece, start: Square, end: Square):
        """Moves a piece on the board.

        Does not handle capture logic or rules validation.

        Args:
            piece: The piece being moved.
            start: The starting square.
            end: The destination square.
        """
        self.remove_piece(start)
        self.set_piece(piece, end)

    def get_pieces(self, piece_type: type[T] = Piece, color: Color | None = None) -> list[T]:
        """Gets a list of pieces matching the criteria.

        Args:
            piece_type: The type of piece to filter by. Defaults to Piece (all types).
            color: The color to filter by. Defaults to None (all colors).

        Returns:
            A list of pieces on the board matching the criteria.
        """
        pieces = []
        colors = [color] if color else [Color.WHITE, Color.BLACK]

        for c in colors:
            types_to_check = [piece_type] if piece_type != Piece else self.bitboard.pieces[c].keys()
            for p_cls in types_to_check:
                mask = self.bitboard.pieces[c][p_cls]
                while mask:
                    mask &= mask - 1
                    pieces.append(p_cls(c))

        return pieces

    def items(self) -> Generator[tuple[Square, Piece], None, None]:
        """Yields (Square, Piece) pairs for all pieces on the board."""
        occupied = self.bitboard.occupied
        while occupied:
            idx = (occupied & -occupied).bit_length() - 1
            sq = Square(divmod(idx, 8))
            p_type, color = self.bitboard.piece_at(idx)
            if p_type and color:
                yield sq, p_type(color)
            occupied &= occupied - 1

    def values(self) -> Generator[Piece, None, None]:
        """Yields all Pieces on the board."""
        for _, piece in self.items():
            yield piece

    def __len__(self) -> int:
        """Returns the number of pieces on the board."""
        # Count set bits in occupied bitmask
        return bin(self.bitboard.occupied).count('1')

    @classmethod
    def empty(cls) -> "Board":
        """Creates an empty board.

        Returns:
            A new Board instance with no pieces.
        """
        return cls(cls.EMPTY_BOARD_FEN)

    @classmethod
    def starting_setup(cls) -> "Board":
        """Creates a board with the standard starting position.

        Returns:
            A new Board instance with the standard chess starting position.
        """
        return cls(cls.STARTING_POSITION_FEN)

    @property
    def fen(self) -> str:
        """Generates the piece placement part of FEN.

        Returns:
            The FEN string representing the board state.
        """
        return get_fen_from_board(self)

    def __str__(self):
        """Returns the FEN string of the board."""
        return self.fen

    def copy(self) -> "Board":
        """Creates a shallow copy of the board.

        Returns:
            A new Board instance with the same piece configuration.
        """
        return Board(self.bitboard)

    def print(self):
        """Prints the chess board to the console.

        Draws a unicode based 2d-list representing the board state.
        """
        grid = [[self.get_piece((r, c)) or 0 for c in range(8)] for r in range(8)]
        for row in grid:
            print([f"{piece}" for piece in row])
