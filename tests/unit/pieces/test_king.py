from v_chess.piece.king import King
from v_chess.enums import Color
from v_chess.square import Square

def test_king_theoretical_moves_center():
    king = King(Color.WHITE)
    center = Square("e4")
    moves = set(king.theoretical_moves(center))
    
    expected = {
        Square("e5"), Square("e3"),
        Square("d4"), Square("f4"),
        Square("d5"), Square("f5"),
        Square("d3"), Square("f3")
    }
    assert moves == expected

def test_king_theoretical_moves_corner():
    king = King(Color.WHITE)
    corner = Square("a1")
    moves = set(king.theoretical_moves(corner))
    
    expected = {Square("a2"), Square("b1"), Square("b2")}
    assert moves == expected
