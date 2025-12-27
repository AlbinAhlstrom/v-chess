import pytest
from backend.main import app
from fastapi.testclient import TestClient
from backend.database import async_session, User, GameModel
from sqlalchemy import select
import uuid
import datetime
import json

@pytest.mark.asyncio
async def test_game_history(client):
    # Manually insert a user and games
    user_id = str(uuid.uuid4())
    
    async with async_session() as session:
        async with session.begin():
            u = User(google_id=user_id, email=f"test_{user_id}@test.com", name="Test User", username=f"user_{user_id[:8]}")
            session.add(u)
            
            # Game 1: Win (White), Standard
            g1 = GameModel(
                id=str(uuid.uuid4()),
                variant="standard",
                fen="start_fen",
                move_history="[]",
                white_player_id=user_id,
                black_player_id="computer",
                is_over=True,
                winner="white",
                created_at=datetime.datetime.now()
            )
            session.add(g1)
            
            # Game 2: Loss (Black), Atomic (Winner is White -> User is Black -> Loss)
            g2 = GameModel(
                id=str(uuid.uuid4()),
                variant="atomic",
                fen="start_fen",
                move_history="[]",
                white_player_id="computer",
                black_player_id=user_id,
                is_over=True,
                winner="white",
                created_at=datetime.datetime.now()
            )
            session.add(g2)
            
            # Game 3: Draw, Standard
            g3 = GameModel(
                id=str(uuid.uuid4()),
                variant="standard",
                fen="start_fen",
                move_history="[]",
                white_player_id=user_id,
                black_player_id="other_user",
                is_over=True,
                winner="draw",
                created_at=datetime.datetime.now()
            )
            session.add(g3)

    # Test Fetch All
    resp = client.get(f"/api/user/{user_id}/games")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["games"]) == 3
    
    # Test Filter Variant Standard
    resp = client.get(f"/api/user/{user_id}/games?variant=standard")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["games"]) == 2
    for g in data["games"]:
        assert g["variant"] == "standard"
        
    # Test Filter Result Win
    resp = client.get(f"/api/user/{user_id}/games?result=win")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["games"]) == 1
    assert data["games"][0]["result"] == "win"
    
    # Test Filter Result Loss
    resp = client.get(f"/api/user/{user_id}/games?result=loss")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["games"]) == 1
    assert data["games"][0]["result"] == "loss"
