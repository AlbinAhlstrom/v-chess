from string import ascii_lowercase

from chess.piece.rook import Rook
from chess.piece.knight import Knight
from chess.piece.bishop import Bishop
from chess.piece.queen import Queen
from chess.piece.king import King
from chess.piece.pawn import Pawn
from chess.piece.color import Color
from chess.square import Square, Coordinate
from chess.move import Move


class Board:
    """Represents the current state of a chessboard."""

    def __init__(
        self,
        board: dict[tuple[int, int], Square],
        history: list[Board],
        player_to_move: Color,
        castling_allowed: list[Color],
        en_passant_square: Square | None,
        halfmove_clock: int,
    ):
        self.board = board
        self.history = history
        self.player_to_move = player_to_move
        self.castling_allowed = castling_allowed
        self.en_passant_square = en_passant_square
        self.halfmove_clock = halfmove_clock

    @classmethod
    def starting_setup(cls) -> "Board":
        """Create the initial chessboard setup."""
        board = {}

        for row in range(8):
            for col in range(8):
                board[(row, col)] = Square((row, col))

        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        for col, piece_cls in enumerate(piece_order):
            board[(0, col)].add_piece(piece_cls(Color.BLACK))
            board[(7, col)].add_piece(piece_cls(Color.WHITE))

        for col in range(8):
            board[(1, col)].add_piece(Pawn(Color.BLACK))
            board[(6, col)].add_piece(Pawn(Color.WHITE))

        return cls(
            board=board,
            history=[],
            player_to_move=Color.WHITE,
            castling_allowed=[Color.WHITE, Color.BLACK],
            en_passant_square=None,
            halfmove_clock=0,
        )

    def get_square(self, coordinate):
        """Retrieve a square by tuple or algebraic notation (e.g. 'e4')."""
        coord = Coordinate.from_any(coordinate)
        return self.board[(coord.row, coord.col)]

    def get_piece(self, coordinate):
        return self.get_square(coordinate).piece

    def make_move(self, move: Move):
        piece = move.start.piece
        move.start.piece = None
        move.end.piece = piece

    def path_is_clear(self, start_square: Square, end_square: Square) -> bool:
        piece = start_square.piece
        if not hasattr(piece, "lines"):
            return True

        path = [line for line in piece.lines if end_square in line]
        assert len(path) == 1, f"Expected one path, found: {path}"

        for square in path[0]:
            square = self.get_square(square)
            if square == end_square:
                break

            if square.is_occupied:
                print("Path blocked")
                return False

        return True

    @property
    def repetitions_of_position(self) -> int:
        return sum(1 for past in self.history if past.board == self.board)
