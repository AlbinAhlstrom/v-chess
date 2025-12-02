from hypothesis import given, strategies as st
from chess.game import Game
from chess.board import Board
from chess.move import Move
from chess.square import Square
from chess.enums import Color
from chess.piece.pawn import Pawn
from chess.piece.rook import Rook

def board():
    """Generates a board in the standard starting position."""
    return st.just(Board.starting_setup())

def squares():
    """Generates valid Square objects."""
    return st.builds(Square, st.integers(min_value=0, max_value=7), st.integers(min_value=0, max_value=7))


@given(board=board(), start=squares(), end=squares())
def test_pseudo_legal_no_piece_moved(board, start, end):
    """Test rejection when moving from an empty square."""
    if board.get_piece(start) is not None:
        board.remove_piece(start)

    game = Game(board)
    move = Move(start, end)

    is_legal, reason = game.is_move_pseudo_legal(move)
    assert is_legal is False
    assert reason == "No piece moved."

@given(board=board(), start=squares(), end=squares())
def test_pseudo_legal_wrong_piece_color(board, start, end):
    """Test rejection when moving the opponent's piece."""
    game = Game(board)

    # Place an opponent's piece on start (Black, since White starts)
    opponent_piece = Rook(Color.BLACK)
    board.set_piece(opponent_piece, start)

    move = Move(start, end)

    is_legal, reason = game.is_move_pseudo_legal(move)
    assert is_legal is False
    assert reason == "Wrong piece color."

@given(board=board())
def test_pseudo_legal_move_not_in_moveset(board):
    """Test rejection when the move is geometrically impossible for the piece."""
    game = Game(board)

    # White Rook on A1 (0,0) trying to move like a Knight to B3 (2, 1)
    start = Square(0, 0)
    # A1 is a Rook in standard setup.
    # Let's ensure it is a rook specifically for the test stability
    board.set_piece(Rook(Color.WHITE), start)

    # A Knight jump is invalid for a Rook
    invalid_end = Square(2, 1)

    move = Move(start, invalid_end)

    is_legal, reason = game.is_move_pseudo_legal(move)
    assert is_legal is False
    assert reason == "Move not in piece moveset."

@given(board=board())
def test_pseudo_legal_cant_capture_own_piece(board):
    """Test rejection when capturing one's own piece."""
    game = Game(board)

    # White Rook on A1 trying to capture White Pawn on A2
    start = Square(7, 0) # A1
    end = Square(6, 0)   # A2

    # Ensure setup is correct for test
    board.set_piece(Rook(Color.WHITE), start)
    board.set_piece(Pawn(Color.WHITE), end)

    move = Move(start, end)

    is_legal, reason = game.is_move_pseudo_legal(move)
    assert is_legal is False
    assert reason == "Can't capture own piece."

@given(board=board())
def test_pseudo_legal_pawn_cant_capture_forwards(board):
    """Test rejection when a pawn tries to capture a piece directly in front of it."""
    game = Game(board)

    # White Pawn on E4, Black Pawn on E5
    start = Square(4, 4)
    end = Square(3, 4)

    board.set_piece(Pawn(Color.WHITE), start)
    board.set_piece(Pawn(Color.BLACK), end)

    move = Move(start, end)

    is_legal, reason = game.is_move_pseudo_legal(move)
    assert is_legal is False
    assert reason == "Cant capture forwards with pawn."

@given(board=board())
def test_pseudo_legal_pawn_diagonal_requires_capture(board):
    """Test rejection when a pawn moves diagonally without a target (and not en passant)."""
    game = Game(board)

    # White Pawn on E4 trying to move to F5 (empty)
    start = Square(4, 4)
    end = Square(3, 5)

    board.set_piece(Pawn(Color.WHITE), start)
    board.remove_piece(end) # Ensure target is empty
    board.en_passant_square = None # Ensure not en passant

    move = Move(start, end)

    is_legal, reason = game.is_move_pseudo_legal(move)
    assert is_legal is False
    assert reason == "Diagonal pawn move requires a capture."

@given(board=board())
def test_pseudo_legal_path_is_blocked(board):
    """Test rejection when a sliding piece is blocked by another piece."""
    game = Game(board)

    # White Rook on A1 trying to move to A5, but A3 is blocked
    start = Square(7, 0) # A1
    end = Square(3, 0)   # A5
    blocker_sq = Square(5, 0) # A3

    board.set_piece(Rook(Color.WHITE), start)
    board.set_piece(Pawn(Color.WHITE), blocker_sq) # Block with own piece
    board.remove_piece(end) # Target is empty

    move = Move(start, end)

    is_legal, reason = game.is_move_pseudo_legal(move)

    assert not is_legal, f"Expected 'Path is blocked'. got {reason}"
    assert reason == "Path is blocked."
    assert end not in board.unblocked_paths(board.get_piece(start))

def test_leaving_king_in_check_is_pseudo_legal():
    fen = "k7/r7/8/8/8/8/R7/K7 w - - 0 1"
    board = Board.from_fen(fen)
    move = Move.from_uci("a2h2")

    game = Game(board)
    assert game.is_move_pseudo_legal(move)[0]
