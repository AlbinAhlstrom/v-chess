import pytest
from v_chess.game import Game
from v_chess.move import Move
from v_chess.square import Square
from v_chess.enums import Color, CastlingRight
from v_chess.piece.pawn import Pawn
from v_chess.piece.rook import Rook
from v_chess.piece.king import King
from v_chess.piece.queen import Queen

def test_move_application_updates_board():
    """Verify making a move updates the board state correctly."""
    game = Game()
    move = Move("e2e4")
    game.take_turn(move)
    
    board = game.state.board
    assert board.get_piece(Square("e2")) is None
    assert isinstance(board.get_piece(Square("e4")), Pawn)
    assert board.get_piece(Square("e4")).color == Color.WHITE

def test_capture_move_updates_board():
    """Verify capturing removes target and moves attacker."""
    fen = "7k/8/8/8/8/8/p7/R6K w - - 0 1"
    game = Game(fen)
    
    move = Move("a1a2")
    game.take_turn(move)
    
    board = game.state.board
    assert board.get_piece(Square("a1")) is None
    assert isinstance(board.get_piece(Square("a2")), Rook)
    assert board.get_piece(Square("a2")).color == Color.WHITE

def test_castling_updates_king_and_rook():
    """Verify castling moves both King and Rook."""
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQK2R w KQkq - 0 1"
    game = Game(fen)
    
    move = Move("e1g1")
    game.take_turn(move)
    
    board = game.state.board
    assert board.get_piece(Square("e1")) is None
    assert isinstance(board.get_piece(Square("g1")), King)
    assert board.get_piece(Square("h1")) is None
    assert isinstance(board.get_piece(Square("f1")), Rook)

def test_en_passant_capture_removes_correct_pawn():
    """Verify en passant removes the pawn *behind* the destination."""
    fen = "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1"
    game = Game(fen)
    
    move = Move("e5d6")
    game.take_turn(move)
    
    board = game.state.board
    assert board.get_piece(Square("e5")) is None
    assert isinstance(board.get_piece(Square("d6")), Pawn)
    assert board.get_piece(Square("d5")) is None

def test_promotion_places_piece():
    """Verify promotion places the correct piece type."""
    fen = "8/P7/8/8/8/8/8/k6K w - - 0 1"
    game = Game(fen)
    
    move = Move("a7a8q")
    game.take_turn(move)
    
    board = game.state.board
    assert board.get_piece(Square("a7")) is None
    piece = board.get_piece(Square("a8"))
    assert isinstance(piece, Queen)
    assert piece.color == Color.WHITE
