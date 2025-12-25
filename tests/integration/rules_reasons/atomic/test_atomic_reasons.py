
import pytest
from v_chess.rules import AtomicRules
from v_chess.fen_helpers import state_from_fen
from v_chess.enums import BoardLegalityReason, MoveLegalityReason, GameOverReason, Color
from v_chess.square import Square
from v_chess.move import Move
from v_chess.piece import King
import dataclasses

def test_atomic_board_legality_kings_adjacent():
    rules = AtomicRules()
    # Kings adjacent: White K e1, Black k e2. Only those pieces.
    fen = "8/8/8/8/8/8/4k3/4K3 w - - 0 1"
    state = state_from_fen(fen)
    rules.state = state
    assert rules.validate_board_state() == BoardLegalityReason.KINGS_ADJACENT

def test_atomic_move_legality_king_exploded_own():
    rules = AtomicRules()
    # White Q captures d2, exploding own King on e1.
    fen = "rnbqkbnr/pppppppp/8/8/8/8/3p4/2Q1K3 w KQkq - 0 1"
    state = state_from_fen(fen)
    rules.state = state
    move = Move(Square("c1"), Square("d2"))
    assert rules.validate_move(move) == MoveLegalityReason.KING_EXPLODED

def test_atomic_game_over_king_exploded():
    rules = AtomicRules()
    fen = "rnbqkbnr/pppppppp/8/8/8/8/8/RNBQ1BNR w KQkq - 0 1" # No white king
    state = state_from_fen(fen)
    rules.state = state
    assert rules.get_game_over_reason() == GameOverReason.KING_EXPLODED

def test_atomic_move_legality_king_promotion():
    rules = AtomicRules()
    fen = "8/P7/8/8/8/8/8/8 w - - 0 1"
    state = state_from_fen(fen)
    rules.state = state
    move = Move(Square("a7"), Square("a8"), King(Color.WHITE))
    assert rules.validate_move(move) == MoveLegalityReason.KING_PROMOTION
