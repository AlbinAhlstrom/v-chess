import pytest
from v_chess.game import Game
from v_chess.move import Move

def test_fen_save_load_cycle():
    game = Game()
    moves = ["e2e4", "e7e5", "g1f3", "b8c6"]
    
    for m in moves:
        game.take_turn(Move(m))
        
    saved_fen = game.state.fen
    
    new_game = Game(saved_fen)
    
    assert new_game.state.fen == saved_fen
    assert new_game.state.turn == game.state.turn
    assert set([m.uci for m in new_game.legal_moves]) == set([m.uci for m in game.legal_moves])

def test_undo_redo_stability():
    game = Game()
    moves = ["e2e4", "e7e5", "g1f3"]
    
    for m in moves:
        game.take_turn(Move(m))
        
    current_fen = game.state.fen
    
    game.undo_move()
    game.undo_move()
    
    game.take_turn(Move("e7e5"))
    game.take_turn(Move("g1f3"))
    
    assert game.state.fen == current_fen
