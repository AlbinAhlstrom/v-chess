import pytest
from v_chess.game import Game, IllegalMoveException
from v_chess.move import Move

def test_take_turn_raises_illegal_move():
    """Verify take_turn raises exception for illegal moves."""
    game = Game()
    move = Move("e2e5") # Illegal pawn move
    
    with pytest.raises(IllegalMoveException):
        game.take_turn(move)

def test_take_turn_executes_legal_move():
    """Verify take_turn executes a legal move without error."""
    game = Game()
    move = Move("e2e4", player_to_move=game.state.turn)
    
    try:
        game.take_turn(move)
    except IllegalMoveException:
        pytest.fail("take_turn raised IllegalMoveException for a legal move")

def test_legal_moves_returns_correct_list():
    """Verify legal_moves returns correct list from Rules."""
    game = Game("8/8/8/8/8/8/8/k6K w - - 0 1")
    moves = [m.uci for m in game.legal_moves]
    
    expected = ["h1g1", "h1h2", "h1g2"]
    assert set(moves) == set(expected)

def test_san_generation_normal():
    """Verify SAN generation for normal moves."""
    game = Game()
    move = Move("g1f3")
    assert move.get_san(game) == "Nf3"

def test_san_generation_check():
    """Verify SAN includes check indicator (+)."""
    game = Game("rnbqkbnr/ppp2ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")
    game.take_turn(Move("f1b5", player_to_move=game.state.turn)) # check
    
    assert game.move_history[-1] == "Bb5+"

def test_san_generation_capture():
    """Verify SAN includes capture indicator (x)."""
    game = Game("rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2")
    move = Move("f3e5", player_to_move=game.state.turn) # capture
    assert move.get_san(game) == "Nxe5"

def test_san_generation_ambiguous_knight():
    """Verify SAN handles ambiguity."""
    game = Game("7k/8/8/8/8/2N1N3/8/K7 w - - 0 1")
    move = Move("c3d5", player_to_move=game.state.turn)
    assert move.get_san(game) == "Ncd5"
