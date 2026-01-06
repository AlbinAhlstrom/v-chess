from v_chess.rules import AntichessRules
from v_chess.game_state import GameState
from v_chess.move import Move
from v_chess.enums import MoveLegalityReason, GameOverReason

def test_mandatory_capture_simple():
    # White R at a1, Black P at a2. Capture available.
    fen = "8/8/8/8/8/8/p7/R7 w - - 0 1"
    state = GameState.from_fen(fen)
    rules = AntichessRules()
    
    # Capture is legal
    assert rules.is_legal(state, Move("a1a2"))
    
    # Non-capture (horizontal) is illegal
    assert not rules.is_legal(state, Move("a1b1"))
    
    # Reason check
    assert rules.validate_move(state, Move("a1b1")) == MoveLegalityReason.MANDATORY_CAPTURE

def test_mandatory_capture_multiple_options():
    # White R a1. Black P a2, P b1.
    # a1xa2 and a1xb1 are captures. a1c1 is non-capture.
    fen = "8/8/8/8/8/8/p7/Rn6 w - - 0 1"
    state = GameState.from_fen(fen)
    rules = AntichessRules()
    
    assert rules.is_legal(state, Move("a1a2"))
    assert rules.is_legal(state, Move("a1b1"))
    assert not rules.is_legal(state, Move("a1c1"))

def test_no_capture_allows_any_move():
    # Start pos. No captures.
    state = GameState.starting_setup()
    rules = AntichessRules()
    
    assert rules.is_legal(state, Move("e2e3"))
    assert rules.is_legal(state, Move("g1f3"))

def test_en_passant_is_mandatory():
    # White P e5. Black P d5 (just moved d7-d5). EP d6.
    # e5xd6 is capture. e5-e6 is push (non-capture).
    fen = "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1"
    state = GameState.from_fen(fen)
    rules = AntichessRules()
    
    assert rules.is_legal(state, Move("e5d6"))
    # Can pawn move e5-e6? No, blocked? No, e6 is empty.
    # But capture is mandatory.
    assert not rules.is_legal(state, Move("e5e6"))

def test_king_mechanics_check_ignored():
    # King in check.
    fen = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 2"
    state = GameState.from_fen(fen)
    rules = AntichessRules()
    
    assert not rules.is_check(state)
    assert not rules.get_game_over_reason(state) == GameOverReason.CHECKMATE
    
    # King can move to attacked square?
    assert rules.is_legal(state, Move("e1f2"))

def test_castling_illegal():
    # Setup where castling would be legal in standard.
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQK2R w KQkq - 0 1"
    state = GameState.from_fen(fen)
    rules = AntichessRules()
    
    # Castling e1g1
    assert not rules.is_legal(state, Move("e1g1"))
    assert rules.validate_move(state, Move("e1g1")) == MoveLegalityReason.CASTLING_DISABLED

def test_termination_zero_pieces():
    # White has no pieces.
    fen = "8/8/8/8/8/8/8/k7 w - - 0 1"
    state = GameState.from_fen(fen)
    rules = AntichessRules()
    
    assert rules.is_game_over(state)
    
def test_termination_stalemate():
    # White has pieces but no moves.
    fen = "8/8/8/8/8/p7/P7/k7 w - - 0 1"
    state = GameState.from_fen(fen)
    rules = AntichessRules()
    
    legal_moves = rules.get_legal_moves(state)
    assert not legal_moves
    assert rules.is_game_over(state)