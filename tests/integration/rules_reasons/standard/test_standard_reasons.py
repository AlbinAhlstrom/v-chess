import pytest
from v_chess.rules import StandardRules
from v_chess.fen_helpers import state_from_fen
from v_chess.enums import BoardLegalityReason, MoveLegalityReason, GameOverReason, Color
from v_chess.square import Square
from v_chess.move import Move
from v_chess.piece import King
import dataclasses

def test_standard_board_legality_invalid_castling_rights():
    rules = StandardRules()
    # White King e1. White Castling K. White Rook h1 MISSING.
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w K - 0 1"
    state = state_from_fen(fen)
    state.board.remove_piece(Square("h1"))
    rules.state = state
    assert rules.validate_board_state() == BoardLegalityReason.INVALID_CASTLING_RIGHTS

def test_standard_board_legality_invalid_ep_square():
    rules = StandardRules()
    fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e5 0 1"
    state = state_from_fen(fen)
    rules.state = state
    assert rules.validate_board_state() == BoardLegalityReason.INVALID_EP_SQUARE

def test_standard_move_legality_no_piece():
    rules = StandardRules()
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    state = state_from_fen(fen)
    rules.state = state
    move = Move(Square("d4"), Square("d5"))
    assert rules.validate_move(move) == MoveLegalityReason.NO_PIECE

def test_standard_move_legality_king_promotion():
    rules = StandardRules()
    # Use empty board to avoid capture logic interfering
    fen = "8/P7/8/8/8/8/8/8 w - - 0 1"
    state = state_from_fen(fen)
    rules.state = state
    move = Move(Square("a7"), Square("a8"), King(Color.WHITE))
    assert rules.validate_move(move) == MoveLegalityReason.KING_PROMOTION

def test_standard_game_over_repetition():
    rules = StandardRules()
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    state = state_from_fen(fen)
    state = dataclasses.replace(state, repetition_count=3)
    rules.state = state
    assert rules.get_game_over_reason() == GameOverReason.REPETITION