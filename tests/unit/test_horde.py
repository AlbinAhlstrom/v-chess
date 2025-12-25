from v_chess.game import Game
from v_chess.move import Move
from v_chess.rules import HordeRules
from v_chess.enums import Color, GameOverReason, MoveLegalityReason
from v_chess.piece import Queen, Pawn, Knight, King

def test_horde_win_white_checkmate():
    """Verify White wins by checkmating Black King."""
    # Black King at h8. Black Pawns at g7, h7.
    # White Queen at g6. White Pawn at f6 (protects g7).
    # White Queen g6 moves to g7#
    fen = "7k/6pp/5PQ1/8/8/8/8/8 w - - 0 1"
    game = Game(fen, rules=HordeRules())
    
    game.take_turn(Move("g6g7"))
    
    assert game.is_over
    assert game.game_over_reason == GameOverReason.CHECKMATE
    assert game.winner == "w"

def test_horde_win_black_all_captured():
    """Verify Black wins by capturing all white pieces."""
    fen = "r6k/8/8/8/8/8/8/P7 b - - 0 1"
    game = Game(fen, rules=HordeRules())
    
    # 1... Rxa1
    game.take_turn(Move("a8a1"))
    
    assert game.is_over
    assert game.game_over_reason == GameOverReason.ALL_PIECES_CAPTURED
    assert game.winner == "b"

def test_horde_pawn_rank1_double_push():
    """Verify White Pawns on Rank 1 can move 2 squares."""
    fen = "k7/8/8/8/8/8/8/P7 w - - 0 1"
    game = Game(fen, rules=HordeRules())
    
    # Move a1-a3
    assert game.is_move_legal(Move("a1a3"))
    game.take_turn(Move("a1a3"))
    
    from v_chess.square import Square
    assert isinstance(game.state.board.get_piece(Square("a3")), Pawn)

def test_horde_get_legal_moves_white():
    """Verify white can get legal moves in Horde (no NameError)."""
    fen = "k7/8/8/8/8/8/8/P7 w - - 0 1"
    game = Game(fen, rules=HordeRules())
    moves = game.rules.get_legal_moves()
    assert len(moves) > 0
    # a1-a2 and a1-a3 should be legal
    uci_moves = [m.uci for m in moves]
    assert "a1a2" in uci_moves
    assert "a1a3" in uci_moves
