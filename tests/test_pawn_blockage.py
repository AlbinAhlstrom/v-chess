import pytest
from oop_chess.board import Board
from oop_chess.move import Move
from oop_chess.square import Square
from oop_chess.game import Game
from oop_chess.exceptions import IllegalMoveException

def test_pawn_double_push_blocked_by_friendly_piece():
    fen = "r2qkb1r/pp2pppp/2np1n2/2p5/4P1b1/1PPP1N2/P4PPP/RNBQKB1R w KQkq - 1 1"
    game = Game(fen)


    move = Move("f2f4")


    is_legal = game.is_move_legal(move)
    assert not is_legal, "Move f2f4 should be illegal because f3 is blocked by a Knight"

    with pytest.raises(IllegalMoveException):
        game.take_turn(move)
