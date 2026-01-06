from v_chess.game import Game
from v_chess.enums import GameOverReason
from v_chess.rules import AntichessRules
from v_chess.move import Move
from dataclasses import replace

def test_termination_checkmate():
    game = Game("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 2")

    assert game.is_checkmate
    assert game.is_over
    assert game.game_over_reason == GameOverReason.CHECKMATE

def test_termination_stalemate():
    fen = "7k/5Q2/8/8/8/8/8/K7 b - - 0 1"
    game = Game(fen)

    assert not game.is_checkmate
    assert game.is_over
    assert not game.is_check
    assert game.game_over_reason == GameOverReason.STALEMATE
    assert game.is_over

def test_fifty_move_rule_standard():
    """Verify 50-move rule triggers a draw in Standard Chess."""
    # Setup a state with halfmove_clock = 99
    # Start pos
    game = Game()
    # Manually set clock
    game.state = replace(game.state, halfmove_clock=99)

    # Make a reversible move (Knight move)
    # 100th halfmove
    game.take_turn(Move("g1f3")) 
    
    assert game.state.halfmove_clock == 100
    assert game.rules.is_fifty_moves(game.state)
    assert game.game_over_reason == GameOverReason.FIFTY_MOVE_RULE
    assert game.is_draw

def test_fifty_move_rule_reset_on_pawn_move():
    """Verify clock resets on pawn move."""
    game = Game()
    game.state = replace(game.state, halfmove_clock=50)
    
    # Pawn move
    game.take_turn(Move("e2e4"))
    
    assert game.state.halfmove_clock == 0
    assert not game.rules.is_fifty_moves(game.state)

def test_fifty_move_rule_reset_on_capture():
    """Verify clock resets on capture."""
    # Setup capture possibility
    # White P e4. Black P d5.
    game = Game("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")
    game.state = replace(game.state, halfmove_clock=50)
    
    # Capture exd5
    game.take_turn(Move("e4d5"))
    
    assert game.state.halfmove_clock == 0
    assert not game.rules.is_fifty_moves(game.state)

def test_fifty_move_rule_antichess():
    """Verify 50-move rule in Antichess."""
    # Antichess often draws if pieces are just moving around
    game = Game(rules=AntichessRules())
    game.state = replace(game.state, halfmove_clock=100)
    
    assert game.rules.is_fifty_moves(game.state)
    assert game.game_over_reason == GameOverReason.FIFTY_MOVE_RULE