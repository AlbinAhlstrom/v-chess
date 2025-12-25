
import pytest
from v_chess.rules import RacingKingsRules
from v_chess.fen_helpers import state_from_fen
from v_chess.enums import BoardLegalityReason, MoveLegalityReason, GameOverReason, Color
from v_chess.square import Square
from v_chess.move import Move
from v_chess.piece import King
import dataclasses

def test_racing_kings_board_legality_king_in_check():
    rules = RacingKingsRules()
    # King in check. (Illegal in RK)
    # White King e1, Black Rook e2. Black King e8 (safe).
    fen = "4k3/8/8/8/8/8/4r3/4K3 w - - 0 1"
    state = state_from_fen(fen)
    rules.state = state
    assert rules.validate_board_state() == BoardLegalityReason.KING_IN_CHECK

def test_racing_kings_move_legality_gives_check():
    rules = RacingKingsRules()
    # Move that gives check to opponent. (Illegal in RK)
    # White R a1. Black K a8. White K e1.
    fen = "k7/8/8/8/8/8/8/R3K3 w - - 0 1"
    state = state_from_fen(fen)
    rules.state = state
    move = Move(Square("a1"), Square("a2"))
    assert rules.validate_move(move) == MoveLegalityReason.GIVES_CHECK

def test_racing_kings_move_legality_king_promotion():
    rules = RacingKingsRules()
    fen = "8/P7/8/8/8/8/8/8 w - - 0 1"
    state = state_from_fen(fen)
    rules.state = state
    move = Move(Square("a7"), Square("a8"), King(Color.WHITE))
    assert rules.validate_move(move) == MoveLegalityReason.KING_PROMOTION

def test_racing_kings_game_over_repetition():
    rules = RacingKingsRules()
    fen = "8/8/8/8/8/8/8/8 w - - 0 1"
    state = state_from_fen(fen)
    state = dataclasses.replace(state, repetition_count=3)
    rules.state = state
    assert rules.get_game_over_reason() == GameOverReason.REPETITION
