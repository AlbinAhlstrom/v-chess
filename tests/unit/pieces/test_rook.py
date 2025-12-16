from oop_chess.piece.rook import Rook
from oop_chess.enums import Color
from oop_chess.square import Square

def test_rook_theoretical_moves_center():
    rook = Rook(Color.WHITE)
    center = Square("e4")
    moves = set(rook.theoretical_moves(center))
    
    assert Square("e5") in moves
    assert Square("e8") in moves
    assert Square("e1") in moves
    assert Square("h4") in moves
    assert Square("a4") in moves
    assert len(moves) == 14

def test_rook_theoretical_moves_corner():
    rook = Rook(Color.WHITE)
    corner = Square("a1")
    moves = set(rook.theoretical_moves(corner))
    
    assert Square("a8") in moves
    assert Square("h1") in moves
    assert len(moves) == 14
