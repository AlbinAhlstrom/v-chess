import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import time

def move_piece(driver, start_sq, end_sq):
    start_selector = f"div.piece[data-square='{start_sq}']"
    end_selector = f".squares div[data-square='{end_sq}']"
    
    try:
        # Wait for piece to be interactable
        piece = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, start_selector))
        )
        target = driver.find_element(By.CSS_SELECTOR, end_selector)
        
        # Perform drag and drop
        action = ActionChains(driver)
        action.click_and_hold(piece).move_to_element(target).release().perform()
        
        # Wait for piece to appear at destination
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"div.piece[data-square='{end_sq}']"))
        )
    except Exception as e:
        print(f"Failed to move {start_sq} to {end_sq}: {e}")
        driver.save_screenshot(f"move_fail_{start_sq}_{end_sq}.png")
        raise e

def test_full_game_ui(driver, frontend_url):
    print(f"Navigating to {frontend_url}/otb")
    driver.get(f"{frontend_url}/otb")
    
    # Wait for game initialization
    WebDriverWait(driver, 10).until(EC.url_contains("/game/"))
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "board"))
    )
    
    # Fool's Mate Sequence
    moves = [
        ("f2", "f3"),
        ("e7", "e5"),
        ("g2", "g4"),
        ("d8", "h4")
    ]
    
    for start, end in moves:
        move_piece(driver, start, end)
        time.sleep(0.5) 
        
    # Verify result in history
    # We look for "0-1" text in the history container
    WebDriverWait(driver, 5).until(
        lambda d: "0-1" in d.find_element(By.CLASS_NAME, "move-history").text
    )
    
    history_text = driver.find_element(By.CLASS_NAME, "move-history").text
    assert "0-1" in history_text

def test_resignation_ui(driver, frontend_url):
    print(f"Navigating to {frontend_url}/otb")
    driver.get(f"{frontend_url}/otb")
    
    WebDriverWait(driver, 10).until(EC.url_contains("/game/"))
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "board"))
    )
    
    # White resigns immediately
    resign_btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='Surrender']"))
    )
    resign_btn.click()
    
    # Verify result in history (0-1 because White resigned)
    WebDriverWait(driver, 5).until(
        lambda d: "0-1" in d.find_element(By.CLASS_NAME, "move-history").text
    )
    
    history_text = driver.find_element(By.CLASS_NAME, "move-history").text
    assert "0-1" in history_text
