import pytest
from v_chess.game import Game
from v_chess.rules import AntichessRules
from v_chess.move import Move

def test_full_game_short():
    """Simulate a short antichess game."""
    # 1. e3 (open lines) ...
    game = Game(rules=AntichessRules())
    
    # 1. e3
    game.take_turn(Move("e2e3"))
    # Black: b6 (bad move in standard, good here?)
    game.take_turn(Move("b7b6"))
    # White: Ba6 (offer bishop)
    game.take_turn(Move("f1a6"))
    # Black: Must capture? No, optional?
    # B a6. N b8. P b6.
    # N xa6 is valid.
    game.take_turn(Move("b8a6"))
    
    assert not game.is_over

def test_win_by_loss():
    """Setup board with 1 White piece. Move it to be captured."""
    # White R a1. Black R a8.
    fen = "r7/8/8/8/8/8/8/R7 w - - 0 1"
    game = Game(fen, rules=AntichessRules())
    
    # White captures a8 (Mandatory).
    game.take_turn(Move("a1a8"))
    
    # Now White has R at a8. Black has nothing.
    # Black wins? Yes, Black has 0 pieces.
    assert game.is_over
    # Winner logic isn't explicit in Game yet, but is_over is True.

def test_win_by_stalemate():
    """Setup board where White is blocked but has pieces."""
    fen = "8/8/8/8/8/p7/P7/k7 w - - 0 1"
    game = Game(fen, rules=AntichessRules())
    
    assert game.is_over
    # White wins (stalemate = win).
