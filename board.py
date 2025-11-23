from string import ascii_lowercase

from chess.piece.color import Color
from chess.piece.piece import Piece
from chess.square import Square, Coordinate
from chess.move import Move


class Board:
    """Represents the current state of a chessboard."""

    def __init__(
        self,
        board: dict[tuple[int, int], Square],
        player_to_move: Color,
        castling_allowed: list[Color],
        en_passant_square: Square | None,
        halfmove_clock: int,
    ):
        self.board = board
        self.player_to_move = player_to_move
        self.castling_allowed = castling_allowed
        self.en_passant_square = en_passant_square
        self.halfmove_clock = halfmove_clock

    @classmethod
    def starting_setup(cls) -> "Board":
        """Create the initial chessboard setup."""
        from chess.piece.rook import Rook
        from chess.piece.knight import Knight
        from chess.piece.bishop import Bishop
        from chess.piece.queen import Queen
        from chess.piece.king import King
        from chess.piece.pawn import Pawn

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

    def get_pieces(self, piece_type=Piece, color=None) -> list[Piece]:
        pieces = self.pieces
        if color == Color.WHITE:
            pieces = self.white_pieces
        if color == Color.BLACK:
            pieces = self.black_pieces

        return [piece for piece in pieces if isinstance(piece, piece_type)]

    @property
    def squares(self):
        return [self.get_square((row, col)) for row in range(8) for col in range(8)]

    @property
    def pieces(self):
        return [square.piece for square in self.squares if square.piece]

    @property
    def white_pieces(self):
        return [piece for piece in self.pieces if piece.color == Color.WHITE]

    @property
    def black_pieces(self):
        return [piece for piece in self.pieces if piece.color == Color.BLACK]

    @property
    def current_players_pieces(self):
        if self.player_to_move == Color.WHITE:
            return self.white_pieces
        elif self.player_to_move == Color.BLACK:
            return self.black_pieces

    @property
    def opponent_pieces(self):
        if self.player_to_move == Color.WHITE:
            return self.black_pieces
        elif self.player_to_move == Color.BLACK:
            return self.white_pieces

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
    def current_players_king(self) -> "King":
        from chess.piece.king import King

        kings = self.get_pieces(King, self.player_to_move)
        assert len(kings) == 1, "Multiple kings of same color found"
        return kings[0]

    @property
    def current_players_rooks(self) -> list["Rook"]:
        from chess.piece.rook import Rook

        return self.get_pieces(Rook, self.player_to_move)

    @property
    def current_player_in_check(self) -> bool:
        king = self.current_players_king
        return any(
            [king.square.coordinate in piece.moves for piece in self.opponent_pieces]
        )

    def get_move(self, start, end):
        from chess.piece.pawn import Pawn

        piece = start.piece
        target_piece = end.piece

        if end == self.en_passant_square and isinstance(piece, Pawn):
            capture_square = Coordinate(start.row, end.col)
            target_square = self.get_square(capture_square)
            target_piece = target_square.piece

        return Move(start, end, piece, target_piece)

    @property
    def short_castle_allowed(self) -> bool:
        king = self.current_players_king
        if king.has_moved:
            return False
        try:
            rook = [
                rook for rook in self.current_players_rooks if rook.square.col == 7
            ][0]
            if rook.has_moved:
                return False
        except IndexError:
            return False

        if self.player_to_move == Color.BLACK:
            squares_to_check = [(0, 5), (0, 6)]
        else:
            squares_to_check = [(7, 5), (7, 6)]

        path_blocked = any(self.get_square(sq).is_occupied for sq in squares_to_check)
        if path_blocked:
            return False

        return True

    @property
    def long_castle_allowed(self) -> bool:
        king = self.current_players_king
        if king.has_moved:
            return False
        try:
            rook = [
                rook for rook in self.current_players_rooks if rook.square.col == 0
            ][0]
            if rook.has_moved:
                return False
        except IndexError:
            return False

        if self.player_to_move == Color.BLACK:
            squares_to_check = [(0, 1), (0, 2), (0, 3)]
        else:
            squares_to_check = [(7, 1), (7, 2), (7, 3)]

        path_blocked = any(self.get_square(sq).is_occupied for sq in squares_to_check)
        if path_blocked:
            return False

        return True

    def short_castle(self):
        king = self.current_players_king
        rook = [rook for rook in self.current_players_rooks if rook.square.col == 7][0]

        king.square.piece = None
        rook.square.piece = None

        king_square = (0, 6) if self.player_to_move == Color.BLACK else (7, 6)
        rook_square = (0, 5) if self.player_to_move == Color.BLACK else (7, 5)
        self.get_square(king_square).piece = king
        self.get_square(rook_square).piece = rook

    def long_castle(self):
        king = self.current_players_king
        rook = [rook for rook in self.current_players_rooks if rook.square.col == 0][0]

        king.square.piece = None
        rook.square.piece = None

        king_square = (0, 2) if self.player_to_move == Color.BLACK else (7, 2)
        rook_square = (0, 3) if self.player_to_move == Color.BLACK else (7, 3)
        self.get_square(king_square).piece = king
        self.get_square(rook_square).piece = rook
