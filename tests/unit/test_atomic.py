from oop_chess.game import Game
from oop_chess.move import Move
from oop_chess.rules import AtomicRules
from oop_chess.enums import Color, GameOverReason, MoveLegalityReason
from oop_chess.piece import Queen, Pawn, Knight, King

def test_atomic_explosion_simple():
    """Verify standard explosion."""
    # White Knight on f3, Black Pawn on d4.
    # Black Pawn on c6. White Bishop on e5.
    fen = "2k5/8/2p1b3/8/3p4/5N2/8/3K4 w - - 0 1"
    game = Game(fen, rules=AtomicRules())
    
    # 1. Nxd4
    game.take_turn(Move("f3d4"))
    
    from oop_chess.square import Square
    assert game.state.board.get_piece(Square("d4")) is None
    assert game.state.board.get_piece(Square("f3")) is None
    assert game.state.board.get_piece(Square("e5")) is None
    assert game.state.board.get_piece(Square("c6")) is not None

def test_atomic_explosion_pawn_immunity():
    # White Knight f3 (5,5) captures Black Pawn e5 (3,4).
    # White Bishop d4 (4,3) is neighbor.
    # Black Pawn d5 (3,3) is neighbor.
    fen = "4k3/8/8/3pp3/3B4/5N2/8/4K3 w - - 0 1"
    game = Game(fen, rules=AtomicRules())
    
    game.take_turn(Move("f3e5"))
    
    from oop_chess.square import Square
    assert game.state.board.get_piece(Square("e5")) is None
    # Bishop d4 exploded
    assert game.state.board.get_piece(Square("d4")) is None
    # Pawn d5 remains
    assert game.state.board.get_piece(Square("d5")) is not None

def test_atomic_king_cannot_capture():
    """Verify Kings cannot capture."""
    # White King on e1, Black Pawn on e2.
    fen = "4k3/8/8/8/8/8/4p3/4K3 w - - 0 1"
    game = Game(fen, rules=AtomicRules())
    
    # Kxe2 is illegal
    assert game.rules.validate_move(Move("e1e2")) != MoveLegalityReason.LEGAL

def test_atomic_win_by_explosion():
    """Verify winning by exploding opponent King."""
    # Black King on e6 (2,4). Black Pawn on f5 (3,5).
    # White Knight on h4 (4,7).
    # 1. Nxf5 explodes King at e6 (neighbor)
    fen = "8/8/4k3/5p2/7N/8/8/4K3 w - - 0 1"
    game = Game(fen, rules=AtomicRules())
    
    # Nxf5. f5 is (3,5). e6 is (2,4). Neighbor.
    game.take_turn(Move("h4f5"))
    
    assert game.is_over
    assert game.game_over_reason == GameOverReason.KING_EXPLODED
    assert game.winner == "w"

def test_atomic_illegal_own_king_explosion():
    """Verify cannot explode own King."""
    # White King on d1 (7,3). White Knight on f3 (5,5). Black Pawn on e2 (6,4).
    # 1. Nxe2 explodes White King at d1?
    # e2 is (6,4). d1 is (7,3). dx=1, dy=1. Neighbor.
    fen = "4k3/8/8/8/8/5N2/4p3/3K4 w - - 0 1"
    game = Game(fen, rules=AtomicRules())
    
    # Nxe2 is illegal
    assert game.rules.validate_move(Move("f3e2")) != MoveLegalityReason.LEGAL

def test_atomic_adjacent_kings_illegal():
    """Verify Kings cannot be adjacent."""
    # Black King on a1 (7,0). White King on c1 (7,2).
    # Kc1-b1 (7,1) is adjacent to a1.
    fen = "8/8/8/8/8/8/8/k1K5 w - - 0 1"
    game = Game(fen, rules=AtomicRules())
    
    assert game.rules.validate_move(Move("c1b1")) != MoveLegalityReason.LEGAL
