import pytest
from v_chess.board import Board
from v_chess.piece.pawn import Pawn
from v_chess.piece.king import King
from v_chess.piece.rook import Rook
from v_chess.enums import Color
from v_chess.square import Square

def test_board_empty():
    board = Board.empty()
    assert len(board.board) == 0
    assert board.get_piece(Square(0, 0)) is None

def test_set_and_get_piece():
    board = Board.empty()
    pawn = Pawn(Color.WHITE)
    square = Square(1, 1)
    
    board.set_piece(pawn, square)
    
    assert board.get_piece(square) == pawn
    assert board.get_piece(Square(2, 2)) is None

def test_remove_piece():
    board = Board.empty()
    pawn = Pawn(Color.WHITE)
    square = Square(1, 1)
    board.set_piece(pawn, square)
    
    removed_piece = board.remove_piece(square)
    
    assert removed_piece == pawn
    assert board.get_piece(square) is None
    assert len(board.board) == 0

def test_move_piece():
    board = Board.empty()
    pawn = Pawn(Color.WHITE)
    start = Square(1, 1)
    end = Square(2, 1)
    board.set_piece(pawn, start)
    
    board.move_piece(pawn, start, end)
    
    assert board.get_piece(start) is None
    assert board.get_piece(end) == pawn

def test_board_copy():
    board = Board.empty()
    pawn = Pawn(Color.WHITE)
    square = Square(1, 1)
    board.set_piece(pawn, square)
    
    board_copy = board.copy()
    
    assert board_copy.get_piece(square) == pawn
    assert board_copy is not board
    assert board_copy.board is not board.board
    
    board_copy.remove_piece(square)
    assert board_copy.get_piece(square) is None
    assert board.get_piece(square) == pawn

def test_get_pieces():
    board = Board.empty()
    white_pawn = Pawn(Color.WHITE)
    black_pawn = Pawn(Color.BLACK)
    white_king = King(Color.WHITE)
    
    board.set_piece(white_pawn, Square(1, 0))
    board.set_piece(black_pawn, Square(6, 0))
    board.set_piece(white_king, Square(0, 4))
    
    all_pieces = board.get_pieces()
    assert len(all_pieces) == 3
    assert white_pawn in all_pieces
    assert black_pawn in all_pieces
    assert white_king in all_pieces
    
    pawns = board.get_pieces(piece_type=Pawn)
    assert len(pawns) == 2
    assert white_pawn in pawns
    assert black_pawn in pawns
    
    white_pieces = board.get_pieces(color=Color.WHITE)
    assert len(white_pieces) == 2
    assert white_pawn in white_pieces
    assert white_king in white_pieces
    
    white_pawns = board.get_pieces(piece_type=Pawn, color=Color.WHITE)
    assert len(white_pawns) == 1
    assert white_pawn in white_pawns

def test_starting_setup():
    board = Board.starting_setup()
    
    assert len(board.get_pieces(piece_type=Pawn, color=Color.WHITE)) == 8
    assert len(board.get_pieces(piece_type=Pawn, color=Color.BLACK)) == 8
    assert len(board.get_pieces(piece_type=Rook, color=Color.WHITE)) == 2
    assert len(board.get_pieces(piece_type=King, color=Color.WHITE)) == 1
    assert len(board.get_pieces(piece_type=King, color=Color.BLACK)) == 1
