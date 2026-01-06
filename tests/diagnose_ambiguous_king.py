import sys
import os
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from v_chess.move import Move
from v_chess.game import Game
from v_chess.board import Board
from v_chess.game_state import GameState
from v_chess.enums import Color, CastlingRight

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

    game = Game()

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
                from v_chess.piece.king import King
                from v_chess.square import Square
                from v_chess.enums import Color
                
                king_sq = None
                for sq, piece in game.state.board.items():
                    if isinstance(piece, King) and piece.color == game.state.turn:
                        king_sq = sq
                        break
                
                print(f"King Square: {king_sq}")
                if king_sq:
                    target_sq = Square("c7")
                    is_attacked_by_black_on_original = game.rules.is_under_attack(game.state.board, target_sq, Color.BLACK)
                    print(f"Original board: Is c7 attacked by Black? {is_attacked_by_black_on_original}")

                    if is_attacked_by_black_on_original:
                        for sq, p in game.state.board.items():
                            if p.color == Color.BLACK:
                                if game.rules.is_attacking(game.state.board, p, target_sq, sq):
                                    print(f"Original board Attacker: {p} at {sq}")


                    print("\n--- Simulating king_left_in_check for Kc7 ---")
                    initial_fen = game.state.fen
                    temp_game = Game(initial_fen)

                    try:
                        temp_game.state = temp_game.rules.apply_move(temp_game.state, Move(king_sq, target_sq))
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
                            for sq, p in temp_board.items():
                                if p.color == Color.BLACK:
                                    if temp_game.rules.is_attacking(temp_board, p, sim_king_sq, sq):
                                        print(f"Temp board Attacker: {p} at {sq}")

    return

if __name__ == "__main__":
    diagnose_moves3()