import pytest
from oop_chess.rules import AntichessRules
from oop_chess.game_state import GameState
from oop_chess.move import Move
from oop_chess.square import Square
from oop_chess.enums import Color, MoveLegalityReason

def test_mandatory_capture_simple():
    rules = AntichessRules()
    # White R at a1, Black P at a2. Capture available.
    fen = "8/8/8/8/8/8/p7/R7 w - - 0 1"
    state = GameState.from_fen(fen)
    
    # Capture is legal
    assert rules.is_move_legal(state, Move("a1a2"))
    
    # Non-capture (horizontal) is illegal
    assert not rules.is_move_legal(state, Move("a1b1"))
    
    # Reason check
    assert rules.move_legality_reason(state, Move("a1b1")) == MoveLegalityReason.MANDATORY_CAPTURE

def test_mandatory_capture_multiple_options():
    rules = AntichessRules()
    # White R a1. Black P a2, P b1.
    # a1xa2 and a1xb1 are captures. a1c1 is non-capture.
    fen = "8/8/8/8/8/8/p7/Rn6 w - - 0 1"
    state = GameState.from_fen(fen)
    
    assert rules.is_move_legal(state, Move("a1a2"))
    assert rules.is_move_legal(state, Move("a1b1"))
    assert not rules.is_move_legal(state, Move("a1c1"))

def test_no_capture_allows_any_move():
    rules = AntichessRules()
    # Start pos. No captures.
    state = GameState.starting_setup()
    
    assert rules.is_move_legal(state, Move("e2e3"))
    assert rules.is_move_legal(state, Move("g1f3"))

def test_en_passant_is_mandatory():
    rules = AntichessRules()
    # White P e5. Black P d5 (just moved d7-d5). EP d6.
    # e5xd6 is capture. e5-e6 is push (non-capture).
    fen = "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1"
    state = GameState.from_fen(fen)
    
    assert rules.is_move_legal(state, Move("e5d6"))
    # Can pawn move e5-e6? No, blocked? No, e6 is empty.
    # But capture is mandatory.
    assert not rules.is_move_legal(state, Move("e5e6"))

def test_king_mechanics_check_ignored():
    rules = AntichessRules()
    # King in check.
    fen = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 2"
    state = GameState.from_fen(fen)
    
    assert not rules.is_check(state)
    assert not rules.is_checkmate(state)
    
    # King can move to attacked square?
    # White K e1. Q h4 attacks f2.
    # e1-f2?
    # K e1. f2 is empty.
    # In standard, illegal. In Antichess, legal (unless capture mandatory elsewhere).
    # Here, can White capture Q? No.
    # So King move should be legal.
    assert rules.is_move_legal(state, Move("e1f2"))

def test_castling_illegal():
    rules = AntichessRules()
    # Setup where castling would be legal in standard.
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQK2R w KQkq - 0 1"
    state = GameState.from_fen(fen)
    
    # Castling e1g1
    assert not rules.is_move_legal(state, Move("e1g1"))
    assert rules.move_legality_reason(state, Move("e1g1")) == MoveLegalityReason.CASTLING_DISABLED

def test_termination_zero_pieces():
    rules = AntichessRules()
    # White has no pieces.
    fen = "8/8/8/8/8/8/8/k7 w - - 0 1"
    state = GameState.from_fen(fen)
    
    assert rules.is_game_over(state)
    # White wins (by losing everything).
    
def test_termination_stalemate():
    rules = AntichessRules()
    # White has pieces but no moves.
    # White P a2. Black P a3. Blocked.
    # White K at h1 trapped by Black R g1, g2?
    # Simpler: White P a2. Black P a3. No other white pieces?
    # If White has ONLY blocked pawn, it's stalemate.
    fen = "8/8/8/8/8/p7/P7/k7 w - - 0 1"
    state = GameState.from_fen(fen)
    
    legal_moves = rules.get_legal_moves(state)
    assert not legal_moves
    assert rules.is_game_over(state)
