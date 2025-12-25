import pytest
import random
from v_chess.game import Game
from v_chess.move import Move

def test_fools_mate():
    """Verify the fastest possible checkmate (2 moves)."""
    game = Game()
    moves = ["f2f3", "e7e5", "g2g4", "d8h4"]
    for m in moves:
        game.take_turn(Move(m))
    
    assert game.is_over
    assert game.is_checkmate

def test_scholars_mate():
    """Verify a common 4-move checkmate."""
    game = Game()
    moves = ["e2e4", "e7e5", "d1h5", "b8c6", "f1c4", "g8f6", "h5f7"]
    for m in moves:
        game.take_turn(Move(m))
        
    assert game.is_over
    assert game.is_checkmate

def test_opera_game():
    """Replay Morphy vs. Duke/Count (1858)."""
    game = Game()
    san_moves = [
        "e4", "e5", "Nf3", "d6", "d4", "Bg4", "dxe5", "Bxf3", "Qxf3", "dxe5",
        "Bc4", "Nf6", "Qb3", "Qe7", "Nc3", "c6", "Bg5", "b5", "Nxb5", "cxb5",
        "Bxb5+", "Nbd7", "O-O-O", "Rd8", "Rxd7", "Rxd7", "Rd1", "Qe6",
        "Bxd7+", "Nxd7", "Qb8+", "Nxb8", "Rd8#"
    ]
    
    for san in san_moves:
        move = Move.from_san(san, game)
        game.take_turn(move)
        
    assert game.is_checkmate

def test_random_legal_game():
    """Play a game with random legal moves for 50 turns to ensure stability."""
    game = Game()
    for _ in range(100):
        if game.is_over:
            break
        legal = game.legal_moves
        if not legal:
            break
        move = random.choice(legal)
        game.take_turn(move)
    
    assert True
