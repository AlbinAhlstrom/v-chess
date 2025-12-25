from v_chess.piece.knight import Knight
from v_chess.enums import Color
from v_chess.square import Square

def test_knight_theoretical_moves_center():
    knight = Knight(Color.WHITE)
    center = Square("e4")
    moves = set(knight.theoretical_moves(center))
    
    expected = {
        Square("d6"), Square("f6"),
        Square("c5"), Square("g5"),
        Square("c3"), Square("g3"),
        Square("d2"), Square("f2")
    }
    assert moves == expected

def test_knight_theoretical_moves_corner():
    knight = Knight(Color.WHITE)
    corner = Square("a1")
    moves = set(knight.theoretical_moves(corner))
    
    expected = {Square("b3"), Square("c2")}
    assert moves == expected
