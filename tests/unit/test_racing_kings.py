from v_chess.game import Game
from v_chess.move import Move
from v_chess.rules import RacingKingsRules
from v_chess.enums import Color, GameOverReason, MoveLegalityReason
from v_chess.piece import Queen, Pawn, Knight, King

def test_rk_win_white():
    """Verify White wins if King reaches 8th and Black fails to follow."""
    # White King on a7 (row 1), just about to move to a8.
    # Black King on h1.
    fen = "8/K7/8/8/8/8/8/7k w - - 0 1"
    game = Game(fen, rules=RacingKingsRules())
    
    # 1. Ka8
    game.take_turn(Move("a7a8"))
    
    assert not game.is_over # Black still has a turn
    
    # Black moves King from h1 to h2
    game.take_turn(Move("h1h2"))
    
    assert game.is_over
    assert game.game_over_reason == GameOverReason.KING_TO_EIGHTH_RANK
    assert game.winner == "w"

def test_rk_draw_both_reach():
    """Verify draw if both reach 8th rank."""
    # White moves to 8th, then Black moves to 8th.
    fen = "8/K6k/8/8/8/8/8/8 w - - 0 1"
    game = Game(fen, rules=RacingKingsRules())
    
    # 1. Ka8
    game.take_turn(Move("a7a8"))
    
    # 1... Kh8
    game.take_turn(Move("h7h8"))
    
    assert game.is_over
    assert game.game_over_reason == GameOverReason.STALEMATE # Or Draw
    assert game.winner is None

def test_rk_illegal_check():
    """Verify moves giving check are illegal."""
    # White Rook on a1, Black King on h1.
    # 1. Ra1-h1 is illegal? No, that's capture.
    # 1. Ra1-a8? No check.
    # Put White Rook on h2. Black King on h1.
    # Rook moves to h2 is check.
    fen = "k7/8/8/8/8/8/R7/7K b - - 0 1"
    # Black King on h1. White Rook on a2. 
    # If Black moves King to h1 (oops, it's already there).
    # Setup: Black King on g1. White Rook on a2.
    # Black moves King to h1? 
    # White Rook at a2 attacks a1-h1? No.
    # Let's put White Rook on h2.
    fen = "k7/8/8/8/8/8/7R/6K1 b - - 0 1"
    # Black King on g1. Rook at h2.
    # If Black moves to h1, it's check.
    game = Game(fen, rules=RacingKingsRules())
    
    # Kh1 is illegal
    assert game.rules.validate_move(game.state, Move("g1h1")) != MoveLegalityReason.LEGAL
