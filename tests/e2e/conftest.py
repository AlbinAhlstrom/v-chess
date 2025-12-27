import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import os

@pytest.fixture(scope="session")
def driver():
    chrome_options = Options()
    if os.environ.get("HEADLESS", "false").lower() == "true":
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Set a fixed window size to ensure elements are visible
    chrome_options.add_argument("--window-size=1280,720")

    service = Service(ChromeDriverManager().install())
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        pytest.skip(f"Could not initialize Selenium driver: {e}")
    
    yield driver
    
    driver.quit()

@pytest.fixture
def frontend_url():
    # Allow override via env var, default to local dev server
    return os.environ.get("FRONTEND_URL", "http://localhost:3000")
