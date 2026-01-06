import pytest
from v_chess.rules import HordeRules
from v_chess.fen_helpers import state_from_fen
from v_chess.enums import BoardLegalityReason, MoveLegalityReason, GameOverReason, Color
from v_chess.square import Square
from v_chess.move import Move
from v_chess.piece import King
import dataclasses

def test_horde_board_legality_invalid_castling_rights():
    rules = HordeRules()
    # Black to move. Castling k (Black Short). Missing Rook h8.
    # FEN: Black King e8, missing h8 rook.
    fen = "rnbqkbn1/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b k - 0 1"
    state = state_from_fen(fen)
    state.board.remove_piece(Square("h8")) # Explicitly ensure removed
    assert rules.validate_board_state(state) == BoardLegalityReason.INVALID_CASTLING_RIGHTS

def test_horde_board_legality_invalid_ep_square():
    rules = HordeRules()
    fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b Kkq e5 0 1"
    state = state_from_fen(fen)
    assert rules.validate_board_state(state) == BoardLegalityReason.INVALID_EP_SQUARE

def test_horde_move_legality_king_promotion():
    rules = HordeRules()
    fen = "8/P7/8/8/8/8/8/8 w - - 0 1"
    state = state_from_fen(fen)
    move = Move(Square("a7"), Square("a8"), King(Color.WHITE))
    assert rules.validate_move(state, move) == MoveLegalityReason.KING_PROMOTION

def test_horde_game_over_repetition():
    rules = HordeRules()
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    state = state_from_fen(fen)
    state = dataclasses.replace(state, repetition_count=3)
    assert rules.get_game_over_reason(state) == GameOverReason.REPETITION
