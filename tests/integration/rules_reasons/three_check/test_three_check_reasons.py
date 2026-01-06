import pytest
from v_chess.rules import ThreeCheckRules
from v_chess.fen_helpers import state_from_fen
from v_chess.enums import BoardLegalityReason, MoveLegalityReason, GameOverReason, Color
from v_chess.square import Square
from v_chess.move import Move
from v_chess.piece import King
import dataclasses

def test_three_check_board_legality_invalid_castling_rights():
    rules = ThreeCheckRules()
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w K - 0 1"
    state = state_from_fen(fen)
    state.board.remove_piece(Square("h1"))
    assert rules.validate_board_state(state) == BoardLegalityReason.INVALID_CASTLING_RIGHTS

def test_three_check_move_legality_king_promotion():
    rules = ThreeCheckRules()
    fen = "8/P7/8/8/8/8/8/8 w - - 0 1"
    state = state_from_fen(fen)
    move = Move(Square("a7"), Square("a8"), King(Color.WHITE))
    assert rules.validate_move(state, move) == MoveLegalityReason.KING_PROMOTION

def test_three_check_game_over_three_checks():
    rules = ThreeCheckRules()
    # ThreeCheckGameState has checks tuple.
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 +3+0"
    state = state_from_fen(fen)
    assert rules.get_game_over_reason(state) == GameOverReason.THREE_CHECKS