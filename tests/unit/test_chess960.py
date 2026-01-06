from v_chess.game import Game
from v_chess.move import Move
from v_chess.rules import Chess960Rules
from v_chess.enums import Color, MoveLegalityReason
from v_chess.piece import King, Rook

def test_chess960_castling_non_standard():
    """Verify castling in a 960 position (King on f1, Rook on h1)."""
    # 960 setup: ... K ... R
    # White King on f1 (row 7, col 5). White Rook on h1 (row 7, col 7).
    # Castling kingside (O-O) -> King to g1, Rook to f1.
    fen = "k7/8/8/8/8/8/8/5K1R w K - 0 1"
    game = Game(fen, rules=Chess960Rules())
    
    # Target square for Kingside castling is g1 (row 7, col 6)
    move = Move("f1g1")
    assert game.rules.validate_move(game.state, move) == MoveLegalityReason.LEGAL
    
    game.take_turn(move)
    
    from v_chess.square import Square
    print(f"Post-move FEN: {game.state.fen}")
    # game.state.board.print() # Would need stdout capture
    
    # King should be on g1
    piece_g1 = game.state.board.get_piece(Square("g1"))
    assert isinstance(piece_g1, King)
    
    # Rook should be on f1
    piece_f1 = game.state.board.get_piece(Square("f1"))
    assert isinstance(piece_f1, Rook), f"Piece on f1 is {piece_f1}, board is {game.state.board.fen}"

def test_chess960_castling_blocked():
    """Verify castling is blocked by pieces in between."""
    # King on f1, Rook on h1. Knight on g1.
    fen = "k7/8/8/8/8/8/8/5KNR w K - 0 1"
    game = Game(fen, rules=Chess960Rules())
    
    move = Move("f1g1")
    assert game.rules.validate_move(game.state, move) != MoveLegalityReason.LEGAL
