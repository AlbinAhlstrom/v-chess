import re
from dataclasses import dataclass
import pytest

from v_chess.game import Game
from v_chess.move import Move


@dataclass
class PGNGame:
    moves: list[str]
    date: str
    white: str
    black: str
    result: str


def parse_pgn_game(game_string: str) -> PGNGame:
    date_match = re.search(r'\[Date "(\d{4}\.\d{2}\.\d{2})"\]', game_string)
    white_match = re.search(r'\[White "(.*?)"\]', game_string)
    black_match = re.search(r'\[Black "(.*?)"\]', game_string)
    result_match = re.search(r'\[Result "(.*?)"\]', game_string)

    date = date_match.group(1) if date_match else "N/A"
    white = white_match.group(1) if white_match else "N/A"
    black = black_match.group(1) if black_match else "N/A"
    result = result_match.group(1) if result_match else "N/A"

    moves_section = game_string.split('\n\n')[-1]
    moves_section = re.sub(r'\{[^}]*\}', '', moves_section)
    moves_section = re.sub(r'\d+\.\s*', '', moves_section)
    moves_section = re.sub(r'(0-1|1-0|1/2-1/2)\s*$', '', moves_section).strip()

    san_moves = [move for move in moves_section.split() if move]

    return PGNGame(moves=san_moves, date=date, white=white, black=black, result=result)


all_games: list[PGNGame] = []
import os
pgn_path = os.path.join(os.path.dirname(__file__), "example_games.pgn")
with open(pgn_path, "r") as f:
    pgn_content = f.read()

game_strings = re.split(r'\n\n(?=\[Event)', pgn_content.strip())


for game_string in game_strings:
    if game_string.strip():
        all_games.append(parse_pgn_game(game_string))

game_moves = [game.moves for game in all_games]

@pytest.mark.parametrize("moves", game_moves)
def test_pgn_game(moves):
    """
    Tests a single full game by parsing moves and executing them.
    """

    game = Game()
    history = []
    for san_move_str in moves:
        move = Move.from_san(san_move_str, game)
        game.take_turn(move)
        history.append(move)
    pass
