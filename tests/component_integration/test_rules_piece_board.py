import pytest
from v_chess.game import Game
from v_chess.move import Move
from v_chess.enums import MoveLegalityReason

def test_sliding_piece_blocked_by_friendly():
    """Verify sliding piece blocked by friendly piece."""
    game = Game("8/8/8/8/8/8/P7/R6k w - - 0 1")
    move = Move("a1a3")
    assert not game.rules.validate_move(move) == MoveLegalityReason.LEGAL

def test_sliding_piece_blocked_by_enemy():
    """Verify sliding piece blocked by enemy piece (can capture, not go through)."""
    game = Game("8/8/8/8/8/8/p7/R6k w - - 0 1")
    
    assert game.rules.is_legal(Move("a1a2"))
    assert not game.rules.is_legal(Move("a1a3"))

def test_knight_jumps_over():
    """Verify Knight jumps over pieces."""
    game = Game()
    move = Move("b1c3") # Jumps over pawn at d2/c2/b2 logic
    assert game.rules.validate_move(move) == MoveLegalityReason.LEGAL

def test_pawn_blocked_by_piece_in_front():
    """Verify pawn is blocked by piece directly in front."""
    game = Game("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")
    move = Move("e4e5")
    assert not game.rules.is_legal(move)

def test_is_check_identifies_attacked_king():
    """Verify is_check correctly identifies attacked king."""
    game = Game("rnbqkbnr/pppp1ppp/8/1B2p3/4P3/8/PPPP1PPP/RNBQK1NR b KQkq - 1 2")
    # Not in check yet
    assert not game.rules.is_check()
    
    # Real check:
    game = Game("rnbqkbnr/pppp1Qpp/8/4p3/4P3/8/PPPP1PPP/RNB1KBNR b KQkq - 0 3")
    assert game.rules.is_check()

def test_king_left_in_check_prevents_move():
    """Verify moving into check is illegal."""
    game = Game("rnbqkbnr/pppp1Qpp/8/4p3/4P3/8/PPPP1PPP/RNB1KBNR b KQkq - 0 3")
    # King at e8 is in check by Q at f7.
    # Trying to move pawn a7a6 is illegal because king stays in check.
    move = Move("a7a6")
    assert not game.rules.is_legal(move)
