import pytest
from fastapi.testclient import TestClient
from backend.main import app

def test_create_new_game_standard(client):
    response = client.post("/api/game/new", json={"variant": "standard"})
    assert response.status_code == 200
    data = response.json()
    assert "game_id" in data
    assert "fen" in data
    assert data["turn"] == "w"
    assert data["fen"] == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

def test_create_new_game_antichess(client):
    response = client.post("/api/game/new", json={"variant": "antichess"})
    assert response.status_code == 200
    data = response.json()
    assert "game_id" in data
    # Antichess standard start is same FEN, but logic differs.
    # We can't verify logic via this endpoint output alone, but success is good.

def test_get_legal_moves_valid_square(client):
    # Create game
    create_res = client.post("/api/game/new", json={"variant": "standard"})
    game_id = create_res.json()["game_id"]
    
    # Get moves for e2 (white pawn)
    response = client.post("/api/moves/legal", json={"game_id": game_id, "square": "e2"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "e2e3" in data["moves"]
    assert "e2e4" in data["moves"]

def test_get_legal_moves_empty_square(client):
    create_res = client.post("/api/game/new", json={"variant": "standard"})
    game_id = create_res.json()["game_id"]
    
    response = client.post("/api/moves/legal", json={"game_id": game_id, "square": "e4"})
    assert response.status_code == 200
    data = response.json()
    assert data["moves"] == []

def test_get_legal_moves_opponent_piece(client):
    create_res = client.post("/api/game/new", json={"variant": "standard"})
    game_id = create_res.json()["game_id"]
    
    # White to move, check Black pawn at e7
    response = client.post("/api/moves/legal", json={"game_id": game_id, "square": "e7"})
    # Expect 400 or empty? Check main.py.
    # main.py: raise HTTPException(status_code=400, detail=f"Piece belongs to the opponent...")
    assert response.status_code == 400
    assert "Piece belongs to the opponent" in response.json()["detail"]

def test_get_legal_moves_invalid_game_id(client):
    response = client.post("/api/moves/legal", json={"game_id": "bad-id", "square": "e2"})
    assert response.status_code == 404

def test_get_all_legal_moves(client):
    create_res = client.post("/api/game/new", json={"variant": "standard"})
    game_id = create_res.json()["game_id"]
    
    response = client.post("/api/moves/all_legal", json={"game_id": game_id})
    assert response.status_code == 200
    data = response.json()
    assert len(data["moves"]) == 20 # 16 pawn moves + 4 knight moves
    assert "e2e4" in data["moves"]
