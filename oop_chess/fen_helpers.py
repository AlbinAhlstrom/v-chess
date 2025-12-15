from typing import TYPE_CHECKING
from oop_chess.enums import CastlingRight, Color
from oop_chess.piece.piece import Piece
from oop_chess.square import Square
from oop_chess.piece import piece_from_char
if TYPE_CHECKING:
    from oop_chess.game_state import GameState
    from oop_chess.board import Board


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

def get_fen_from_board(board: "Board") -> str:
    """Generates the piece placement part of FEN."""
    fen_rows = []
    for row in range(8):
        empty_squares = 0
        fen_row_string = ""
        for col in range(8):
            coord = Square(row, col)
            piece = board.get_piece(coord)

            if piece is None:
                empty_squares += 1
                continue

            if empty_squares > 0:
                fen_row_string += str(empty_squares)
                empty_squares = 0

            fen_row_string += piece.fen

        if empty_squares > 0:
            fen_row_string += str(empty_squares)
        fen_rows.append(fen_row_string)

    return "/".join(fen_rows)

def state_from_fen(fen: str) -> "GameState":
    from oop_chess.game_state import GameState
    from oop_chess.board import Board

    fen_parts = fen.split()
    if len(fen_parts) != 6:
        raise ValueError("Invalid FEN format: Must contain 6 fields.")

    board = Board(fen_parts[0])
    active_color = Color(fen_parts[1])
    castling_rights = CastlingRight.from_fen(fen_parts[2])
    en_passant = None if fen_parts[3] == "-" else Square(fen_parts[3])

    try:
        halfmove_clock = int(fen_parts[4])
        fullmove_count = int(fen_parts[5])
    except ValueError:
        raise ValueError("FEN halfmove and fullmove must be int.")

    return GameState(
        board,
        active_color,
        castling_rights,
        en_passant,
        halfmove_clock,
        fullmove_count,
    )

def state_to_fen(state: GameState) -> str:
    """Serializes the state to FEN."""
    placement = state.board.fen
    active = state.turn.value

    rights_str = "".join([r.value for r in state.castling_rights]) or "-"

    ep = str(state.ep_square) if state.ep_square else "-"
    hm = str(state.halfmove_clock)
    fm = str(state.fullmove_count)

    return f"{placement} {active} {rights_str} {ep} {hm} {fm}"

