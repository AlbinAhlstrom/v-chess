import pytest

from chess.square import Square
from chess.piece.rook import Rook
from chess.piece.knight import Knight
from chess.piece.bishop import Bishop
from chess.piece.queen import Queen
from chess.piece.king import King
from chess.piece.pawn import Pawn
from chess.piece.color import Color


def test_rook_moves_and_value():
    rook = Rook(Color.WHITE, Square(4, 4))
    assert rook.color == Color.WHITE
    moves = rook.moves()
    assert len(moves) == 14
    assert rook.value == 5


def test_bishop_moves_and_value():
    bishop = Bishop(Color.BLACK, Square(4, 4))
    assert bishop.color == Color.BLACK
    moves = bishop.moves()
    assert len(moves) == 13
    assert bishop.value == 3


def test_queen_moves_and_value():
    queen = Queen(Color.WHITE, Square(4, 4))
    assert queen.color == Color.WHITE
    moves = queen.moves()
    assert len(moves) == 27
    assert queen.value == 9


def test_knight_moves_and_value():
    knight = Knight(Color.BLACK, Square(4, 4))
    assert knight.color == Color.BLACK
    moves = knight.moves()
    assert len(moves) == 8
    assert knight.value == 3


def test_king_moves_and_value():
    king = King(Color.WHITE, Square(4, 4))
    assert king.color == Color.WHITE
    moves = king.moves()
    assert len(moves) == 8
    assert king.value == float("inf")


def test_pawn_moves_first_and_after_moving():
    pawn = Pawn(Color.WHITE, Square(6, 4))
    assert pawn.has_moved == False
    assert pawn.color == Color.WHITE
    moves = pawn.moves()
    assert Square(5, 4) in moves
    assert Square(4, 4) in moves

    pawn.has_moved = True
    moves = pawn.moves()
    assert len(moves) == 1
    assert Square(5, 4) in moves
    assert pawn.value == 1
