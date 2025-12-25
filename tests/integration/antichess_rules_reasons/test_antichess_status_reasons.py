from v_chess.game_state import GameState
from v_chess.rules import AntichessRules
from v_chess.enums import BoardLegalityReason

def test_antichess_status_valid():
    state = GameState.starting_setup()
    rules = AntichessRules(state)
    assert rules.validate_board_state() == BoardLegalityReason.VALID

def test_antichess_status_too_many_white_pawns():
    fen = "rnbqkbnr/pppppppp/8/8/P7/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    state = GameState.from_fen(fen)
    rules = AntichessRules(state)
    assert rules.validate_board_state() == BoardLegalityReason.TOO_MANY_WHITE_PAWNS

def test_antichess_status_too_many_black_pawns():
    fen = "rnbqkbnr/pppppppp/8/p7/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    state = GameState.from_fen(fen)
    rules = AntichessRules(state)
    assert rules.validate_board_state() == BoardLegalityReason.TOO_MANY_BLACK_PAWNS

def test_antichess_status_pawns_on_backrank():
    fen = "rnbqkbnr/pppppppp/8/8/8/8/8/PNBQKBNR w KQkq - 0 1"
    state = GameState.from_fen(fen)
    rules = AntichessRules(state)
    assert rules.validate_board_state() == BoardLegalityReason.PAWNS_ON_BACKRANK

def test_antichess_status_invalid_ep_square():
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq e4 0 1"
    state = GameState.from_fen(fen)
    rules = AntichessRules(state)
    assert rules.validate_board_state() == BoardLegalityReason.INVALID_EP_SQUARE

def test_antichess_status_valid_no_king():
    fen = "rnbq1bnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQ1BNR w - - 0 1" # No kings
    state = GameState.from_fen(fen)
    rules = AntichessRules(state)
    # Antichess ignores missing kings in its overridden status logic.
    assert rules.validate_board_state() == BoardLegalityReason.VALID
