import pytest
import random
from .variant_test_utils import load_games_by_variant, run_game_test

by_variant = load_games_by_variant()
antichess_games = by_variant.get("antichess", [])
samples = random.sample(antichess_games, min(10, len(antichess_games)))

@pytest.mark.parametrize("game_data", samples, ids=[f"antichess{i+1}" for i in range(len(samples))])
def test_full_game_antichess(game_data):
    run_game_test(game_data)