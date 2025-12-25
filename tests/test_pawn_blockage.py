import pytest
from v_chess.move import Move
from v_chess.game import Game
from v_chess.exceptions import IllegalMoveException

def test_pawn_double_push_blocked_by_friendly_piece():
    fen = "r2qkb1r/pp2pppp/2np1n2/2p5/4P1b1/1PPP1N2/P4PPP/RNBQKB1R w KQkq - 1 1"
    game = Game(fen)


    move = Move("f2f4")


    is_legal = game.rules.is_legal(move)
    assert not is_legal, "Move f2f4 should be illegal because f3 is blocked by a Knight"

    with pytest.raises(IllegalMoveException):
        game.take_turn(move)
