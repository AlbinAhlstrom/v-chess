import pytest
import json
import uuid

def drain_messages(ws, count):
    msgs = []
    for _ in range(count):
        msgs.append(ws.receive_json())
    return msgs

def find_message(msgs, type_name):
    for m in msgs:
        if m.get("type") == type_name:
            return m
    return None

@pytest.mark.asyncio
async def test_takeback_flow(client):
    """Test takeback offer and acceptance."""
    resp = client.post("/api/game/new", json={"variant": "standard"})
    game_id = resp.json()["game_id"]
    
    with client.websocket_connect(f"/ws/{game_id}") as ws1:
        with client.websocket_connect(f"/ws/{game_id}") as ws2:
            # Drain connection messages
            # ws1 gets 2 (own + ws2's), ws2 gets 1
            drain_messages(ws1, 2)
            drain_messages(ws2, 1)
            
            # Make a move (ws1)
            ws1.send_json({"type": "move", "uci": "e2e4"})
            
            # Both get: takeback_cleared, draw_cleared, game_state (order might vary in some envs but let's assume rapid)
            # Actually order is deterministic in backend. 
            # But let's just drain 3 and check content.
            msgs1 = drain_messages(ws1, 3)
            msgs2 = drain_messages(ws2, 3)
            assert find_message(msgs1, "takeback_cleared")
            assert find_message(msgs1, "game_state")
            
            # Offer takeback (ws1)
            ws1.send_json({"type": "takeback_offer"})
            msg1 = ws1.receive_json()
            msg2 = ws2.receive_json()
            assert msg1["type"] == "takeback_offered"
            
            # Accept takeback (ws2)
            ws2.send_json({"type": "takeback_accept"})
            
            # Both get: takeback_cleared, game_state
            msgs1 = drain_messages(ws1, 2)
            msgs2 = drain_messages(ws2, 2)
            
            state = find_message(msgs1, "game_state")
            assert state["status"] == "takeback_accepted"
            assert len(state["move_history"]) == 0

@pytest.mark.asyncio
async def test_draw_agreement_flow(client):
    """Test draw offer and acceptance."""
    resp = client.post("/api/game/new", json={"variant": "standard"})
    game_id = resp.json()["game_id"]
    
    with client.websocket_connect(f"/ws/{game_id}") as ws1:
        with client.websocket_connect(f"/ws/{game_id}") as ws2:
            drain_messages(ws1, 2)
            drain_messages(ws2, 1)
            
            # Offer draw (ws1)
            ws1.send_json({"type": "draw_offer"})
            msg1 = ws1.receive_json()
            assert msg1["type"] == "draw_offered"
            
            # Accept draw (ws2)
            ws2.send_json({"type": "draw_accept"})
            
            msg1 = ws1.receive_json()
            assert msg1["type"] == "game_state"
            assert msg1["is_over"] == True
            assert msg1["winner"] == "draw"
            assert msg1["move_history"][-1] == "1/2-1/2"
