import sys
import os
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from oop_chess.move import Move
from oop_chess.game import Game
from oop_chess.board import Board
from oop_chess.game_state import GameState
from oop_chess.enums import Color, CastlingRight

def parse_moves(game_string):
    moves_section = game_string.split('\n\n')[-1]
    moves_section = re.sub(r'\{[^}]*\}', '', moves_section)
    moves_section = re.sub(r'\d+\.\s*', '', moves_section)
    moves_section = re.sub(r'(0-1|1-0|1/2-1/2)\s*$', '', moves_section).strip()
    return [move for move in moves_section.split() if move]




def diagnose_moves3():
    print("--- Diagnosing moves3 Failure ---")
    pgn_path = "tests/example_games.pgn"
    with open(pgn_path, "r") as f:
        pgn_content = f.read()

    game_strings = re.split(r'\n\n(?=\[Event)', pgn_content.strip())

    if len(game_strings) <= 3:
        print("Error: Could not find game index 3.")
        return

    game_string = game_strings[3]
    moves = parse_moves(game_string)

    print(f"Game 3 Moves: {moves}")

    board = Board.starting_setup()
    state = GameState(
        board=board,
        turn=Color.WHITE,
        castling_rights=(CastlingRight.WHITE_SHORT, CastlingRight.WHITE_LONG, CastlingRight.BLACK_SHORT, CastlingRight.BLACK_LONG),
        ep_square=None,
        halfmove_clock=0,
        fullmove_count=1
    )
    game = Game(state)

    print("\nExecuting moves...")
    for i, san in enumerate(moves):
        print(f"{i+1}. {san}")
        try:
            move = Move.from_san(san, game)
            game.take_turn(move)
        except Exception as e:
            print(f"FAILED at move {i+1} ({san}): {e}")
            print(f"Current FEN: {game.state.fen}")
            print(f"Player to move: {game.state.turn}")

            if "Kc7" in san:
                from oop_chess.piece.king import King
                from oop_chess.square import Square
                from oop_chess.enums import Color
                pieces = game.state.board.get_pieces(King, game.state.turn)
                print(f"King found: {pieces}")
                if pieces:
                    king = pieces[0]
                    print(f"King Square: {king.square}")

                    target_sq = Square("c7")
                    is_attacked_by_black_on_original = game.rules.is_under_attack(game.state.board, target_sq, Color.BLACK)
                    print(f"Original board: Is c7 attacked by Black? {is_attacked_by_black_on_original}")

                    if is_attacked_by_black_on_original:
                        black_pieces_original = game.state.board.get_pieces(color=Color.BLACK)
                        for p in black_pieces_original:
                            if p.square is not None and game.rules.is_attacking(game.state.board, p, target_sq, p.square):
                                print(f"Original board Attacker: {p} at {p.square}")


                    print("\n--- Simulating king_left_in_check for Kc7 ---")
                    initial_fen = game.state.fen
                    temp_game = Game(initial_fen)

                    try:
                        temp_game.state = temp_game.rules.apply_move(temp_game.state, Move(king.square, target_sq))
                        temp_board = temp_game.state.board
                    except Exception as e:
                        print(f"Could not apply move on temp board: {e}")

                    print(f"Temp board FEN after Kc7: {temp_game.state.fen}")

                    is_check_on_temp_board = temp_game.rules.inactive_player_in_check(temp_game.state)
                    print(f"Temp board: inactive_player_in_check (White in check)? {is_check_on_temp_board}")

                    if is_check_on_temp_board:
                        sim_king_sq = target_sq
                        is_attacked_on_temp = temp_game.rules.is_under_attack(temp_board, sim_king_sq, Color.BLACK)
                        print(f"Temp board: Is c7 attacked by Black (after move)? {is_attacked_on_temp}")
                        if is_attacked_on_temp:
                            black_pieces_temp = temp_board.get_pieces(color=Color.BLACK)
                            for p in black_pieces_temp:
                                if p.square is not None and temp_game.rules.is_attacking(temp_board, p, sim_king_sq, p.square):
                                    print(f"Temp board Attacker: {p} at {p.square}")





    assert game.state.fen == initial_fen



    print(f"King Theoretical Moves: {king.theoretical_moves}")

    print(f"King Legal Moves: {[m.uci for m in game.legal_moves if m.start == king.square]}")





    print("\n--- Diagnosing King theoretical_moves ---")

    isolated_king_board = Board.empty()

    test_king = King(Color.BLACK)

    a7_square = Square("a7")

    c7_square = Square("c7")

    isolated_king_board.set_piece(test_king, a7_square)





    test_king.square = a7_square



    king_theoretical_moves = test_king.theoretical_moves

    print(f"Theoretical moves for King at a7: {king_theoretical_moves}")



    if c7_square in king_theoretical_moves:

        print(f"CRITICAL BUG: King at a7 incorrectly includes {c7_square} in theoretical_moves!")

    else:

        print(f"King at a7 correctly does NOT include {c7_square} in theoretical_moves.")



        print("\n-----------------------------------------")



        return
if __name__ == "__main__":
    diagnose_moves3()
