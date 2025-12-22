from uuid import uuid4
from typing import Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

from oop_chess.game import Game, IllegalMoveException
from oop_chess.move import Move
from oop_chess.square import Square
from oop_chess.rules import (
    AntichessRules, StandardRules, AtomicRules, Chess960Rules,
    CrazyhouseRules, HordeRules, KingOfTheHillRules, RacingKingsRules,
    ThreeCheckRules
)


app = FastAPI()

origins = [
    "https://v-chess.com",
    "https://www.v-chess.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


games: dict[str, Game] = {}


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, game_id: str):
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)

    def disconnect(self, websocket: WebSocket, game_id: str):
        if game_id in self.active_connections:
            self.active_connections[game_id].remove(websocket)

    async def broadcast(self, game_id: str, message: str):
        if game_id in self.active_connections:
            for connection in self.active_connections[game_id]:
                await connection.send_text(message)


manager = ConnectionManager()


def get_game(game_id: str) -> Game:
    if game_id not in games:
        raise HTTPException(status_code=404, detail=f"Game ID '{game_id}' not found.")
    return games[game_id]


class MoveRequest(BaseModel):
    move_uci: str


class GameRequest(BaseModel):
    game_id: str


class SquareRequest(BaseModel):
    game_id: str
    square: str


class SquareSelection(BaseModel):
    square: str


class NewGameRequest(BaseModel):
    variant: str = "standard"
    fen: Optional[str] = None
    time_control: Optional[dict] = None


@app.post("/api/game/new")
def new_game(req: NewGameRequest):
    game_id = str(uuid4())

    rules_map = {
        "standard": StandardRules,
        "antichess": AntichessRules,
        "atomic": AtomicRules,
        "chess960": Chess960Rules,
        "crazyhouse": CrazyhouseRules,
        "horde": HordeRules,
        "kingofthehill": KingOfTheHillRules,
        "racingkings": RacingKingsRules,
        "threecheck": ThreeCheckRules,
    }

    rules_cls = rules_map.get(req.variant.lower(), StandardRules)
    rules = rules_cls()

    try:
        game = Game(state=req.fen, rules=rules, time_control=req.time_control)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid FEN: {e}")

    games[game_id] = game
    return {"game_id": game_id, "fen": game.state.fen, "turn": game.state.turn}


@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await manager.connect(websocket, game_id)
    try:
        game = get_game(game_id)

        winner_color = game.rules.get_winner()
        is_over = game.rules.is_game_over()

        await manager.broadcast(game_id, json.dumps({
            "type": "game_state",
            "fen": game.state.fen,
            "turn": game.state.turn.value,
            "is_over": is_over,
            "in_check": game.rules.is_check(),
            "winner": winner_color.value if winner_color else None,
            "move_history": game.move_history,
            "clocks": {c.value: t for c, t in game.clocks.items()} if game.clocks else None,
            "status": "connected"
        }))

        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "move":
                move_uci = message["uci"]
                try:
                    move = Move(move_uci, player_to_move=game.state.turn)
                    game.take_turn(move)
                except (ValueError, IllegalMoveException) as e:
                    await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
                    continue

            elif message["type"] == "undo":
                try:
                    game.undo_move()
                except ValueError as e:
                    await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
                    continue

            winner_color = game.rules.get_winner()
            is_over = game.rules.is_game_over()

            status = "active"
            if game.rules.is_checkmate:
                status = "checkmate"
            elif game.rules.is_draw:
                status = "draw"
            elif is_over:
                status = "game_over"
            
            # Check for timeout
            if game.clocks:
                for color, time_left in game.clocks.items():
                    if time_left <= 0:
                        status = "timeout"
                        game.clocks[color] = 0 # Clamp to zero

            await manager.broadcast(game_id, json.dumps({
                "type": "game_state",
                "fen": game.state.fen,
                "turn": game.state.turn.value,
                "is_over": is_over or status == "timeout",
                "in_check": game.rules.is_check(),
                "winner": winner_color.value if winner_color else (game.state.turn.opposite.value if status == "timeout" else None),
                "move_history": game.move_history,
                "clocks": {c.value: t for c, t in game.clocks.items()} if game.clocks else None,
                "status": status
            }))

    except WebSocketDisconnect:
        manager.disconnect(websocket, game_id)
    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
        manager.disconnect(websocket, game_id)


@app.post("/api/moves/legal")
def get_legal_moves_for_square(req: SquareRequest):
    game = get_game(req.game_id)

    try:
        sq_obj = Square(req.square)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid square format.")

    piece = game.state.board.get_piece(sq_obj)

    if piece is None:
        return {"moves": [], "status": "success"}

    if piece.color != game.state.turn:
        raise HTTPException(status_code=400, detail=f"Piece belongs to the opponent ({piece.color}).")

    all_legal_moves = game.rules.get_legal_moves()
    piece_moves = [
        m.uci for m in all_legal_moves
        if m.start == sq_obj
    ]

    return {
        "moves": piece_moves,
        "status": "success",
    }


@app.post("/api/moves/all_legal")
def get_all_legal_moves(req: GameRequest):
    game = get_game(req.game_id)
    all_legal_moves = [m.uci for m in game.rules.get_legal_moves()]
    return {
        "moves": all_legal_moves,
        "status": "success",
    }
