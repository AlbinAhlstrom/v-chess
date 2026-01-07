import pytest
import random
from .variant_test_utils import load_games_by_variant, run_game_test

by_variant = load_games_by_variant()
crazyhouse_games = by_variant.get("crazyhouse", [])
samples = random.sample(crazyhouse_games, min(10, len(crazyhouse_games)))

@pytest.mark.parametrize("game_data", samples, ids=[f"crazyhouse{i+1}" for i in range(len(samples))])
def test_full_game_crazyhouse(game_data):
    run_game_test(game_data)