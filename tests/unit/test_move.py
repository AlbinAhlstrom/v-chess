import pytest
from oop_chess.move import Move
from oop_chess.square import Square
from oop_chess.enums import Color
from oop_chess.piece.queen import Queen

def test_move_uci_parsing_normal():
    move = Move("e2e4")
    assert move.start == Square("e2")
    assert move.end == Square("e4")
    assert move.promotion_piece is None

def test_move_uci_parsing_promotion():
    move = Move("a7a8q", player_to_move=Color.WHITE)
    assert move.start == Square("a7")
    assert move.end == Square("a8")
    assert isinstance(move.promotion_piece, Queen)
    assert move.promotion_piece.color == Color.WHITE

def test_move_uci_invalid_length():
    with pytest.raises(ValueError, match="Invalid UCI string"):
        Move("e2e44")

def test_move_uci_invalid_coords():
    with pytest.raises(ValueError):
        Move("z2e4")

def test_move_properties_vertical():
    move = Move("e2e4")
    assert move.is_vertical
    assert not move.is_horizontal
    assert not move.is_diagonal

def test_move_properties_horizontal():
    move = Move("a1h1")
    assert not move.is_vertical
    assert move.is_horizontal
    assert not move.is_diagonal

def test_move_properties_diagonal():
    move = Move("a1h8")
    assert not move.is_vertical
    assert not move.is_horizontal
    assert move.is_diagonal

def test_move_equality():
    m1 = Move("e2e4")
    m2 = Move("e2e4")
    m3 = Move("d2d4")
    
    assert m1 == m2
    assert m1 != m3
