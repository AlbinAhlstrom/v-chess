import pytest
import random
from .variant_test_utils import load_games_by_variant, run_game_test

by_variant = load_games_by_variant()
horde_games = by_variant.get("horde", [])
samples = random.sample(horde_games, min(10, len(horde_games)))

@pytest.mark.parametrize("game_data", samples, ids=[f"horde{i+1}" for i in range(len(samples))])
def test_full_game_horde(game_data):
    run_game_test(game_data)