import pytest
from oop_chess.game_state import GameState
from oop_chess.rules import AntichessRules
from oop_chess.enums import MoveLegalityReason
from oop_chess.move import Move
from oop_chess.square import Square

def test_antichess_reason_mandatory_capture():
    rules = AntichessRules()
    fen = "8/8/8/8/8/8/p7/R7 w - - 0 1"
    state = GameState.from_fen(fen)
    move = Move("a1b1") # Non-capture when capture is available
    assert rules.move_legality_reason(state, move) == MoveLegalityReason.MANDATORY_CAPTURE

def test_antichess_reason_no_castling_right():
    rules = AntichessRules()
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQK2R w KQkq - 0 1"
    state = GameState.from_fen(fen)
    move = Move("e1g1")
    assert rules.move_legality_reason(state, move) == MoveLegalityReason.CASTLING_DISABLED

def test_antichess_reason_legal_king_into_check():
    rules = AntichessRules()
    fen = "rnbqkbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 2" # Check from Q
    state = GameState.from_fen(fen)
    # Moving e1 to f2 (attacked square) is legal if no capture is available.
    # Q at h4 is NOT capturable by K at e1.
    move = Move("e1f2")
    assert rules.move_legality_reason(state, move) == MoveLegalityReason.LEGAL

def test_antichess_reason_no_piece():
    rules = AntichessRules()
    state = GameState.starting_setup()
    move = Move("e3e4")
    assert rules.move_legality_reason(state, move) == MoveLegalityReason.NO_PIECE

def test_antichess_reason_wrong_color():
    rules = AntichessRules()
    state = GameState.starting_setup()
    move = Move("e7e5")
    assert rules.move_legality_reason(state, move) == MoveLegalityReason.WRONG_COLOR

def test_antichess_reason_not_in_moveset():
    rules = AntichessRules()
    state = GameState.starting_setup()
    move = Move("e2e5")
    assert rules.move_legality_reason(state, move) == MoveLegalityReason.NOT_IN_MOVESET

def test_antichess_reason_own_piece_capture():
    rules = AntichessRules()
    state = GameState.starting_setup()
    move = Move("a1a2")
    assert rules.move_legality_reason(state, move) == MoveLegalityReason.OWN_PIECE_CAPTURE
