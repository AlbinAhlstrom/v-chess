
import pytest
from v_chess.rules import Chess960Rules
from v_chess.fen_helpers import state_from_fen
from v_chess.enums import BoardLegalityReason, MoveLegalityReason, GameOverReason, Color
from v_chess.square import Square
from v_chess.move import Move
from v_chess.piece import King
import dataclasses

def test_chess960_board_legality_invalid_castling_rights():
    rules = Chess960Rules()
    # Standard FEN is valid 960 too.
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w K - 0 1"
    state = state_from_fen(fen)
    state.board.remove_piece(Square("h1"))
    rules.state = state
    # 960 might validate differently?
    # It checks if Rook is on expected square derived from the right.
    # If K right exists (Standard K), it expects Rook on h1.
    # If missing, it should be INVALID_CASTLING_RIGHTS.
    assert rules.validate_board_state() == BoardLegalityReason.INVALID_CASTLING_RIGHTS

def test_chess960_move_legality_king_promotion():
    rules = Chess960Rules()
    fen = "8/P7/8/8/8/8/8/8 w - - 0 1"
    state = state_from_fen(fen)
    rules.state = state
    move = Move(Square("a7"), Square("a8"), King(Color.WHITE))
    assert rules.validate_move(move) == MoveLegalityReason.KING_PROMOTION

def test_chess960_game_over_repetition():
    rules = Chess960Rules()
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    state = state_from_fen(fen)
    state = dataclasses.replace(state, repetition_count=3)
    rules.state = state
    assert rules.get_game_over_reason() == GameOverReason.REPETITION
