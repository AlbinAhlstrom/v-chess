from oop_chess.game import Game
from oop_chess.move import Move


def test_checkmate():
    fen = 'rnbqkbnr/pppp1ppp/8/4p3/6P1/5P2/PPPPP2P/RNBQKBNR b KQkq g3 0 3'
    game = Game(fen=fen)
    move = Move.from_uci("d8h4")
    assert game.is_move_legal(move)
    game.take_turn(move)
    assert game.is_over
    assert game.is_checkmate



def test_checkmate_on_backrank():
    fen = 'Q1q1kbnr/2pppppp/n7/8/8/8/1PPPPPPP/RNBQKBNR w KQk - 0 11'
    game = Game(fen=fen)
    move = Move.from_uci("a8c8")
    assert game.is_move_legal(move)
    game.take_turn(move)
    assert game.is_over
    assert game.is_checkmate

def test_scholars_mate():
    fen = 'r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 1'
    game = Game(fen=fen)
    move = Move.from_uci("h5f7")
    assert game.is_move_legal(move)
    game.take_turn(move)
    assert game.is_over
    assert game.is_checkmate
