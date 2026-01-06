import pytest
from v_chess.game import Game
from v_chess.move import Move

def test_castling_prevented_through_check():
    fen = "5k2/5r2/8/8/8/8/8/R3K2R w KQ - 0 1"
    game = Game(fen)

    move = Move("e1g1")
    assert not game.is_move_legal(move)

def test_promotion_checkmate():
    fen = "kn6/P1K5/8/8/8/8/5B2/8 w - - 0 1"
    game = Game(fen)

    move = Move("a7b8q")
    game.take_turn(move)

    assert game.is_checkmate

def test_en_passant_discovered_check():
    fen = "4k3/8/8/3pP3/8/8/8/4R2K w - d6 0 1"
    game = Game(fen)

    game.take_turn(Move("e5d6"))

    assert game.is_check
