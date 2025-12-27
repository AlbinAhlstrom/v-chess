import pytest
import re
from playwright.sync_api import Page, expect

def move_piece(page: Page, start_sq: str, end_sq: str):
    start_selector = f"div.piece[data-square='{start_sq}']"
    end_selector = f".squares div[data-square='{end_sq}']"
    page.wait_for_selector(start_selector, timeout=10000)
    page.wait_for_selector(end_selector, timeout=10000)
    start_box = page.locator(start_selector).bounding_box()
    end_box = page.locator(end_selector).bounding_box()
    page.mouse.move(start_box["x"] + start_box["width"] / 2, start_box["y"] + start_box["height"] / 2)
    page.mouse.down()
    page.mouse.move(end_box["x"] + end_box["width"] / 2, end_box["y"] + end_box["height"] / 2, steps=5)
    page.mouse.up()
    page.wait_for_selector(f"div.piece[data-square='{end_sq}']", timeout=10000)

def test_history_navigation_ui(page: Page, frontend_url: str):
    # page.set_viewport_size({"width": 375, "height": 667})
    print(f"Navigating to {frontend_url}/otb")
    page.goto(f"{frontend_url}/otb", timeout=60000)
    
    # Wait for board instead of URL redirect
    print("Waiting for board to load...")
    try:
        page.wait_for_selector(".board", timeout=30000)
    except Exception as e:
        page.screenshot(path="nav_fail.png")
        print(f"Current URL: {page.url}")
        raise e
    
    # 1. Make some moves
    print("Making moves...")
    move_piece(page, "e2", "e4")
    page.wait_for_timeout(500)
    move_piece(page, "e7", "e5")
    page.wait_for_timeout(500)
    
    # 2. Check history bar items
    print("Checking history items...")
    history_bar = page.locator(".mobile-history-scroll")
    expect(history_bar).to_be_visible()
    items = history_bar.locator(".history-item")
    expect(items).to_have_count(3)
    
    # 3. Go back to Start
    print("Navigating back to Start...")
    items.nth(0).click()
    page.wait_for_timeout(500)
    expect(page.locator("div.piece[data-square='e2']")).to_be_visible()
    
    # 4. Verify board is disabled
    print("Verifying board is disabled...")
    board = page.locator(".board")
    expect(board).to_have_css("pointer-events", "none")
    
    # 5. Use navigation buttons
    print("Testing navigation buttons...")
    next_btn = page.locator("button[title='Next']")
    next_btn.click()
    page.wait_for_timeout(500)
    expect(page.locator("div.piece[data-square='e4']")).to_be_visible()
    
    # 6. Go to latest
    print("Returning to latest...")
    items.nth(2).click() # e5
    page.wait_for_timeout(500)
    expect(board).to_have_css("pointer-events", "auto")
    
    # 7. Make another move
    print("Making another move...")
    move_piece(page, "g1", "f3")
    expect(items).to_have_count(4)