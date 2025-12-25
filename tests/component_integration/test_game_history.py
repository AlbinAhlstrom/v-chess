from v_chess.game import Game
from v_chess.move import Move

def test_undo_restores_previous_state():
    """Verify undo_move restores previous GameState."""
    game = Game()
    initial_fen = game.state.fen

    game.take_turn(Move("e2e4"))
    assert game.state.fen != initial_fen

    game.undo_move()
    assert game.state.fen == initial_fen
    assert game.state.turn.value == "w"

def test_repetitions_counts_accurately():
    """Verify repetitions_of_position counts accurately based on history."""
    game = Game()
    # 1
    game.take_turn(Move("g1f3", player_to_move=game.state.turn))
    game.take_turn(Move("g8f6", player_to_move=game.state.turn))
    # 2
    game.take_turn(Move("f3g1", player_to_move=game.state.turn))
    game.take_turn(Move("f6g8", player_to_move=game.state.turn))

    assert game.repetitions_of_position == 2

    # 3
    game.take_turn(Move("g1f3", player_to_move=game.state.turn))
    game.take_turn(Move("g8f6", player_to_move=game.state.turn))

    assert game.repetitions_of_position == 2

    # 4
    game.take_turn(Move("f3g1", player_to_move=game.state.turn))
    game.take_turn(Move("f6g8", player_to_move=game.state.turn))

    assert game.repetitions_of_position == 3
