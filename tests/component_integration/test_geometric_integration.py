import pytest
from v_chess.board import Board
from v_chess.square import Square
from v_chess.piece.pawn import Pawn
from v_chess.piece.bishop import Bishop
from v_chess.enums import Color

def test_coordinate_alignment():
    """Verify Piece move patterns map correctly to Board coordinates."""
    board = Board.empty()
    pawn = Pawn(Color.WHITE)
    # Rank 2 in algebraic is row 6 in 0-indexed board (0=rank 8)
    sq = Square("e2")
    assert sq.row == 6
    assert sq.col == 4
    
    board.set_piece(pawn, sq)
    assert board.get_piece(Square(6, 4)) == pawn

def test_boundary_conditions():
    """Verify moves near board edges are handled."""
    board = Board.empty()
    bishop = Bishop(Color.WHITE)
    # a1 is row 7, col 0
    sq = Square("a1")
    board.set_piece(bishop, sq)
    
    moves = bishop.theoretical_moves(sq)
    # Should not contain squares with col < 0 or > 7 or row < 0 or > 7
    for m in moves:
        assert 0 <= m.row <= 7
        assert 0 <= m.col <= 7
