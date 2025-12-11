from uuid import uuid4
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

from oop_chess.game import Game, IllegalMoveException
from oop_chess.board import Board
from oop_chess.move import Move
from oop_chess.square import Square


app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
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


@app.post("/api/game/new")
def new_game():
    game_id = str(uuid4())
    board = Board.starting_setup()
    games[game_id] = Game(board)
    return {"game_id": game_id, "fen": board.fen, "turn": board.player_to_move}


@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await manager.connect(websocket, game_id)
    try:
        game = get_game(game_id)
        await manager.broadcast(game_id, json.dumps({
            "type": "game_state",
            "fen": game.board.fen,
            "turn": game.board.player_to_move.value,
            "is_over": game.is_over,
            "in_check": game.is_check,
            "status": "connected"
        }))
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "move":
                move_uci = message["uci"]
                try:
                    move = Move.from_uci(move_uci, player_to_move=game.board.player_to_move)
                    game.take_turn(move)
                except (ValueError, IllegalMoveException) as e:
                    await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
                    continue

                status = "active"
                if game.is_checkmate:
                    status = "checkmate"
                elif game.is_draw:
                    status = "draw"

                await manager.broadcast(game_id, json.dumps({
                    "type": "game_state",
                    "fen": game.board.fen,
                    "turn": game.board.player_to_move.value,
                    "is_over": game.is_over,
                    "in_check": game.is_check,
                    "status": status
                }))
            elif message["type"] == "undo":
                try:
                    game.undo_move()
                except ValueError as e:
                    await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
                    continue
                
                status = "active"
                if game.is_checkmate:
                    status = "checkmate"
                elif game.is_draw:
                    status = "draw"

                await manager.broadcast(game_id, json.dumps({
                    "type": "game_state",
                    "fen": game.board.fen,
                    "turn": game.board.player_to_move.value,
                    "is_over": game.is_over,
                    "in_check": game.is_check,
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
        sq_obj = Square.from_coord(req.square)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid square format.")

    piece = game.board.get_piece(sq_obj)

    if piece is None:
        return {"moves": [], "status": "success"}

    if piece.color != game.board.player_to_move:
        raise HTTPException(status_code=400, detail=f"Piece belongs to the opponent ({piece.color}).")

    all_legal_moves = game.legal_moves
    piece_moves = [
        m.uci for m in all_legal_moves
        if m.start == sq_obj
    ]

    return {
        "moves": piece_moves,
        "status": "success",
    }
