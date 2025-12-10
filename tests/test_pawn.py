from hypothesis import given

from oop_chess.board import Board
from oop_chess.square import Square
from oop_chess.piece import Piece
from oop_chess.piece.pawn import Pawn
from oop_chess.enums import Color
from conftest import random_square, random_piece
from test_theoretical_moves import empty_board_with_piece


@given(square=random_square(), piece=random_piece())
def test_pawn_two_step_move(square: Square, piece: Piece):
    """
    Specific check: For an un-moved pawn, ensure the double-step square is included
    in theoretical moves if it's a valid square.
    """
    board = Board.empty()
    board.set_piece(piece, square)
    if not isinstance(piece, Pawn):
        return

    piece.has_moved = False
    start_square = piece.square
    assert start_square is not None

    single_step = start_square.get_step(piece.direction)
    double_step = single_step.get_step(piece.direction) if single_step else None

    theoretical_moves = piece.theoretical_moves

    if double_step:
        assert double_step in theoretical_moves

@given(square=random_square(), piece=random_piece())
def test_pawn_capture(square: Square, piece: Piece):
    board = Board.empty()
    board.set_piece(piece, square)

    assert piece.square is not None

    if not isinstance(piece, Pawn):
        return

    starting_row = 1 if piece.color == Color.BLACK else 6
    last_row = 0 if piece.color == Color.WHITE else 7
    is_on_last_row = square.row == last_row
    is_on_edge = square.col in (0, 7)

    if is_on_last_row:
        return

    if square.row == starting_row - piece.direction.value[1]:
        return

    expected_captures= 2
    if is_on_edge:
        expected_captures = 1

    assert len(piece.capture_squares) == expected_captures, f"{expected_captures=} got {piece.capture_squares} for {piece.color} pawn at {square}"



@given(square=random_square(), piece=random_piece())
def test_theoretical_moves_count_pawn(square: Square, piece: Piece):
    empty_board_with_piece(square, piece)

    starting_row = 1 if piece.color == Color.BLACK else 6
    last_row = 0 if piece.color == Color.WHITE else 7
    is_on_edge = square.col in (0, 7)

    is_on_last_row = square.row == last_row
    if is_on_last_row:
        return

    piece.has_moved = not square.row == starting_row
    if not isinstance(piece, Pawn):
        return

    if square.row == starting_row - piece.direction.value[1]:
        return
    expected_moves = 3 if piece.has_moved else 4
    if is_on_edge:
        expected_moves -= 1

    moves_count = len(piece.theoretical_moves)
    assert moves_count == expected_moves, (
        f"{piece.color} pawn at {square} calculated {moves_count}, expected {expected_moves}."
    )


