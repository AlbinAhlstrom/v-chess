import pytest
from v_chess.game_state import GameState
from v_chess.rules import StandardRules
from v_chess.enums import MoveLegalityReason, Color
from v_chess.move import Move
from v_chess.piece import Queen

def test_reason_no_piece():
    state = GameState.starting_setup()
    rules = StandardRules(state)
    move = Move("e3e4")
    rules.validate_move(move)

def test_reason_wrong_color():
    state = GameState.starting_setup()
    rules = StandardRules(state)
    move = Move("e7e5")
    assert rules.validate_move(move) == MoveLegalityReason.WRONG_COLOR

def test_reason_no_castling_right():
    fen = "r3k2r/8/8/8/8/8/8/R3K2R w - - 0 1"
    state = GameState.from_fen(fen)
    rules = StandardRules(state)
    move = Move("e1g1")
    assert rules.validate_move(move) == MoveLegalityReason.NO_CASTLING_RIGHT

def test_reason_castling_from_check():
    fen = "r3k2r/8/8/8/8/8/4r3/R3K2R w KQkq - 0 1"
    state = GameState.from_fen(fen)
    rules = StandardRules(state)
    move = Move("e1g1")
    assert rules.validate_move(move) == MoveLegalityReason.CASTLING_FROM_CHECK

def test_reason_castling_through_check():
    fen = "r3k2r/8/8/8/8/8/5r2/R3K2R w KQkq - 0 1"
    state = GameState.from_fen(fen)
    rules = StandardRules(state)
    move = Move("e1g1")
    assert rules.validate_move(move) == MoveLegalityReason.CASTLING_THROUGH_CHECK

def test_reason_not_in_moveset():
    state = GameState.starting_setup()
    rules = StandardRules(state)
    move = Move("e2e5")
    assert rules.validate_move(move) == MoveLegalityReason.NOT_IN_MOVESET

def test_reason_own_piece_capture():
    state = GameState.starting_setup()
    rules = StandardRules(state)
    move = Move("a1a2")
    assert rules.validate_move(move) == MoveLegalityReason.OWN_PIECE_CAPTURE

def test_reason_forward_pawn_capture():
    fen = "8/8/8/8/4p3/4P3/8/8 w - - 0 1"
    state = GameState.from_fen(fen)
    rules = StandardRules(state)
    move = Move("e3e4")
    assert rules.validate_move(move) == MoveLegalityReason.FORWARD_PAWN_CAPTURE

def test_reason_pawn_diagonal_non_capture():
    state = GameState.starting_setup()
    rules = StandardRules(state)
    move = Move("e2f3")
    assert rules.validate_move(move) == MoveLegalityReason.PAWN_DIAGONAL_NON_CAPTURE

def test_reason_non_promotion():
    fen = "8/P7/8/8/8/8/8/8 w - - 0 1"
    state = GameState.from_fen(fen)
    rules = StandardRules(state)
    move = Move("a7a8")
    assert rules.validate_move(move) == MoveLegalityReason.NON_PROMOTION

def test_reason_path_blocked():
    state = GameState.starting_setup()
    rules = StandardRules(state)
    move = Move("a1a3")
    assert rules.validate_move(move) == MoveLegalityReason.PATH_BLOCKED

from v_chess.square import Square

def test_reason_early_promotion():
    state = GameState.starting_setup()
    rules = StandardRules(state)
    move = Move(Square("e2"), Square("e3"), Queen(Color.WHITE))
    assert rules.validate_move(move) == MoveLegalityReason.EARLY_PROMOTION

def test_reason_king_left_in_check():
    fen = "rnbqkbnr/pppp1Qpp/8/4p3/4P3/8/PPPP1PPP/RNB1KBNR b KQkq - 0 1"
    state = GameState.from_fen(fen)
    rules = StandardRules(state)
    move = Move("a7a6")
    assert rules.validate_move(move) == MoveLegalityReason.KING_LEFT_IN_CHECK
