import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from oop_chess.board import Board
from oop_chess.game import Game
from oop_chess.move import Move
from oop_chess.square import Square
from oop_chess.piece.queen import Queen
import traceback

def run_test(test_func):
    test_name = test_func.__name__
    print(f"Running {test_name}...")
    try:
        test_func()
        print(f"PASS: {test_name}")
    except Exception as e:
        print(f"FAIL: {test_name}")
        traceback.print_exc()
        raise

def test_san_simple_pawn_move():
    game = Game()
    move = Move.from_san("e4", game)
    assert move.start == Square.from_str("e2")
    assert move.end == Square.from_str("e4")
    assert move.promotion_piece is None

def test_san_knight_move():
    game = Game()
    move = Move.from_san("Nf3", game)
    assert move.start == Square.from_str("g1")
    assert move.end == Square.from_str("f3")

def test_san_castling():
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQK2R w KQkq - 0 1"
    game = Game(fen=fen)
    move = Move.from_san("O-O", game)
    assert move.start == Square.from_str("e1")
    assert move.end == Square.from_str("g1")

def test_san_disambiguation():
    fen = "8/8/8/8/8/5N2/8/1N4K1 w - - 0 1"
    game = Game(fen=fen)
    move = Move.from_san("Nbd2", game)
    assert move.start == Square.from_str("b1")
    assert move.end == Square.from_str("d2")

    move = Move.from_san("Nfd2", game)
    assert move.start == Square.from_str("f3")
    assert move.end == Square.from_str("d2")

def test_san_capture():
    fen = "rnbqkbnr/pppppppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"
    game = Game(fen=fen)
    move = Move.from_san("exd5", game)
    assert move.start == Square.from_str("e4")
    assert move.end == Square.from_str("d5")

def test_san_promotion():
    fen = "8/P7/8/8/8/8/8/K7 w - - 0 1"
    game = Game(fen=fen)
    move = Move.from_san("a8=Q", game)
    assert move.start == Square.from_str("a7")
    assert move.end == Square.from_str("a8")
    assert isinstance(move.promotion_piece, Queen)
    assert move.promotion_piece.fen == "Q"

def test_san_check_stripping():
    game = Game()
    move = Move.from_san("e4+", game)
    assert move.end == Square.from_str("e4")

def test_san_ambiguous_move_raises():
    fen = "6k1/8/8/8/8/8/8/R3R1K1 w - - 0 1"
    game = Game(fen=fen)
    try:
        Move.from_san("Rc1", game)
        raise AssertionError("Should have raised ValueError for ambiguous move")
    except ValueError as e:
        assert "ambiguous" in str(e)

def test_san_pawn_capture_validation():
    game = Game()
    with pytest.raises(ValueError):
        Move.from_san("exd3", game)
        raise AssertionError("Should have raised ValueError for invalid pawn capture")
