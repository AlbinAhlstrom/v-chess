from oop_chess.game import Game
from oop_chess.move import Move
from oop_chess.rules import CrazyhouseRules
from oop_chess.enums import Color, GameOverReason
from oop_chess.game_state import CrazyhouseGameState
from oop_chess.piece import Queen, Pawn, Knight

def test_crazyhouse_capture_to_pocket():
    """Verify that capturing a piece adds it to the pocket."""
    # White King on h1, White Rook on a1. Black King on h8, Black Pawn on a2.
    fen = "7k/8/8/8/8/8/p7/R6K w - - 0 1"
    game = Game(fen, rules=CrazyhouseRules())
    
    # 1. Rxa2
    game.take_turn(Move("a1a2"))
    
    assert isinstance(game.state, CrazyhouseGameState)
    # White should now have a Pawn in their pocket
    white_pocket = game.state.pockets[0]
    assert len(white_pocket) == 1
    assert isinstance(white_pocket[0], Pawn)
    assert white_pocket[0].color == Color.WHITE

def test_crazyhouse_drop_move():
    """Verify that dropping a piece works."""
    # White has a Knight in pocket
    fen = "k7/8/8/8/8/8/8/7K[N] w - - 0 1"
    game = Game(fen, rules=CrazyhouseRules())
    
    assert len(game.state.pockets[0]) == 1
    
    # Drop Knight to e4
    drop_move = Move("N@e4")
    game.take_turn(drop_move)
    
    # Knight should be on e4
    from oop_chess.square import Square
    piece = game.state.board.get_piece(Square("e4"))
    assert isinstance(piece, Knight)
    assert piece.color == Color.WHITE
    
    # Pocket should be empty
    assert len(game.state.pockets[0]) == 0

def test_crazyhouse_legal_moves_include_drops():
    """Verify that legal_moves includes possible drops."""
    fen = "k7/8/8/8/8/8/8/7K[Q] w - - 0 1"
    game = Game(fen, rules=CrazyhouseRules())
    
    legal_uci = [m.uci for m in game.legal_moves]
    assert "Q@e4" in legal_uci
    assert "Q@a1" in legal_uci

def test_crazyhouse_illegal_pawn_drop():
    """Verify pawns cannot be dropped on 1st or 8th rank."""
    fen = "k7/8/8/8/8/8/8/7K[P] w - - 0 1"
    game = Game(fen, rules=CrazyhouseRules())
    
    legal_uci = [m.uci for m in game.legal_moves]
    assert "P@e4" in legal_uci
    assert "P@e1" not in legal_uci
    assert "P@e8" not in legal_uci

def test_crazyhouse_drop_on_occupied_square():
    """Verify pieces cannot be dropped on occupied squares."""
    # White Pawn on e4, White has Queen in pocket
    fen = "k7/8/8/8/4P3/8/8/7K[Q] w - - 0 1"
    game = Game(fen, rules=CrazyhouseRules())
    
    legal_uci = [m.uci for m in game.legal_moves]
    assert "Q@e4" not in legal_uci

def test_crazyhouse_checkmate_with_drop():
    """Verify dropping a piece can deliver mate."""
    # White has Rook on a7, Queen in pocket. Black King on h8, pawns on g7, h7.
    fen = "7k/R5pp/8/8/8/8/8/7K[Q] w - - 0 1"
    game = Game(fen, rules=CrazyhouseRules())
    
    # White drops Queen to a8. 
    # Board becomes: Q6k/R5pp/...
    # Queen at a8 checks King at h8 (horizontal).
    # King can't move to g8 (attacked by Q at a8 and R at a7).
    # King can't take Q (too far).
    # Black can't block (too close).
    
    game.take_turn(Move("Q@a8"))
    
    assert game.is_over
    assert game.game_over_reason == GameOverReason.CHECKMATE