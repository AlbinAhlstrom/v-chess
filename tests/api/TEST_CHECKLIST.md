# API Test Checklist

This checklist tracks tests for the FastAPI backend (`backend/main.py`), ensuring the API endpoints and WebSocket communication work as expected.

## HTTP Endpoints
- [ ] **Create New Game (`POST /api/game/new`)**:
    - [ ] Verify success response (game_id, fen, turn).
    - [ ] Verify standard variant initialization.
    - [ ] Verify antichess variant initialization.
- [ ] **Get Legal Moves (`POST /api/moves/legal`)**:
    - [ ] Verify valid square returns moves.
    - [ ] Verify empty square returns empty list.
    - [ ] Verify opponent piece returns error/empty.
    - [ ] Verify invalid square format returns 400.
    - [ ] Verify non-existent game ID returns 404.
- [ ] **Get All Legal Moves (`POST /api/moves/all_legal`)**:
    - [ ] Verify returns list of all UCI moves.

## WebSocket Communication (`/ws/{game_id}`)
- [ ] **Connection**:
    - [ ] Verify successful connection receives initial `game_state`.
    - [ ] Verify connecting to invalid game_id closes connection/returns error.
- [ ] **Making Moves**:
    - [ ] Send valid move (UCI), receive updated `game_state`.
    - [ ] Send invalid move, receive error message.
    - [ ] Send illegal move (rule violation), receive error message.
- [ ] **Undo Moves**:
    - [ ] Send undo command, receive previous `game_state`.
- [ ] **Game End States**:
    - [ ] Checkmate triggers status update in broadcast.
    - [ ] Draw triggers status update.
