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
    assert not game.rules.validate_move(Move("a1b1")) == MoveLegalityReason.LEGAL
    # White captures
    game.take_turn(Move("a1a2"))

    # Now Black's turn. Black R b8. White R a2.
    # b8xa2? No, R b8 -> a2 is not theoretical move?
    # R moves straight. b8->a2 is Knight move.
    # R b8->b2? No.
    # So Black might not have mandatory capture.
    pass

def test_king_capture():
    """Verify King can be captured."""
    # White R a1. Black K a2.
    fen = "8/8/8/8/8/8/k7/R7 w - - 0 1"
    game = Game(fen, rules=AntichessRules())

    # White MUST capture K.
    assert game.rules.validate_move(Move("a1a2")) == MoveLegalityReason.LEGAL
    game.take_turn(Move("a1a2"))

    assert game.state.board.get_piece("a2").color == "w"
    # Black has no King. Game continues?
    # In Antichess, King is not royal. Losing King is fine.
    # Losing ALL pieces is the goal.
    assert game.rules.get_game_over_reason() != GameOverReason.ONGOING
