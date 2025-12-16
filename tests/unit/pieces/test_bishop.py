from oop_chess.piece.bishop import Bishop
from oop_chess.enums import Color
from oop_chess.square import Square

def test_bishop_theoretical_moves_center():
    bishop = Bishop(Color.WHITE)
    center = Square("e4")
    moves = set(bishop.theoretical_moves(center))
    
    assert Square("f5") in moves
    assert Square("h1") in moves
    assert Square("d3") in moves
    assert Square("a8") in moves
    assert len(moves) == 13

def test_bishop_theoretical_moves_corner():
    bishop = Bishop(Color.WHITE)
    corner = Square("a1")
    moves = set(bishop.theoretical_moves(corner))
    
    assert Square("b2") in moves
    assert Square("h8") in moves
    assert len(moves) == 7
