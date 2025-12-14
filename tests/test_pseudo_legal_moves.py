from hypothesis import given, strategies as st
from oop_chess.game import Game
from oop_chess.board import Board
from oop_chess.move import Move
from oop_chess.square import Square
from oop_chess.enums import Color, MoveLegalityReason
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
    assert reason == MoveLegalityReason.NO_PIECE

@given(board=board(), start=squares(), end=squares())
def test_pseudo_legal_wrong_piece_color(board, start, end):
    """Test rejection when moving the opponent's piece."""
    game = Game(board)
    opponent_piece = Rook(Color.BLACK)
    board.set_piece(opponent_piece, start)
    move = Move(start, end)

    is_legal, reason = game.is_move_pseudo_legal(move)
    assert is_legal is False
    assert reason == MoveLegalityReason.WRONG_COLOR

@given(board=board())
def test_pseudo_legal_move_not_in_moveset(board):
    """Test rejection when the move is geometrically impossible for the piece."""
    game = Game(board)
    start = Square(0, 0)
    board.set_piece(Rook(Color.WHITE), start)
    invalid_end = Square(2, 1)
    move = Move(start, invalid_end)

    is_legal, reason = game.is_move_pseudo_legal(move)
    assert is_legal is False
    assert reason == MoveLegalityReason.NOT_IN_MOVESET

@given(board=board())
def test_pseudo_legal_cant_capture_own_piece(board):
    """Test rejection when capturing one's own piece."""
    game = Game(board)
    start = Square(7, 0)
    end = Square(6, 0)
    board.set_piece(Rook(Color.WHITE), start)
    board.set_piece(Pawn(Color.WHITE), end)
    move = Move(start, end)

    is_legal, reason = game.is_move_pseudo_legal(move)
    assert is_legal is False
    assert reason == MoveLegalityReason.OWN_PIECE_CAPTURE

@given(board=board())
def test_pseudo_legal_pawn_cant_capture_forwards(board):
    """Test rejection when a pawn tries to capture a piece directly in front of it."""
    game = Game(board)
    start = Square(4, 4)
    end = Square(3, 4)
    board.set_piece(Pawn(Color.WHITE), start)
    board.set_piece(Pawn(Color.BLACK), end)
    move = Move(start, end)

    is_legal, reason = game.is_move_pseudo_legal(move)
    assert is_legal is False
    assert reason == MoveLegalityReason.FORWARD_PAWN_CAPTURE

@given(board=board())
def test_pseudo_legal_pawn_diagonal_requires_capture(board):
    """Test rejection when a pawn moves diagonally without a target (and not en passant)."""
    game = Game(board)
    start = Square(4, 4)
    end = Square(3, 5)
    board.set_piece(Pawn(Color.WHITE), start)
    board.remove_piece(end)
    move = Move(start, end)

    is_legal, reason = game.is_move_pseudo_legal(move)
    assert is_legal is False
    assert reason == MoveLegalityReason.PAWN_DIAGONAL_NON_CAPTURE

@given(board=board())
def test_pseudo_legal_path_is_blocked(board):
    """Test rejection when a sliding piece is blocked by another piece."""
    game = Game(board)
    start = Square(7, 0)
    end = Square(3, 0)
    blocker_sq = Square(5, 0)

    board.set_piece(Rook(Color.WHITE), start)
    board.set_piece(Pawn(Color.WHITE), blocker_sq)
    board.remove_piece(end)
    move = Move(start, end)

    is_legal, reason = game.is_move_pseudo_legal(move)
    assert not is_legal, f"Expected 'Path is blocked'. got {reason}"
    assert reason == MoveLegalityReason.PATH_BLOCKED

    piece = board.get_piece(start)
    assert end not in board.unblocked_paths(piece, piece.theoretical_move_paths(start))

def test_leaving_king_in_check_is_pseudo_legal():
    fen = "k7/r7/8/8/8/8/R7/K7 w - - 0 1"
    game = Game(fen=fen)
    move = Move.from_uci("a2h2")

    assert game.is_move_pseudo_legal(move)[0]

def test_pseudo_legal_en_passant_is_legal():
    """Test that a valid en passant capture is recognized as pseudo-legal."""
    fen = "4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1"
    game = Game(fen=fen)
    move = Move.from_uci("e5d6")

    is_legal, reason = game.is_move_pseudo_legal(move)
    assert is_legal is True, f"En passant move was incorrectly deemed illegal: {reason}"

def test_fen_after_initial_pawn_move():
    """Test that the FEN's en passant field is correctly 'a3' after 1. a4."""
    game = Game()
    move = Move.from_uci("a2a4")
    game.take_turn(move)

    expected_fen = "rnbqkbnr/pppppppp/8/8/P7/8/1PPPPPPP/RNBQKBNR b KQkq a3 0 1"
    assert game.state.fen == expected_fen

def test_en_passant_capture_removes_pawn():
    """Test that an en passant capture correctly removes the captured pawn."""
    fen = "4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1"
    game = Game(fen=fen)
    captured_pawn_square = Square.from_coord('d5')

    assert game.state.board.get_piece(captured_pawn_square) is not None

    move = Move.from_uci("e5d6")
    game.take_turn(move)

    assert game.state.board.get_piece(captured_pawn_square) is None
    assert isinstance(game.state.board.get_piece(Square.from_coord('d6')), Pawn)


def test_en_passant_capture_from_start():
    """Test a specific en passant capture sequence from the starting position."""
    game = Game()

    moves_uci = ["a2a4", "a7a6", "a4a5", "b7b5", "a5b6"]
    for uci in moves_uci:
        move = Move.from_uci(uci)
        game.take_turn(move)

    captured_pawn_square = Square.from_coord('b5')
    assert game.state.board.get_piece(captured_pawn_square) is None

    assert game.state.fen != 'rnbqkbnr/2pppppp/pP6/1p6/8/8/1PPPPPPP/RNBQKBNR b KQkq - 0 3'
    assert isinstance(game.state.board.get_piece(Square.from_coord('b6')), Pawn)
