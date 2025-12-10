from dataclasses import dataclass
import pytest

from oop_chess.board import Board
from oop_chess.game import Game
from oop_chess.move import Move
import chess.pgn

@dataclass
class UCIGame:
    moves: list[Move]
    date: str
    white: str
    black: str
    result: str

with open("./example_games.pgn")
game_san_string = 


def san_game_to_uci(san_game: str) -> list[str]:
    """Convert a game in san format to a list of uci moves"""


@pytest.mark.parametrize("moves", game_moves)
def test_pgn_game(moves):
    """
    Tests a single full game by parsing moves and executing them.
    """
    board = Board.starting_setup()
    game = Game(board)
    imported_moves = 
    history = [Move.from_uci(uci) for uci in imported_moves]

    for i, san in enumerate(moves):
        try:
            move = interpreter.get_move(san)
            game.take_turn(move)
        except Exception as e:
            pytest.fail(f"Failed at move {i+1} ('{san}') for game {white_player} vs {black_player}: {e}")
