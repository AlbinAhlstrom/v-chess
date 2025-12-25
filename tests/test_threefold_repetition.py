from v_chess.game import Game
from v_chess.move import Move
from v_chess.enums import Color

def test_repetition():
    print("--- Test 3-fold Repetition ---")
    game = Game()
    
    # 1. Nf3 Nf6
    game.take_turn(Move("g1f3"))
    game.take_turn(Move("g8f6"))
    
    # 2. Ng1 Ng8 (Back to start - 2nd occurrence)
    game.take_turn(Move("f3g1"))
    game.take_turn(Move("f6g8"))
    
    # 3. Nf3 Nf6
    game.take_turn(Move("g1f3"))
    game.take_turn(Move("g8f6"))
    
    # 4. Ng1 Ng8 (Back to start - 3rd occurrence)
    game.take_turn(Move("f3g1"))
    game.take_turn(Move("f6g8"))
    
    print(f"Current FEN: {game.state.fen}")
    print(f"Repetitions: {game.repetitions_of_position}")
    print(f"Is Draw? {game.is_draw}")
    
    if game.is_draw:
        print("PASS: Draw detected.")
    else:
        print("FAIL: Draw NOT detected.")

if __name__ == "__main__":
    test_repetition()
