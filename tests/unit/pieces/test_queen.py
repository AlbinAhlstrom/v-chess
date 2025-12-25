from v_chess.piece.queen import Queen
from v_chess.enums import Color
from v_chess.square import Square

def test_queen_theoretical_moves_center():
    queen = Queen(Color.WHITE)
    center = Square("e4")
    moves = set(queen.theoretical_moves(center))
    
    assert Square("e8") in moves
    assert Square("h4") in moves
    assert Square("h7") in moves
    assert Square("b1") in moves
    assert len(moves) == 27

def test_queen_theoretical_moves_corner():
    queen = Queen(Color.WHITE)
    corner = Square("a1")
    moves = set(queen.theoretical_moves(corner))
    
    assert len(moves) == 21
