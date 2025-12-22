from oop_chess.game import Game
from oop_chess.rules import AntichessRules
from oop_chess.move import Move

def test_reproduce_illegal_move_ghost_pawn():
    """Reproduce 'move not in piece moveset' for c8c6 in Antichess."""
    # FEN from user report (re-verified: empty c8)
    fen = "r5r1/p1p3pp/p7/8/2K5/P6P/P6P/R6R b - - 0 22"
    game = Game(fen, rules=AntichessRules())

    # Try c8c6 (Invalid start square)
    move = Move("c8c6")

    # Expected: NO_PIECE (because c8 is empty)
    # If we get NOT_IN_MOVESET, it means backend thinks there is a piece.
    is_legal, reason = game.is_move_pseudo_legal(move)
    # In Antichess, is_move_pseudo_legal uses StandardRules logic.

    # Assert we get NO_PIECE
    assert reason == "no piece moved."

    # Try c7c5 (Valid start square, likely intended move)
    move_valid = Move("c7c5")
    # Black pawn at c7.
    # c7c5 is double push.
    # Start rank for black is row 1 (rank 7). c7 is rank 7.
    # c6 empty? Yes (p1p3pp).
    # c5 empty? Yes (8).
    # So c7c5 is pseudo-legal.
    is_legal, reason = game.is_move_pseudo_legal(move_valid)
    assert is_legal is True

def test_reproduce_illegal_board_valid():
    """Reproduce 'Board state is illegal. Reason: valid'."""
    # Same FEN.
    fen = "r5r1/p1p3pp/p7/8/2K5/P6P/P6P/R6R b - - 0 22"
    game = Game(fen, rules=AntichessRules())

    # StandardRules checks kings. FEN has NO BLACK KING.
    # So StandardRules.board_state_legality_reason -> NO_BLACK_KING.
    # AntichessRules.board_state_legality_reason -> VALID.

    # Verify rules are AntichessRules
    assert isinstance(game.rules, AntichessRules)

    # Verify internal check
    # game.rules.is_board_state_legal()
    # Should use AntichessRules.is_board_state_legal (Inherited from Standard)
    # which calls self.board_state_legality_reason (Overridden in Antichess)
    from oop_chess.enums import BoardLegalityReason
    is_legal = game.rules.validate_board_state() == BoardLegalityReason.VALID

    # This should be True for Antichess
    assert is_legal is True

    # If we use StandardRules, it should be False
    from oop_chess.rules import StandardRules
    std_rules = StandardRules(game.state)
    assert (std_rules.validate_board_state() == BoardLegalityReason.VALID) is False # No black king
