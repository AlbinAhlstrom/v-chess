import pytest
import random
from .variant_test_utils import load_games_by_variant, run_game_test

by_variant = load_games_by_variant()
koth_games = by_variant.get("kingofthehill", [])
samples = random.sample(koth_games, min(10, len(koth_games)))

@pytest.mark.parametrize("game_data", samples, ids=[f"koth{i+1}" for i in range(len(samples))])
def test_full_game_koth(game_data):
    run_game_test(game_data)