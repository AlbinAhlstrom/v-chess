from oop_chess.enums import Color
from oop_chess.piece.piece import Piece
from oop_chess.square import Square
from oop_chess.piece import piece_from_char


def board_from_fen(fen_board: str) -> dict[Square, Piece]:
    """Gets a piece dict from the board part of a fen string."""
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
    return board

def get_fen_board_row(self, row) -> str:
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
