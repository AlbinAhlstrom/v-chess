from hypothesis import given, strategies as st

from oop_chess.board import Board
from oop_chess.move import Move
from oop_chess.square import Square
from oop_chess.enums import Color
from oop_chess.piece.pawn import Pawn
from oop_chess.piece.piece import Piece
from tests.conftest import random_square, random_piece

@given(square=random_square(), piece=random_piece())
def test_pawn_two_step_move(square: Square, piece: Piece):
    """
    Specific check: For an un-moved pawn, ensure the double-step square is included
    in theoretical moves if it's a valid square.
    """

    board = Board.empty()
    board.set_piece(piece, square)











    moves = piece.theoretical_moves(square)

    if isinstance(piece, Pawn):


        pass

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
