import pytest
from oop_chess.game_state import GameState
from oop_chess.rules import AntichessRules
from oop_chess.enums import MoveLegalityReason, GameOverReason
from oop_chess.move import Move

def test_antichess_reason_castling_disabled():
    rules = AntichessRules()
    # FEN with castling rights
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQK2R w KQkq - 0 1"
    state = GameState.from_fen(fen)
    move = Move("e1g1")
    
    # Logic might not be implemented yet (currently returns NO_CASTLING_RIGHT), but we expect CASTLING_DISABLED
    assert rules.move_legality_reason(state, move) == MoveLegalityReason.CASTLING_DISABLED

def test_antichess_reason_all_pieces_captured():
    rules = AntichessRules()
    # White has no pieces
    fen = "8/8/8/8/8/8/8/k7 w - - 0 1"
    state = GameState.from_fen(fen)
    
    assert rules.is_game_over(state)
    assert rules.game_over_reason(state) == GameOverReason.ALL_PIECES_CAPTURED

def test_antichess_reason_stalemate_win():
    rules = AntichessRules()
    # White blocked (Stalemate)
    fen = "8/8/8/8/8/p7/P7/k7 w - - 0 1"
    state = GameState.from_fen(fen)
    
    assert rules.is_game_over(state)
    # Stalemate is a win condition in Antichess, but the REASON is still Stalemate
    # or maybe we want "WIN_BY_STALEMATE"? STALEMATE is fine.
    assert rules.game_over_reason(state) == GameOverReason.STALEMATE
