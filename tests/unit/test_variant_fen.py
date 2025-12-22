from oop_chess.game_state import GameState, ThreeCheckGameState, CrazyhouseGameState
from oop_chess.fen_helpers import state_from_fen, state_to_fen
from oop_chess.piece import Queen, Pawn
from oop_chess.enums import Color

def test_three_check_fen_parsing():
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 +2+1"
    state = state_from_fen(fen)
    
    assert isinstance(state, ThreeCheckGameState)
    assert state.checks == (2, 1)
    
    # Verify round-trip serialization
    new_fen = state_to_fen(state)
    assert new_fen == fen

def test_crazyhouse_fen_parsing():
    # Pocket with White Queen, Black Pawn
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR[Qp] w KQkq - 0 1"
    state = state_from_fen(fen)
    
    assert isinstance(state, CrazyhouseGameState)
    
    white_pocket = state.pockets[0]
    black_pocket = state.pockets[1]
    
    assert len(white_pocket) == 1
    assert isinstance(white_pocket[0], Queen)
    assert white_pocket[0].color == Color.WHITE
    
    assert len(black_pocket) == 1
    assert isinstance(black_pocket[0], Pawn)
    assert black_pocket[0].color == Color.BLACK
    
    # Verify round-trip serialization
    new_fen = state_to_fen(state)
    assert new_fen == fen

def test_standard_fen_parsing():
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    state = state_from_fen(fen)
    
    assert isinstance(state, GameState)
    assert not isinstance(state, ThreeCheckGameState)
    assert not isinstance(state, CrazyhouseGameState)
    
    new_fen = state_to_fen(state)
    assert new_fen == fen
