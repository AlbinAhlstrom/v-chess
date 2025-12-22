from oop_chess.game import Game
from oop_chess.move import Move
from oop_chess.rules import KingOfTheHillRules
from oop_chess.enums import GameOverReason

def test_koth_win_center():
    """Test that moving the king to the center wins the game."""
    # White King on e3, just about to move to e4.
    fen = "8/8/8/8/8/4K3/8/k7 w - - 0 1"
    game = Game(fen, rules=KingOfTheHillRules())
    
    assert not game.is_over
    
    # Move King to e4 (Center)
    game.take_turn(Move("e3e4"))
    
    assert game.is_over
    assert game.game_over_reason == GameOverReason.KING_ON_HILL
    assert game.winner == "w"

def test_koth_checkmate_still_works():
    """Test that standard checkmate still ends the game."""
    # Fool's Mate pattern
    fen = "rnbqkbnr/pppppppp/8/8/8/5P2/PPPPP1PP/RNBQKBNR b KQkq - 0 1"
    game = Game(fen, rules=KingOfTheHillRules())
    
    # 1... e5 2. g4 Qh4#
    game.take_turn(Move("e7e5"))
    game.take_turn(Move("g2g4"))
    game.take_turn(Move("d8h4"))
    
    assert game.is_over
    assert game.game_over_reason == GameOverReason.CHECKMATE
    assert game.winner == "b"

def test_koth_stalemate():
    """Test that stalemate is still a draw."""
    # Stalemate position
    fen = "k7/8/8/8/8/8/5Q2/K7 w - - 0 1" 
    # Not actually stalemate yet, let's setup direct stalemate
    # White King a1, White Queen c2. Black King a3.
    # W: Ka1, Qc2. B: Ka3.
    # If it is Black's turn? No moves?
    # Actually: 7k/8/8/8/8/8/7p/7K w - - 0 1 (White to move, can't move)
    fen = "7k/8/8/8/8/8/7p/7K w - - 0 1"
    game = Game(fen, rules=KingOfTheHillRules())
    
    assert game.is_over
    assert game.game_over_reason == GameOverReason.STALEMATE
    assert game.winner is None

def test_koth_king_d4():
    fen = "8/8/8/8/8/3K4/8/k7 w - - 0 1"
    game = Game(fen, rules=KingOfTheHillRules())
    game.take_turn(Move("d3d4"))
    assert game.is_over
    assert game.game_over_reason == GameOverReason.KING_ON_HILL

def test_koth_king_d5():
    fen = "8/8/8/8/3K4/8/8/k7 w - - 0 1"
    game = Game(fen, rules=KingOfTheHillRules())
    game.take_turn(Move("d4d5"))
    assert game.is_over
    assert game.game_over_reason == GameOverReason.KING_ON_HILL

def test_koth_king_e5():
    fen = "8/8/8/8/4K3/8/8/k7 w - - 0 1"
    game = Game(fen, rules=KingOfTheHillRules())
    game.take_turn(Move("e4e5"))
    assert game.is_over
    assert game.game_over_reason == GameOverReason.KING_ON_HILL
