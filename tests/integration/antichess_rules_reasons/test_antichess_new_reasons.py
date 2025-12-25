import pytest
from v_chess.game_state import GameState
from v_chess.rules import AntichessRules
from v_chess.enums import MoveLegalityReason, GameOverReason
from v_chess.move import Move

def test_antichess_reason_castling_disabled():
    # FEN with castling rights
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQK2R w KQkq - 0 1"
    state = GameState.from_fen(fen)
    rules = AntichessRules(state)
    move = Move("e1g1")
    
    # Logic might not be implemented yet (currently returns NO_CASTLING_RIGHT), but we expect CASTLING_DISABLED
    assert rules.validate_move(move) == MoveLegalityReason.CASTLING_DISABLED

def test_antichess_reason_all_pieces_captured():
    # White has no pieces
    fen = "8/8/8/8/8/8/8/k7 w - - 0 1"
    state = GameState.from_fen(fen)
    rules = AntichessRules(state)
    
    assert rules.is_game_over()
    assert rules.get_game_over_reason() == GameOverReason.ALL_PIECES_CAPTURED

def test_antichess_reason_stalemate_win():
    # White blocked (Stalemate)
    fen = "8/8/8/8/8/p7/P7/k7 w - - 0 1"
    state = GameState.from_fen(fen)
    rules = AntichessRules(state)
    
    assert rules.is_game_over()
    # Stalemate is a win condition in Antichess, but the REASON is still Stalemate
    # or maybe we want "WIN_BY_STALEMATE"? STALEMATE is fine.
    assert rules.get_game_over_reason() == GameOverReason.STALEMATE
