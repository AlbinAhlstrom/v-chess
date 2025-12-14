from hypothesis import given, strategies as st

from oop_chess.board import Board
from oop_chess.square import Square
from oop_chess.piece.piece import Piece
from oop_chess.piece.king import King
from oop_chess.piece.queen import Queen
from oop_chess.piece.rook import Rook
from oop_chess.piece.bishop import Bishop
from oop_chess.piece.knight import Knight
from oop_chess.piece.pawn import Pawn
from tests.conftest import random_square, random_piece


def empty_board_with_piece(square, piece):
    board = Board.empty()
    board.set_piece(piece, square)
    return board

@given(square=random_square(), piece=random_piece())
def test_pawn_capture(square: Square, piece: Piece):
    if not isinstance(piece, Pawn):
        return

    moves = piece.capture_squares(square)
    for move in moves:
        assert move.col != square.col

@given(square=random_square(), piece=random_piece())
def test_theoretical_moves_count_king(square: Square, piece: Piece):
    if not isinstance(piece, King):
        return
    moves = piece.theoretical_moves(square)
    assert len(moves) <= 8

@given(square=random_square(), piece=random_piece())
def test_theoretical_moves_count_knight(square: Square, piece: Piece):
    if not isinstance(piece, Knight):
        return
    moves = piece.theoretical_moves(square)
    assert len(moves) <= 8

@given(square=random_square(), piece=random_piece())
def test_theoretical_moves_count_rook(square: Square, piece: Piece):
    if not isinstance(piece, Rook):
        return
    moves = piece.theoretical_moves(square)
    assert len(moves) <= 14

@given(square=random_square(), piece=random_piece())
def test_theoretical_moves_count_bishop(square: Square, piece: Piece):
    if not isinstance(piece, Bishop):
        return
    moves = piece.theoretical_moves(square)
    assert len(moves) <= 13

@given(square=random_square(), piece=random_piece())
def test_theoretical_moves_count_queen(square: Square, piece: Piece):
    if not isinstance(piece, Queen):
        return
    moves = piece.theoretical_moves(square)
    assert len(moves) <= 27

@given(square=random_square(), piece=random_piece())
def test_theoretical_moves_are_valid(square: Square, piece: Piece):
    moves = piece.theoretical_moves(square)
    for move in moves:
        assert Square.is_valid(move.row, move.col)

@given(square=random_square(), piece=random_piece())
def test_theoretical_moves_count_limits(square: Square, piece: Piece):
    moves = piece.theoretical_moves(square)
    assert len(moves) > 0 or (square.row == 0 and piece.color == "w" and isinstance(piece, Pawn)) or (square.row == 7 and piece.color == "b" and isinstance(piece, Pawn))