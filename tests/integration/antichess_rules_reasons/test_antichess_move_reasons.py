from v_chess.game_state import GameState
from v_chess.rules import AntichessRules
from v_chess.enums import MoveLegalityReason
from v_chess.move import Move

def test_antichess_reason_mandatory_capture():
    fen = "8/8/8/8/8/8/p7/R7 w - - 0 1"
    state = GameState.from_fen(fen)
    rules = AntichessRules()
    move = Move("a1b1") # Non-capture when capture is available
    assert rules.validate_move(state, move) == MoveLegalityReason.MANDATORY_CAPTURE

def test_antichess_reason_no_castling_right():
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQK2R w KQkq - 0 1"
    state = GameState.from_fen(fen)
    rules = AntichessRules()
    move = Move("e1g1")
    assert rules.validate_move(state, move) == MoveLegalityReason.CASTLING_DISABLED

def test_antichess_reason_legal_king_into_check():
    fen = "rnbqkbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 2" # Check from Q
    state = GameState.from_fen(fen)
    rules = AntichessRules()
    # Moving e1 to f2 (attacked square) is legal if no capture is available.
    move = Move("e1f2")
    assert rules.validate_move(state, move) == MoveLegalityReason.LEGAL

def test_antichess_reason_no_piece():
    state = GameState.starting_setup()
    rules = AntichessRules()
    move = Move("e3e4")
    assert rules.validate_move(state, move) == MoveLegalityReason.NO_PIECE

def test_antichess_reason_wrong_color():
    state = GameState.starting_setup()
    rules = AntichessRules()
    move = Move("e7e5")
    assert rules.validate_move(state, move) == MoveLegalityReason.WRONG_COLOR

def test_antichess_reason_not_in_moveset():
    state = GameState.starting_setup()
    rules = AntichessRules()
    move = Move("e2e5")
    assert rules.validate_move(state, move) == MoveLegalityReason.NOT_IN_MOVESET

def test_antichess_reason_own_piece_capture():
    state = GameState.starting_setup()
    rules = AntichessRules()
    move = Move("a1a2")
    assert rules.validate_move(state, move) == MoveLegalityReason.OWN_PIECE_CAPTURE