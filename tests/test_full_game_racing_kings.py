import pytest
import random
from .variant_test_utils import load_games_by_variant, run_game_test

by_variant = load_games_by_variant()
racingkings_games = by_variant.get("racingkings", [])
samples = random.sample(racingkings_games, min(10, len(racingkings_games)))

@pytest.mark.parametrize("game_data", samples, ids=[f"racingkings{i+1}" for i in range(len(samples))])
def test_full_game_racing_kings(game_data):
    run_game_test(game_data)