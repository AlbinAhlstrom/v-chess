from v_chess.game_state import GameState
from v_chess.rules import AntichessRules
from v_chess.enums import MoveLegalityReason, GameOverReason
from v_chess.move import Move

def test_antichess_reason_castling_disabled():
    # FEN with castling rights
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQK2R w KQkq - 0 1"
    state = GameState.from_fen(fen)
    rules = AntichessRules()
    move = Move("e1g1")
    
    assert rules.validate_move(state, move) == MoveLegalityReason.CASTLING_DISABLED

def test_antichess_reason_all_pieces_captured():
    # White has no pieces
    fen = "8/8/8/8/8/8/8/k7 w - - 0 1"
    state = GameState.from_fen(fen)
    rules = AntichessRules()
    
    assert rules.is_game_over(state)
    assert rules.get_game_over_reason(state) == GameOverReason.ALL_PIECES_CAPTURED

def test_antichess_reason_stalemate_win():
    # White blocked (Stalemate)
    fen = "8/8/8/8/8/p7/P7/k7 w - - 0 1"
    state = GameState.from_fen(fen)
    rules = AntichessRules()
    
    assert rules.is_game_over(state)
    assert rules.get_game_over_reason(state) == GameOverReason.STALEMATE