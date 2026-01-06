from v_chess.game import Game
from v_chess.rules import AntichessRules
from v_chess.move import Move

def test_reproduce_illegal_move_ghost_pawn():
    """Reproduce 'move not in piece moveset' for c8c6 in Antichess."""
    # FEN from user report (re-verified: empty c8)
    fen = "r5r1/p1p3pp/p7/8/2K5/P6P/P6P/R6R b - - 0 22"
    game = Game(fen, rules=AntichessRules())

    # Try c8c6 (Invalid start square)
    move = Move("c8c6")

    # Expected: NO_PIECE (because c8 is empty)
    reason = game.rules.move_pseudo_legality_reason(game.state, move)

    # Assert we get NO_PIECE
    assert reason.value == "no piece moved."

    # Try c7c5 (Valid start square, likely intended move)
    move_valid = Move("c7c5")
    reason_valid = game.rules.move_pseudo_legality_reason(game.state, move_valid)
    assert reason_valid.value == "move is legal"

def test_reproduce_illegal_board_valid():
    """Reproduce 'Board state is illegal. Reason: valid'."""
    # Same FEN.
    fen = "r5r1/p1p3pp/p7/8/2K5/P6P/P6P/R6R b - - 0 22"
    game = Game(fen, rules=AntichessRules())

    # Verify rules are AntichessRules
    assert isinstance(game.rules, AntichessRules)

    from v_chess.enums import BoardLegalityReason
    is_legal = game.rules.validate_board_state(game.state) == BoardLegalityReason.VALID

    # This should be True for Antichess
    assert is_legal is True

    # If we use StandardRules, it should be False
    from v_chess.rules import StandardRules
    std_rules = StandardRules()
    assert (std_rules.validate_board_state(game.state) == BoardLegalityReason.VALID) is False # No black king
