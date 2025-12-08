from chess.board import Board
from chess.game import Game
from chess.move import Move


def test_checkmate():
    fen = 'rnbqkbnr/pppp1ppp/8/4p3/6P1/5P2/PPPPP2P/RNBQKBNR b KQkq g3 0 3'
    board = Board.from_fen(fen)
    game = Game(board)
    move = Move.from_uci("d8h4")
    is_legal, reason = game.is_move_legal(move)
    assert is_legal, reason
    game.take_turn(move)
    assert game.is_over
    assert game.is_checkmate



def test_checkmate_on_backrank():
    fen = 'Q1q1kbnr/2pppppp/n7/8/8/8/1PPPPPPP/RNBQKBNR w KQk - 0 11'
    board = Board.from_fen(fen)
    game = Game(board)
    move = Move.from_uci("a8c8")
    is_legal, reason = game.is_move_legal(move)
    assert is_legal, reason
    game.take_turn(move)
    assert game.is_over
    assert game.is_checkmate

