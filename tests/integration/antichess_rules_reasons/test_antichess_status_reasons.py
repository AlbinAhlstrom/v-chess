import pytest
from oop_chess.game_state import GameState
from oop_chess.rules import AntichessRules
from oop_chess.enums import StatusReason

def test_antichess_status_valid():
    rules = AntichessRules()
    state = GameState.starting_setup()
    assert rules.status(state) == StatusReason.VALID

def test_antichess_status_too_many_white_pawns():
    rules = AntichessRules()
    fen = "rnbqkbnr/pppppppp/8/8/P7/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    state = GameState.from_fen(fen)
    assert rules.status(state) == StatusReason.TOO_MANY_WHITE_PAWNS

def test_antichess_status_too_many_black_pawns():
    rules = AntichessRules()
    fen = "rnbqkbnr/pppppppp/8/p7/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    state = GameState.from_fen(fen)
    assert rules.status(state) == StatusReason.TOO_MANY_BLACK_PAWNS

def test_antichess_status_pawns_on_backrank():
    rules = AntichessRules()
    fen = "rnbqkbnr/pppppppp/8/8/8/8/8/PNBQKBNR w KQkq - 0 1"
    state = GameState.from_fen(fen)
    assert rules.status(state) == StatusReason.PAWNS_ON_BACKRANK

def test_antichess_status_invalid_ep_square():
    rules = AntichessRules()
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq e4 0 1"
    state = GameState.from_fen(fen)
    assert rules.status(state) == StatusReason.INVALID_EP_SQUARE

def test_antichess_status_valid_no_king():
    rules = AntichessRules()
    fen = "rnbq1bnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQ1BNR w - - 0 1" # No kings
    state = GameState.from_fen(fen)
    # Antichess ignores missing kings in its overridden status logic.
    assert rules.status(state) == StatusReason.VALID
