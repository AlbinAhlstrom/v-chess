import pytest
import random
from .variant_test_utils import load_games_by_variant, run_game_test

by_variant = load_games_by_variant()
threecheck_games = by_variant.get("threecheck", [])
samples = random.sample(threecheck_games, min(10, len(threecheck_games)))

@pytest.mark.parametrize("game_data", samples, ids=[f"threecheck{i+1}" for i in range(len(samples))])
def test_full_game_three_check(game_data):
    run_game_test(game_data)