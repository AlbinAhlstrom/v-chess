import pytest
from v_chess.rules import AntichessRules
from v_chess.fen_helpers import state_from_fen
from v_chess.enums import BoardLegalityReason, MoveLegalityReason, GameOverReason, Color
from v_chess.square import Square
from v_chess.move import Move
from v_chess.piece import King
import dataclasses

def test_antichess_board_legality_invalid_ep_square():
    rules = AntichessRules()
    fen = "8/8/8/8/4P3/8/8/8 b - e5 0 1"
    state = state_from_fen(fen)
    assert rules.validate_board_state(state) == BoardLegalityReason.INVALID_EP_SQUARE

def test_antichess_move_legality_no_piece():
    rules = AntichessRules()
    fen = "8/8/8/8/8/8/8/8 w - - 0 1"
    state = state_from_fen(fen)
    move = Move(Square("d4"), Square("d5"))
    assert rules.validate_move(state, move) == MoveLegalityReason.NO_PIECE

def test_antichess_move_legality_king_promotion():
    rules = AntichessRules()
    fen = "8/P7/8/8/8/8/8/8 w - - 0 1"
    state = state_from_fen(fen)
    move = Move(Square("a7"), Square("a8"), King(Color.WHITE))
    assert rules.validate_move(state, move) == MoveLegalityReason.KING_PROMOTION

def test_antichess_game_over_repetition():
    rules = AntichessRules()
    fen = "8/8/8/8/8/8/8/8 w - - 0 1"
    state = state_from_fen(fen)
    state = dataclasses.replace(state, repetition_count=3)
    assert rules.get_game_over_reason(state) == GameOverReason.REPETITION