import pytest
import os
import subprocess
import time
import uuid
import socket
import sys
import shutil
from playwright.sync_api import Page

def wait_for_port(port, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("localhost", port)) == 0:
                return True
        time.sleep(0.5)
    return False

@pytest.fixture(scope="session", autouse=True)
def e2e_environment(tmp_path_factory):
    """
    Sets up the full E2E environment:
    1. Creates a temporary test database.
    2. Starts the Backend (FastAPI).
    3. Starts the Frontend (React).
    4. Cleans up everything after tests finish.
    """
    # 1. Database Setup
    temp_dir = tmp_path_factory.mktemp("e2e_db")
    test_db_file = str(temp_dir / "chess.db")
    db_url = f"sqlite+aiosqlite:///{test_db_file}"
    os.environ["DATABASE_URL"] = db_url
    print(f"\n[E2E Setup] Using temporary DB: {test_db_file}")

    # Paths
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    frontend_dir = os.path.join(root_dir, "frontend")
    
    # 2. Start Backend
    print("[E2E Setup] Starting Backend on port 8000...")
    # Ensure we use the same python interpreter (virtualenv)
    # Add --reload to ensure code changes are picked up automatically
    backend_cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--port", "8000", "--reload"]
    
    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=root_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "DATABASE_URL": db_url}  # Pass the env explicitly
    )

    if not wait_for_port(8000):
        print("[E2E Error] Backend failed to start!")
        backend_proc.terminate()
        stdout, stderr = backend_proc.communicate()
        print(f"Backend STDOUT: {stdout.decode()}")
        print(f"Backend STDERR: {stderr.decode()}")
        # DB file is in temp dir, pytest handles cleanup
        pytest.fail("Backend failed to start on port 8000")

    # 3. Start Frontend
    print("[E2E Setup] Starting Frontend on port 3000...")
    # Set BROWSER=none to prevent opening a tab
    frontend_env = {**os.environ, "BROWSER": "none"}
    frontend_proc = subprocess.Popen(
        ["npm", "start"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=frontend_env
    )

    if not wait_for_port(3000, timeout=60): # React startup can be slow
        print("[E2E Error] Frontend failed to start!")
        frontend_proc.terminate()
        backend_proc.terminate()
        stdout, stderr = frontend_proc.communicate()
        print(f"Frontend STDOUT: {stdout.decode()}")
        print(f"Frontend STDERR: {stderr.decode()}")
        # DB file is in temp dir, pytest handles cleanup
        pytest.fail("Frontend failed to start on port 3000")

    print("[E2E Setup] Environment Ready!")
    
    yield

    # 4. Teardown
    print("\n[E2E Teardown] Stopping servers and cleaning up...")
    
    # Terminate Frontend
    frontend_proc.terminate()
    try:
        frontend_proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        frontend_proc.kill()
        
    # Terminate Backend
    backend_proc.terminate()
    try:
        backend_proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        backend_proc.kill()

    # DB cleanup handled by pytest tmp_path_factory

@pytest.fixture
def frontend_url():
    # Always point to the local instance managed by e2e_environment
    return "http://localhost:3000"

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "args": ["--disable-web-security"]
    }

@pytest.fixture(autouse=True)
def set_default_timeout(page: Page):
    page.set_default_timeout(5000)
    yield