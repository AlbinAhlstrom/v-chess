import pytest
from fastapi.testclient import TestClient
from backend.main import app

def test_create_new_game_from_fen_success(client):
    fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
    response = client.post("/api/game/new", json={"variant": "standard", "fen": fen})
    assert response.status_code == 200
    data = response.json()
    assert data["fen"] == fen
    assert data["turn"] == "w"

def test_create_new_game_from_fen_invalid(client):
    fen = "invalid-fen-string"
    response = client.post("/api/game/new", json={"variant": "standard", "fen": fen})
    assert response.status_code == 400
    assert "Invalid FEN" in response.json()["detail"]

def test_create_new_game_from_fen_antichess(client):
    fen = "8/8/8/8/8/8/p7/R7 w - - 0 1"
    response = client.post("/api/game/new", json={"variant": "antichess", "fen": fen})
    assert response.status_code == 200
    data = response.json()
    assert data["fen"] == fen
