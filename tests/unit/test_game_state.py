import pytest
from oop_chess.game_state import GameState
from oop_chess.enums import Color, CastlingRight
from oop_chess.square import Square
from oop_chess.board import Board

def test_fen_parsing_starting_position():
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    state = GameState.from_fen(fen)

    assert state.turn == Color.WHITE
    assert set(state.castling_rights) == {CastlingRight.WHITE_SHORT, CastlingRight.WHITE_LONG, CastlingRight.BLACK_SHORT, CastlingRight.BLACK_LONG}
    assert state.ep_square is None
    assert state.halfmove_clock == 0
    assert state.fullmove_count == 1
    assert len(state.board.board) == 32

def test_fen_parsing_mid_game():
    fen = "rnbq1rk1/ppp1bppp/5n2/3p4/3P4/2N2N2/PPP1BPPP/R1BQ1RK1 b - - 4 7"
    state = GameState.from_fen(fen)

    assert state.turn == Color.BLACK
    assert state.castling_rights == ()
    assert state.ep_square is None
    assert state.halfmove_clock == 4
    assert state.fullmove_count == 7

def test_fen_parsing_with_en_passant():
    fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    state = GameState.from_fen(fen)

    assert state.ep_square == Square("e3")

def test_fen_serialization_round_trip():
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    state = GameState.from_fen(fen)
    assert state.fen == fen

def test_fen_serialization_complex():
    fen = "rnbq1rk1/ppp1bppp/5n2/3p4/3P4/2N2N2/PPP1BPPP/R1BQ1RK1 b - - 4 7"
    state = GameState.from_fen(fen)
    assert state.fen == fen

def test_fen_parsing_no_castling_rights():
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 1"
    state = GameState.from_fen(fen)
    assert state.castling_rights == ()

def test_invalid_fen_wrong_fields():
    with pytest.raises(ValueError, match="Invalid FEN format"):
        GameState.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0")

def test_invalid_fen_bad_clock():
    with pytest.raises(ValueError, match="FEN halfmove and fullmove must be int"):
        GameState.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - a 1")

def test_gamestate_immutability():
    state = GameState.starting_setup()
    with pytest.raises(AttributeError):
        state.halfmove_clock = 10
