import pytest

from chess.board import Coordinate, Color
from chess.pieces import Rook, Bishop, Queen, Knight, King, Pawn


def test_rook_moves_and_value():
    rook = Rook(Color.WHITE, Coordinate(4, 4))
    moves = rook.moves()
    assert len(moves) == 14
    assert rook.value == 5


def test_bishop_moves_and_value():
    bishop = Bishop(Color.BLACK, Coordinate(4, 4))
    moves = bishop.moves()
    assert len(moves) == 13
    assert bishop.value == 3


def test_queen_moves_and_value():
    queen = Queen(Color.WHITE, Coordinate(4, 4))
    moves = queen.moves()
    assert len(moves) == 27
    assert queen.value == 9


def test_knight_moves_and_value():
    knight = Knight(Color.BLACK, Coordinate(4, 4))
    moves = knight.moves()
    assert len(moves) == 8
    assert knight.value == 3


def test_king_moves_and_value():
    king = King(Color.WHITE, Coordinate(4, 4))
    moves = king.moves()
    assert len(moves) == 8
    assert king.value == float("inf")


def test_pawn_moves_first_and_after_moving():
    pawn = Pawn(Color.WHITE, Coordinate(6, 4))
    assert pawn.has_moved == False
    moves = pawn.moves()
    assert len(moves) == 2
    assert Coordinate(5, 4) in moves
    assert Coordinate(4, 4) in moves

    pawn.has_moved = True
    moves = pawn.moves()
    assert len(moves) == 1
    assert Coordinate(5, 4) in moves
    assert pawn.value == 1
