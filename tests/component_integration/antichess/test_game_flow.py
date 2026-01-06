from v_chess.game import Game
from v_chess.rules import AntichessRules
from v_chess.move import Move
from v_chess.enums import MoveLegalityReason, GameOverReason

def test_forced_sequence():
    """Verify game enforces captures in a sequence."""
    # White R a1. Black R a8.
    # 1. R a1xa8 (Mandatory).
    # 2. Black must capture back if possible.
    # Setup: White R a1. Black P a2. Black R b8.
    # White must capture a2.
    fen = "1r6/8/8/8/8/8/p7/R7 w - - 0 1"
    game = Game(fen, rules=AntichessRules())

    # White attempts non-capture
    assert not game.is_move_legal(Move("a1b1"))
    # White captures
    game.take_turn(Move("a1a2"))

def test_king_capture():
    """Verify King can be captured."""
    # White R a1. Black K a2.
    fen = "8/8/8/8/8/8/k7/R7 w - - 0 1"
    game = Game(fen, rules=AntichessRules())

    # White MUST capture K.
    assert game.is_move_legal(Move("a1a2"))
    game.take_turn(Move("a1a2"))

    assert game.state.board.get_piece("a2").color == "w"
    # Black has no King. Game continues?
    # In Antichess, King is not royal. Losing King is fine.
    # Losing ALL pieces is the goal.
    assert game.game_over_reason != GameOverReason.ONGOING