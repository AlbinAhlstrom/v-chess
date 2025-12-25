import pytest
from v_chess.game import Game
from v_chess.move import Move
from v_chess.enums import Color, CastlingRight
from v_chess.square import Square
from v_chess.game_state import GameState

def test_turn_switch():
    """Verify turn switches from White to Black and back."""
    game = Game()
    assert game.state.turn == Color.WHITE
    
    game.take_turn(Move("e2e4", player_to_move=game.state.turn))
    assert game.state.turn == Color.BLACK
    
    game.take_turn(Move("e7e5", player_to_move=game.state.turn))
    assert game.state.turn == Color.WHITE

def test_castling_rights_revoked():
    """Verify castling rights are revoked upon moving king/rook."""
    game = Game()
    
    game.take_turn(Move("e2e4", player_to_move=game.state.turn))
    game.take_turn(Move("e7e5", player_to_move=game.state.turn))
    
    game.take_turn(Move("h2h3", player_to_move=game.state.turn))
    game.take_turn(Move("h7h6", player_to_move=game.state.turn))
    
    game.take_turn(Move("h1h2", player_to_move=game.state.turn))
    assert CastlingRight.WHITE_SHORT not in game.state.castling_rights
    assert CastlingRight.WHITE_LONG in game.state.castling_rights
    
    game.take_turn(Move("a7a6", player_to_move=game.state.turn))
    game.take_turn(Move("e1e2", player_to_move=game.state.turn))
    assert CastlingRight.WHITE_LONG not in game.state.castling_rights
    assert len(game.state.castling_rights) == 2

def test_en_passant_square_lifecycle():
    """Verify en passant square is set and cleared correctly."""
    game = Game()
    assert game.state.ep_square is None
    
    game.take_turn(Move("e2e4", player_to_move=game.state.turn))
    assert game.state.ep_square == Square("e3")
    
    game.take_turn(Move("e7e5", player_to_move=game.state.turn))
    assert game.state.ep_square == Square("e6")

def test_halfmove_clock_reset_and_increment():
    """Verify halfmove clock resets on pawn moves/captures and increments otherwise."""
    game = Game()
    assert game.state.halfmove_clock == 0
    
    game.take_turn(Move("g1f3", player_to_move=game.state.turn))
    assert game.state.halfmove_clock == 1
    
    game.take_turn(Move("g8f6", player_to_move=game.state.turn))
    assert game.state.halfmove_clock == 2
    
    game.take_turn(Move("e2e4", player_to_move=game.state.turn))
    assert game.state.halfmove_clock == 0

def test_fullmove_count_increment():
    """Verify fullmove count increments after Black's move."""
    game = Game()
    assert game.state.fullmove_count == 1
    
    game.take_turn(Move("e2e4", player_to_move=game.state.turn))
    assert game.state.fullmove_count == 1
    
    game.take_turn(Move("e7e5", player_to_move=game.state.turn))
    assert game.state.fullmove_count == 2

def test_game_initialization_from_fen():
    """Verify Game correctly initializes state from FEN string."""
    fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    game = Game(fen)
    
    assert game.state.turn == Color.BLACK
    assert game.state.ep_square == Square("e3")
    assert game.state.halfmove_clock == 0
    assert game.state.fullmove_count == 1

def test_game_state_serialization_matches_internal():
    """Verify GameState FEN property matches internal state after moves."""
    game = Game()
    
    game.take_turn(Move("e2e4", player_to_move=game.state.turn))
    expected_fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    assert game.state.fen == expected_fen

def test_history_immutability():
    """Verify history stores distinct snapshots."""
    game = Game()
    initial_fen = game.state.fen
    
    game.take_turn(Move("e2e4", player_to_move=game.state.turn))
    second_fen = game.state.fen
    
    assert len(game.history) == 1
    assert game.history[0].fen == initial_fen
    assert game.history[0].fen != second_fen
    assert game.history[0] is not game.state
