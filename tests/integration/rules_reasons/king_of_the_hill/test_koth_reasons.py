
import pytest
from v_chess.rules import KingOfTheHillRules
from v_chess.fen_helpers import state_from_fen
from v_chess.enums import BoardLegalityReason, MoveLegalityReason, GameOverReason, Color
from v_chess.square import Square
from v_chess.move import Move
from v_chess.piece import King
import dataclasses

def test_koth_board_legality_invalid_castling_rights():
    rules = KingOfTheHillRules()
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w K - 0 1"
    state = state_from_fen(fen)
    state.board.remove_piece(Square("h1"))
    rules.state = state
    assert rules.validate_board_state() == BoardLegalityReason.INVALID_CASTLING_RIGHTS

def test_koth_move_legality_king_promotion():
    rules = KingOfTheHillRules()
    fen = "8/P7/8/8/8/8/8/8 w - - 0 1"
    state = state_from_fen(fen)
    rules.state = state
    move = Move(Square("a7"), Square("a8"), King(Color.WHITE))
    assert rules.validate_move(move) == MoveLegalityReason.KING_PROMOTION

def test_koth_game_over_king_on_hill():
    rules = KingOfTheHillRules()
    # White King on e4 (center).
    fen = "8/8/8/8/4K3/8/8/8 w - - 0 1"
    state = state_from_fen(fen)
    rules.state = state
    assert rules.get_game_over_reason() == GameOverReason.KING_ON_HILL
