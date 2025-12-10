from dataclasses import dataclass
import pytest

from oop_chess.board import Board
from oop_chess.game import Game
from oop_chess.move import Move

@dataclass
class UCIGame:
    moves: list[Move]
    date: str
    white: str
    black: str
    result: str


game_moves = []

def san_game_to_uci(san_game: str) -> list[str]:
    """Convert a game in san format to a list of uci moves"""
    pass


@pytest.mark.parametrize("moves", game_moves)
def test_pgn_game(moves):
    """
    Tests a single full game by parsing moves and executing them.
    """
    board = Board.starting_setup()
    game = Game(board)
    history = [Move.from_uci(uci) for uci in moves]

    return
    for i, san in enumerate(moves):
        try:
            game.take_turn(move)
        except Exception as e:
            pytest.fail(f"Failed at move {i+1} ('{san}') for game {white_player} vs {black_player}: {e}")
