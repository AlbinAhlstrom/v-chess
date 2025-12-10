from hypothesis import given, strategies as st
from oop_chess.game import Game
from oop_chess.board import Board
from oop_chess.move import Move
from oop_chess.square import Square
from oop_chess.enums import Color
from oop_chess.piece.pawn import Pawn
from oop_chess.piece.rook import Rook

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
    board.ep_square = None # Ensure not en passant

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

def test_pseudo_legal_en_passant_is_legal():
    """Test that a valid en passant capture is recognized as pseudo-legal."""
    # FEN: White pawn on e5, black on d5, en passant on d6
    fen = "4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1"
    board = Board.from_fen(fen)
    game = Game(board)

    # White's en passant capture: e5xd6
    move = Move.from_uci("e5d6")

    is_legal, reason = game.is_move_pseudo_legal(move)
    assert is_legal is True, f"En passant move was incorrectly deemed illegal: {reason}"

def test_fen_after_initial_pawn_move():
    """Test that the FEN's en passant field is correctly 'a3' after 1. a4."""
    board = Board.starting_setup()
    game = Game(board)

    # Make the move 1. a4
    move = Move.from_uci("a2a4")
    game.take_turn(move)

    # The FEN should have 'a3' for the en passant square
    expected_fen = "rnbqkbnr/pppppppp/8/8/P7/8/1PPPPPPP/RNBQKBNR b KQkq a3 0 1"
    assert game.board.fen == expected_fen

def test_en_passant_capture_removes_pawn():
    """Test that an en passant capture correctly removes the captured pawn."""
    # FEN: White pawn on e5, black on d5, en passant on d6
    fen = "4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1"
    board = Board.from_fen(fen)
    game = Game(board)
    captured_pawn_square = Square.from_any('d5')

    # Ensure the black pawn is on d5 before the move
    assert board.get_piece(captured_pawn_square) is not None

    # White's en passant capture: e5xd6
    move = Move.from_uci("e5d6")

    # The game logic should handle setting is_en_passant and removing the pawn.
    game.take_turn(move)

    # After the move, the white pawn should be on d6, and the black pawn on d5 should be gone
    assert board.get_piece(captured_pawn_square) is None
    assert isinstance(board.get_piece(Square.from_any('d6')), Pawn)

def test_en_passant_capture_from_start():
    """Test a specific en passant capture sequence from the starting position."""
    board = Board.starting_setup()
    game = Game(board)

    moves_uci = ["a2a4", "a7a6", "a4a5", "b7b5", "a5b6"]
    for uci in moves_uci:
        move = Move.from_uci(uci)
        game.take_turn(move)

    captured_pawn_square = Square.from_any('b5')
    assert game.board.get_piece(captured_pawn_square) is None

    assert game.board.fen != 'rnbqkbnr/2pppppp/pP6/1p6/8/8/1PPPPPPP/RNBQKBNR b KQkq - 0 3'
    assert isinstance(game.board.get_piece(Square.from_any('b6')), Pawn)

def test_en_passant_valid():
    fen = 'rnbqkbnr/2pppppp/p7/Pp6/8/8/1PPPPPPP/RNBQKBNR w KQkq - 0 3'
    board = Board.from_fen(fen)
    game = Game(board)
    move = Move.from_uci("a5b5")
