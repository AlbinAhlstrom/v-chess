from typing import TYPE_CHECKING
from v_chess.enums import CastlingRight, Color
from v_chess.piece.piece import Piece
from v_chess.square import Square
from v_chess.piece import piece_from_char

if TYPE_CHECKING:
    from v_chess.game_state import GameState
    from v_chess.board import Board


def board_from_fen(fen_board: str) -> dict[Square, Piece]:
    """Parses the piece placement part of a FEN string.

    Args:
        fen_board: The piece placement part of a FEN string.

    Returns:
        A dictionary mapping Squares to Pieces.

    Raises:
        ValueError: If the FEN string contains invalid characters.
    """
    # Strip pocket info if present for board parsing
    if "[" in fen_board:
        fen_board = fen_board.split("[")[0]

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
    """Generates the piece placement part of a FEN string from a board.

    Args:
        board: The board to serialize.

    Returns:
        The FEN piece placement string.
    """
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

def _parse_pocket(pocket_str: str) -> tuple[tuple[Piece, ...], tuple[Piece, ...]]:
    """Parses a Crazyhouse pocket string into piece tuples.

    Args:
        pocket_str: The pocket string (e.g., 'QNp').

    Returns:
        A tuple (white_pocket, black_pocket).
    """
    # content inside []
    white_pocket: list[Piece] = []
    black_pocket: list[Piece] = []

    for char in pocket_str:
        piece_cls = piece_from_char.get(char)
        if piece_cls:
            # Uppercase = White, Lowercase = Black
            if char.isupper():
                white_pocket.append(piece_cls(Color.WHITE))
            else:
                black_pocket.append(piece_cls(Color.BLACK))

    return (tuple(white_pocket), tuple(black_pocket))

def _serialize_pocket(white_pocket: tuple[Piece, ...], black_pocket: tuple[Piece, ...]) -> str:
    """Serializes Crazyhouse pockets to a string.

    Args:
        white_pocket: Pieces in White's pocket.
        black_pocket: Pieces in Black's pocket.

    Returns:
        The FEN-compatible pocket string.
    """
    s = ""
    for p in white_pocket:
        s += p.fen
    for p in black_pocket:
        s += p.fen
    return f"[{s}]" if s else ""

def state_from_fen(fen: str) -> "GameState":
    """Creates a GameState object from a full FEN string.

    Args:
        fen: The full FEN string.

    Returns:
        A GameState (or subclass) instance.

    Raises:
        ValueError: If the FEN string is malformed.
    """
    from v_chess.game_state import GameState, ThreeCheckGameState, CrazyhouseGameState
    from v_chess.board import Board

    # Pre-processing for Variants
    # Check for Three-Check: ends with +N+M
    # We split by space. Standard has 6 fields.
    fen_parts = fen.split()

    three_check_suffix = None
    if len(fen_parts) == 7 and "+" in fen_parts[6]:
        three_check_suffix = fen_parts[6]

    # Check for Crazyhouse: 1st field has []
    crazyhouse_pocket = None
    if "[" in fen_parts[0] and "]" in fen_parts[0]:
        board_part, pocket_part = fen_parts[0].split("[")
        pocket_part = pocket_part.rstrip("]")
        crazyhouse_pocket = _parse_pocket(pocket_part)
        fen_parts[0] = board_part # Clean board part for standard parsing

    if len(fen_parts) < 6:
        raise ValueError("Invalid FEN format: Must contain at least 6 fields.")

    board = Board(fen_parts[0])
    active_color = Color(fen_parts[1])
    castling_rights = CastlingRight.from_fen(fen_parts[2])
    en_passant = None if fen_parts[3] == "-" else Square(fen_parts[3])

    try:
        halfmove_clock = int(fen_parts[4])
        fullmove_count = int(fen_parts[5])
    except ValueError:
        raise ValueError("FEN halfmove and fullmove must be int.")

    # Instantiate specific GameState
    if three_check_suffix:
        # format +w+b e.g. +2+0
        parts = three_check_suffix.split("+")
        # parts[0] is empty string, parts[1] is white, parts[2] is black
        w_checks = int(parts[1])
        b_checks = int(parts[2])
        return ThreeCheckGameState(
            board, active_color, castling_rights, en_passant,
            halfmove_clock, fullmove_count, 1,
            checks=(w_checks, b_checks)
        )
    elif crazyhouse_pocket:
        return CrazyhouseGameState(
            board, active_color, castling_rights, en_passant,
            halfmove_clock, fullmove_count, 1,
            pockets=crazyhouse_pocket
        )
    else:
        return GameState(
            board, active_color, castling_rights, en_passant,
            halfmove_clock, fullmove_count, 1
        )

def state_to_fen(state: "GameState") -> str:
    """Serializes a GameState object to a full FEN string.

    Args:
        state: The GameState to serialize.

    Returns:
        The full FEN string.
    """
    from v_chess.game_state import ThreeCheckGameState, CrazyhouseGameState

    placement = state.board.fen

    # Variant handling for placement (Crazyhouse)
    if isinstance(state, CrazyhouseGameState):
        pocket_str = _serialize_pocket(state.pockets[0], state.pockets[1])
        placement += pocket_str

    active = state.turn.value

    rights_str = "".join([r.value for r in state.castling_rights]) or "-"

    ep = str(state.ep_square) if state.ep_square else "-"
    hm = str(state.halfmove_clock)
    fm = str(state.fullmove_count)

    base_fen = f"{placement} {active} {rights_str} {ep} {hm} {fm}"

    # Variant handling for suffix (Three-Check)
    if isinstance(state, ThreeCheckGameState):
        base_fen += f" +{state.checks[0]}+{state.checks[1]}"

    return base_fen
