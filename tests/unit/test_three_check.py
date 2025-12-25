from v_chess.game import Game
from v_chess.move import Move
from v_chess.rules import ThreeCheckRules
from v_chess.enums import GameOverReason, Color
from v_chess.game_state import ThreeCheckGameState

def test_three_check_increment():
    """Verify checks are counted."""
    # Start pos with correct FEN suffix
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 +0+0"
    game = Game(fen, rules=ThreeCheckRules())
    assert isinstance(game.state, ThreeCheckGameState)
    assert game.state.checks == (0, 0)
    
    # 1. e4 e5 2. Qh5 Nc6 3. Qxf7+ (Check 1 for White)
    game.take_turn(Move("e2e4"))
    game.take_turn(Move("e7e5"))
    game.take_turn(Move("d1h5"))
    game.take_turn(Move("b8c6"))
    game.take_turn(Move("h5f7")) # Check!
    
    assert isinstance(game.state, ThreeCheckGameState)
    assert game.state.checks == (1, 0)
    
def test_three_check_win():
    """Verify winning by 3 checks."""
    # Setup a position where White can give multiple checks easily.
    # White Rook a1, White Rook b1. Black King h8.
    # 1. Ra8+ Kh7 2. Rh8+ (sac) Kxh8 3. Rb8+ (3rd check)
    
    fen = "7k/8/8/8/8/8/8/RR5K w - - 0 1 +0+0"
    game = Game(fen, rules=ThreeCheckRules())
    
    # Check 1
    game.take_turn(Move("a1a8"))
    assert game.state.checks == (1, 0)
    assert not game.is_over
    
    # Black moves King
    game.take_turn(Move("h8h7"))
    
    # Check 2
    game.take_turn(Move("a8h8"))
    assert game.state.checks == (2, 0)
    
    # Black takes Rook
    game.take_turn(Move("h7h8"))
    
    # Check 3
    game.take_turn(Move("b1b8"))
    
    assert game.state.checks == (3, 0)
    assert game.is_over
    assert game.game_over_reason == GameOverReason.THREE_CHECKS
    assert game.winner == "w"

def test_three_check_mate_priority():
    """Test that checkmate counts as win even if checks < 3."""
    # Fool's mate
    fen = "rnbqkbnr/pppppppp/8/8/8/5P2/PPPPP1PP/RNBQKBNR b KQkq - 0 1 +0+0"
    game = Game(fen, rules=ThreeCheckRules())
    
    game.take_turn(Move("e7e5"))
    game.take_turn(Move("g2g4"))
    game.take_turn(Move("d8h4")) # Checkmate (and Check #1 for Black)
    
    assert game.is_over
    assert game.game_over_reason == GameOverReason.CHECKMATE
    assert game.winner == "b"
    assert game.state.checks == (0, 1)

def test_fen_persistence():
    """Verify FEN correctly loads/saves check counts."""
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 +2+1"
    game = Game(fen, rules=ThreeCheckRules())
    
    assert game.state.checks == (2, 1)
    assert "+2+1" in game.state.fen