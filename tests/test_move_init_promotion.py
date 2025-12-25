from v_chess.move import Move
from v_chess.enums import Color

def test_move_init_promotion():
    print("--- Test Move Initialization with Promotion ---")
    
    uci = "a7a8q"
    print(f"Initializing Move from UCI: '{uci}'")
    
    try:
        move = Move(uci, player_to_move=Color.WHITE)
        print(f"Move object: {move}")
        print(f"Promotion Piece: {move.promotion_piece}")
        
        if move.promotion_piece is None:
            print("FAIL: Promotion piece is None!")
        else:
            print(f"PASS: Promotion piece is {move.promotion_piece}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_move_init_promotion()
