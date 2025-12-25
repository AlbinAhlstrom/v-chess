from hypothesis import given

from v_chess.board import Board
from v_chess.square import Square
from v_chess.piece.pawn import Pawn
from v_chess.piece.piece import Piece
from tests.conftest import random_square, random_piece


@given(square=random_square(), piece=random_piece())
def test_pawn_capture(square: Square, piece: Piece):
    board = Board.empty()
    board.set_piece(piece, square)


    captures = piece.capture_squares(square)
    if isinstance(piece, Pawn):
        for cap in captures:
            assert cap.col != square.col

@given(square=random_square(), piece=random_piece())
def test_theoretical_moves_count_pawn(square: Square, piece: Piece):
    board = Board.empty()
    board.set_piece(piece, square)

    moves = piece.theoretical_moves(square)

    assert isinstance(moves, list)
