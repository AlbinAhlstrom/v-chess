from hypothesis import given

from oop_chess.enums import Color
from oop_chess.piece.bishop import Bishop
from oop_chess.piece.king import King
from oop_chess.piece.knight import Knight
from oop_chess.piece.pawn import Pawn
from oop_chess.piece.piece import Piece
from oop_chess.board import Board
from oop_chess.piece.queen import Queen
from oop_chess.piece.rook import Rook
from oop_chess.square import Square
from conftest import random_square, random_piece


def _dist_from_center(index: int) -> int:
    """Maps 0-7 index to 0-3 index for symmetrical board lookups."""
    return min(index, 7 - index)


_KNIGHT_MOVES_MAP = [
    # Col 0 1 2 3
    [2, 3, 4, 4], # Row 0
    [3, 4, 6, 6], # Row 1
    [4, 6, 8, 8], # Row 2
    [4, 6, 8, 8]  # Row 3
]

def empty_board_with_piece(square, piece):
    board = Board.empty()
    board.set_piece(piece, square)
    return board


@given(square=random_square(), piece=random_piece())
def test_pawn_capture(square: Square, piece: Piece):
    board = Board.empty()
    board.set_piece(piece, square)


@given(square=random_square(), piece=random_piece())
def test_theoretical_moves_count_king(square: Square, piece: Piece):
    """Verifies the exact theoretical move count for a King based on its position."""
    empty_board_with_piece(square, piece)

    if piece.__class__ is not King:
        return
    piece.has_moved = True

    row_idx = square.row
    col_idx = square.col

    is_on_edge = 0
    if row_idx == 0 or row_idx == 7: is_on_edge += 1
    if col_idx == 0 or col_idx == 7: is_on_edge += 1

    if is_on_edge == 2:
        expected_moves = 3
    elif is_on_edge == 1:
        expected_moves = 5
    else:
        expected_moves = 8

    moves_count = len(piece.theoretical_moves)
    assert moves_count == expected_moves, (
        f"King at {square} calculated {moves_count}, expected {expected_moves}."
    )


@given(square=random_square(), piece=random_piece())
def test_theoretical_moves_count_knight(square: Square, piece: Piece):
    empty_board_with_piece(square, piece)

    if piece.__class__ is not Knight:
        return

    row_key = _dist_from_center(square.row)
    col_key = _dist_from_center(square.col)

    expected_moves = _KNIGHT_MOVES_MAP[row_key][col_key]

    moves_count = len(piece.theoretical_moves)
    assert moves_count == expected_moves, (
        f"Knight at {square} calculated {moves_count}, expected {expected_moves}."
    )


@given(square=random_square(), piece=random_piece())
def test_theoretical_moves_count_rook(square: Square, piece: Piece):
    empty_board_with_piece(square, piece)

    if piece.__class__ is not Rook:
        return

    expected_moves = 14

    moves_count = len(piece.theoretical_moves)
    assert moves_count == expected_moves, (
        f"Rook at {square} calculated {moves_count}, expected {expected_moves}."
    )


@given(square=random_square(), piece=random_piece())
def test_theoretical_moves_count_bishop(square: Square, piece: Piece):
    empty_board_with_piece(square, piece)

    if piece.__class__ is not Bishop:
        return

    row_idx = square.row
    col_idx = square.col

    diag1_moves = min(row_idx, col_idx) + min(7 - row_idx, 7 - col_idx)
    diag2_moves = min(row_idx, 7 - col_idx) + min(7 - row_idx, col_idx)

    expected_moves = diag1_moves + diag2_moves

    moves_count = len(piece.theoretical_moves)
    assert moves_count == expected_moves, (
        f"Bishop at {square} calculated {moves_count}, expected {expected_moves}."
    )


@given(square=random_square(), piece=random_piece())
def test_theoretical_moves_count_queen(square: Square, piece: Piece):
    empty_board_with_piece(square, piece)

    if piece.__class__ is not Queen:
        return

    row_idx = square.row
    col_idx = square.col

    rook_moves = 14

    diag1_moves = min(row_idx, col_idx) + min(7 - row_idx, 7 - col_idx)
    diag2_moves = min(row_idx, 7 - col_idx) + min(7 - row_idx, col_idx)
    bishop_moves = diag1_moves + diag2_moves

    expected_moves = rook_moves + bishop_moves

    moves_count = len(piece.theoretical_moves)
    assert moves_count == expected_moves, (
        f"Queen at {square} calculated {moves_count}, expected {expected_moves}."
    )


@given(square=random_square(), piece=random_piece())
def test_theoretical_moves_are_valid(square: Square, piece: Piece):
    empty_board_with_piece(square, piece)

    assert piece is not None
    assert piece.square is not None

    theoretical_moves = piece.theoretical_moves
    assert len(theoretical_moves) == len(set(theoretical_moves))

    for end_square in theoretical_moves:
        assert isinstance(end_square, Square)
        assert 0 <= end_square.row < 8
        assert 0 <= end_square.col < 8


@given(square=random_square(), piece=random_piece())
def test_theoretical_moves_count_limits(square: Square, piece: Piece):
    empty_board_with_piece(square, piece)

    assert piece is not None
    piece.square = square

    moves_count = len(piece.theoretical_moves)
    piece_type = piece.__class__

    if issubclass(piece_type, (King, Knight)):
        # Castling included
        assert moves_count <= 10
    elif issubclass(piece_type, (Rook, Bishop)):
        assert moves_count <= 14
    elif piece_type is Queen:
        assert moves_count <= 27
    elif piece_type is Pawn:
        assert moves_count <= 4


