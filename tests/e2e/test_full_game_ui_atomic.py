import pytest
from playwright.sync_api import Page
from .variant_ui_test_utils import load_variant_samples, run_variant_ui_game

samples = load_variant_samples("atomic", count=2)

@pytest.mark.parametrize("game_data", samples, ids=[f"atomic{i+1}" for i in range(len(samples))])
def test_full_game_ui_atomic(page: Page, frontend_url: str, game_data):
    run_variant_ui_game(page, frontend_url, game_data)
