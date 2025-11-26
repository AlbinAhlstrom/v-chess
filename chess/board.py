from typing import TypeVar

from chess.piece import piece_from_char
from chess.enums import Color, CastlingRight
from chess.piece.piece import Piece
from chess.coordinate import Coordinate


T = TypeVar("T", bound=Piece)


class Board:
    """Represents the current state of a chessboard."""

    def __init__(
        self,
        board: dict[Coordinate, Piece | None],
        player_to_move: Color,
        castling_rights: list[CastlingRight],
        en_passant_square: Coordinate | None,
        halfmove_clock: int,
        fullmove_count: int,
    ):
        self.board: dict[Coordinate, Piece | None] = board
        self.player_to_move = player_to_move
        self.castling_rights = castling_rights
        self.en_passant_square = en_passant_square
        self.halfmove_clock = halfmove_clock
        self.fullmove_count = fullmove_count

    @classmethod
    def starting_setup(cls) -> "Board":
        start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        return cls.from_fen(start_fen)

    def get_piece(self, coordinate: str | tuple | "Coordinate"):
        return self.board.get(Coordinate.from_any(coordinate))

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

        (
            fen_board,
            fen_active_color,
            fen_castling,
            fen_en_passant,
            fen_halfmove_clock,
            fen_fullmove_number,
        ) = fen_parts

        board: dict[Coordinate, Piece | None] = {
            Coordinate(r, c): None for r in range(8) for c in range(8)
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
                    coord = Coordinate(row, col + empty_squares)
                    board[coord] = piece
                    piece.square = coord

        active_color = Color(fen_active_color)
        castling_rights = CastlingRight.from_fen(fen_castling)

        en_passant_square = (
            None if fen_en_passant == "-" else Coordinate.from_any(fen_en_passant)
        )

        try:
            halfmove_clock = int(fen_halfmove_clock)
            fullmove_count = int(fen_fullmove_number)
        except ValueError:
            raise ValueError("FEN halfmove and fullmove must be int.")

        return cls(
            board,
            active_color,
            castling_rights,
            en_passant_square,
            halfmove_clock,
            fullmove_count,
        )

    def _get_fen_row(self, row) -> str:
        empty_squares = 0
        fen_row_string = ""
        for col in range(8):
            coord = Coordinate(row, col)
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
