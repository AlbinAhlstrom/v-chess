import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend import database
from backend.database import User, GameModel
import uuid
import json
import asyncio

@pytest.mark.asyncio
async def test_game_result_history_checkmate(client):
    """Test that 1-0 or 0-1 is appended to move history on checkmate."""
    # Create game via API
    resp = client.post("/api/game/new", json={"variant": "standard"})
    game_id = resp.json()["game_id"]
    
    with client.websocket_connect(f"/ws/{game_id}") as ws:
        ws.receive_json() # Initial
        
        # 1. f3 e5 2. g4 Qh4#
        moves = ["f2f3", "e7e5", "g2g4", "d8h4"]
        for uci in moves:
            ws.send_json({"type": "move", "uci": uci})
            
            # Drain until we get the state for this move
            while True:
                msg = ws.receive_json()
                if msg.get("type") == "game_state":
                    if uci == "d8h4":
                        history = msg.get("move_history")
                        if history[-1] == "0-1":
                            assert history[-2].endswith("#")
                            break
                        else: continue 
                    break 

@pytest.mark.asyncio
async def test_game_result_history_resign(client):
    """Test that result is appended on resignation."""
    resp = client.post("/api/game/new", json={"variant": "standard"})
    game_id = resp.json()["game_id"]
    
    with client.websocket_connect(f"/ws/{game_id}") as ws:
        ws.receive_json() # Initial
        
        # Make a move to ensure it's not aborted
        ws.send_json({"type": "move", "uci": "e2e4"})
        
        # Wait for move to be processed
        while True:
            msg = ws.receive_json()
            if msg.get("type") == "game_state" and "e4" in msg.get("move_history", []):
                break

        ws.send_json({"type": "resign"})
        msg = ws.receive_json()
        
        history = msg["move_history"]
        assert history[-1] == "1-0"

@pytest.mark.asyncio
async def test_game_result_history_draw_agreement(client):
    """Test that 1/2-1/2 is appended on draw agreement."""
    resp = client.post("/api/game/new", json={"variant": "standard"})
    game_id = resp.json()["game_id"]
    
    with client.websocket_connect(f"/ws/{game_id}") as ws:
        ws.receive_json() # Initial
        
        # Make a move so it's not empty history (optional but realistic)
        ws.send_json({"type": "move", "uci": "e2e4"})
        ws.receive_json()
        
        # Send draw accept (simulating agreement, as offer just broadcasts)
        ws.send_json({"type": "draw_accept"})
        
        while True:
            msg = ws.receive_json()
            if msg.get("type") == "game_state":
                history = msg.get("move_history")
                if history and history[-1] == "1/2-1/2":
                    break
