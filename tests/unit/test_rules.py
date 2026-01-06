from v_chess.rules import StandardRules
from v_chess.game_state import GameState
from v_chess.move import Move
from v_chess.enums import CastlingRight
from v_chess.square import Square

def test_castling_rights_king_move_revokes_all():
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    state = GameState.from_fen(fen)
    rules = StandardRules()
    
    move = Move("e1e2")
    next_state = rules.apply_move(state, move)
    
    assert CastlingRight.WHITE_SHORT not in next_state.castling_rights
    assert CastlingRight.WHITE_LONG not in next_state.castling_rights
    assert CastlingRight.BLACK_SHORT in next_state.castling_rights
    assert CastlingRight.BLACK_LONG in next_state.castling_rights

def test_castling_rights_rook_move_revokes_side():
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    state = GameState.from_fen(fen)
    rules = StandardRules()
    
    move = Move("h1h2")
    next_state = rules.apply_move(state, move)
    
    assert CastlingRight.WHITE_SHORT not in next_state.castling_rights
    assert CastlingRight.WHITE_LONG in next_state.castling_rights
    assert CastlingRight.BLACK_SHORT in next_state.castling_rights

def test_castling_rights_captured_rook_revokes_side():
    fen = "r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1"
    state = GameState.from_fen(fen)
    rules = StandardRules()
    
    move = Move("a8a1")
    next_state = rules.apply_move(state, move)
    
    assert CastlingRight.WHITE_LONG not in next_state.castling_rights
    assert CastlingRight.WHITE_SHORT in next_state.castling_rights

def test_en_passant_square_set_on_double_push():
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    state = GameState.from_fen(fen)
    rules = StandardRules()
    
    move = Move("e2e4")
    next_state = rules.apply_move(state, move)
    
    assert next_state.ep_square == Square("e3")

def test_en_passant_square_cleared_next_move():
    fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    state = GameState.from_fen(fen)
    rules = StandardRules()
    
    move = Move("a7a6")
    next_state = rules.apply_move(state, move)
    
    assert next_state.ep_square is None

def test_halfmove_clock_reset_on_pawn_move():
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 10 1"
    state = GameState.from_fen(fen)
    rules = StandardRules()
    
    move = Move("e2e4")
    next_state = rules.apply_move(state, move)
    
    assert next_state.halfmove_clock == 0

def test_halfmove_clock_reset_on_capture():
    fen = "rnbqkbnr/pppppppp/8/8/4P3/5n2/PPPP1PPP/RNBQKBNR w KQkq - 10 1"
    state = GameState.from_fen(fen)
    rules = StandardRules()
    
    move = Move("g2f3")
    next_state = rules.apply_move(state, move)
    
    assert next_state.halfmove_clock == 0

def test_halfmove_clock_increment():
    fen = "rnbqkbnr/pppppppp/8/8/8/2N5/PPPPPPPP/R1BQKBNR b KQkq - 10 1"
    state = GameState.from_fen(fen)
    rules = StandardRules()
    
    move = Move("g8f6")
    next_state = rules.apply_move(state, move)
    
    assert next_state.halfmove_clock == 11