import pytest
import random
from .variant_test_utils import load_games_by_variant, run_game_test

by_variant = load_games_by_variant()
atomic_games = by_variant.get("atomic", [])
samples = random.sample(atomic_games, min(10, len(atomic_games)))

@pytest.mark.parametrize("game_data", samples, ids=[f"atomic{i+1}" for i in range(len(samples))])
def test_full_game_atomic(game_data):
    run_game_test(game_data)