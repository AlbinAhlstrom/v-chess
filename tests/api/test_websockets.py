import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_websocket_connection():
    create_res = client.post("/api/game/new", json={"variant": "standard"})
    game_id = create_res.json()["game_id"]

    with client.websocket_connect(f"/ws/{game_id}") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "game_state"
        assert data["status"] == "connected"
        assert data["fen"] == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

def test_websocket_make_move():
    create_res = client.post("/api/game/new", json={"variant": "standard"})
    game_id = create_res.json()["game_id"]
    
    with client.websocket_connect(f"/ws/{game_id}") as websocket:
        # Initial state
        websocket.receive_json()
        
        # Send move e2e4
        websocket.send_json({"type": "move", "uci": "e2e4"})
        
        # Receive update
        data = websocket.receive_json()
        assert data["type"] == "game_state"
        assert data["status"] == "active"
        assert "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1" in data["fen"]
        assert data["turn"] == "b"

def test_websocket_invalid_move_format():
    create_res = client.post("/api/game/new", json={"variant": "standard"})
    game_id = create_res.json()["game_id"]

    with client.websocket_connect(f"/ws/{game_id}") as websocket:
        websocket.receive_json()

        # Send garbage
        websocket.send_json({"type": "move", "uci": "garbage"})

        data = websocket.receive_json()
        assert data["type"] == "error"
        # ValueError from Move init

def test_websocket_illegal_move_logic():
    create_res = client.post("/api/game/new", json={"variant": "standard"})
    game_id = create_res.json()["game_id"]

    with client.websocket_connect(f"/ws/{game_id}") as websocket:
        websocket.receive_json()

        # Send illegal move (pawn jump)
        websocket.send_json({"type": "move", "uci": "e2e5"})

        data = websocket.receive_json()
        assert data["type"] == "error"
        # IllegalMoveException

def test_websocket_undo_move():
    create_res = client.post("/api/game/new", json={"variant": "standard"})
    game_id = create_res.json()["game_id"]

    with client.websocket_connect(f"/ws/{game_id}") as websocket:
        websocket.receive_json()

        # Move
        websocket.send_json({"type": "move", "uci": "e2e4"})
        websocket.receive_json()

        # Undo
        websocket.send_json({"type": "undo"})

        data = websocket.receive_json()
        assert data["type"] == "game_state"
        assert data["fen"] == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

def test_websocket_checkmate_status():
    # Setup Fool's Mate sequence
    create_res = client.post("/api/game/new", json={"variant": "standard"})
    game_id = create_res.json()["game_id"]

    moves = ["f2f3", "e7e5", "g2g4", "d8h4"]

    with client.websocket_connect(f"/ws/{game_id}") as websocket:
        websocket.receive_json()

        for m in moves:
            websocket.send_json({"type": "move", "uci": m})
            data = websocket.receive_json()

        # Last update should be checkmate
        assert data["status"] == "checkmate"
        assert data["is_over"] is True
