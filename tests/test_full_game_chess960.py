import pytest
import random
from .variant_test_utils import load_games_by_variant, run_game_test

by_variant = load_games_by_variant()
chess960_games = by_variant.get("chess960", [])
samples = random.sample(chess960_games, min(10, len(chess960_games)))

@pytest.mark.parametrize("game_data", samples, ids=[f"chess960_{i+1}" for i in range(len(samples))])
def test_full_game_chess960(game_data):
    run_game_test(game_data)