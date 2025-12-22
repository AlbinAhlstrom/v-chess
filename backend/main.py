from uuid import uuid4
from typing import Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import asyncio

from oop_chess.game import Game, IllegalMoveException
from oop_chess.move import Move
from oop_chess.square import Square
from oop_chess.enums import Color
from oop_chess.rules import (
    AntichessRules, StandardRules, AtomicRules, Chess960Rules,
    CrazyhouseRules, HordeRules, KingOfTheHillRules, RacingKingsRules,
    ThreeCheckRules
)
from backend.database import init_db, async_session, GameModel
from sqlalchemy import select, update
import json

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
game_variants: dict[str, str] = {} # game_id -> variant name


async def save_game_to_db(game_id: str):
    game = games.get(game_id)
    variant = game_variants.get(game_id)
    if not game or not variant:
        return

    async with async_session() as session:
        async with session.begin():
            stmt = select(GameModel).where(GameModel.id == game_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            
            clocks_data = None
            if game.clocks:
                clocks_data = json.dumps({k.value: v for k, v in game.clocks.items()})

            if model:
                model.fen = game.state.fen
                model.move_history = json.dumps(game.move_history)
                model.clocks = clocks_data
                model.last_move_at = game.last_move_at
                model.is_over = game.is_over
                model.winner = game.winner
            else:
                model = GameModel(
                    id=game_id,
                    variant=variant,
                    fen=game.state.fen,
                    move_history=json.dumps(game.move_history),
                    time_control=json.dumps(game.time_control) if game.time_control else None,
                    clocks=clocks_data,
                    last_move_at=game.last_move_at,
                    is_over=game.is_over,
                    winner=game.winner
                )
                session.add(model)


async def timeout_monitor():
    """Background task to check for timeouts every 100ms."""
    print("Timeout monitor started.")
    while True:
        try:
            active_games = list(games.items())
            for game_id, game in active_games:
                if game.clocks and not game.is_over:
                    current_clocks = game.get_current_clocks()
                    for color, time_left in current_clocks.items():
                        if time_left <= 0:
                            print(f"Timeout detected for game {game_id}, color {color}")
                            game.is_over_by_timeout = True
                            winner = Color.WHITE if color == Color.BLACK else Color.BLACK
                            
                            await save_game_to_db(game_id)

                            await manager.broadcast(game_id, json.dumps({
                                "type": "game_state",
                                "fen": game.state.fen,
                                "turn": game.state.turn.value,
                                "is_over": True,
                                "in_check": game.rules.is_check(),
                                "winner": winner.value,
                                "move_history": game.move_history,
                                "clocks": {c.value: 0 if c == color else t for c, t in current_clocks.items()},
                                "status": "timeout"
                            }))
            
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Error in timeout monitor: {e}")
            await asyncio.sleep(1)


RULES_MAP = {
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


@app.on_event("startup")
async def startup_event():
    await init_db()
    
    # Load active games from DB
    async with async_session() as session:
        stmt = select(GameModel).where(GameModel.is_over == False)
        result = await session.execute(stmt)
        models = result.scalars().all()
        
        for model in models:
            rules_cls = RULES_MAP.get(model.variant.lower(), StandardRules)
            rules = rules_cls()
            
            time_control = json.loads(model.time_control) if model.time_control else None
            game = Game(state=model.fen, rules=rules, time_control=time_control)
            game.move_history = json.loads(model.move_history)
            
            if model.clocks:
                clocks_dict = json.loads(model.clocks)
                game.clocks = {Color(k): v for k, v in clocks_dict.items()}
            
            game.last_move_at = model.last_move_at
            
            games[model.id] = game
            game_variants[model.id] = model.variant
            
    asyncio.create_task(timeout_monitor())


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


async def get_game(game_id: str) -> Game:
    if game_id not in games:
        async with async_session() as session:
            stmt = select(GameModel).where(GameModel.id == game_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                rules_cls = RULES_MAP.get(model.variant.lower(), StandardRules)
                rules = rules_cls()
                
                time_control = json.loads(model.time_control) if model.time_control else None
                game = Game(state=model.fen, rules=rules, time_control=time_control)
                game.move_history = json.loads(model.move_history)
                
                if model.clocks:
                    clocks_dict = json.loads(model.clocks)
                    game.clocks = {Color(k): v for k, v in clocks_dict.items()}
                
                game.last_move_at = model.last_move_at
                
                games[game_id] = game
                game_variants[game_id] = model.variant
            else:
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
async def new_game(req: NewGameRequest):
    game_id = str(uuid4())

    rules_cls = RULES_MAP.get(req.variant.lower(), StandardRules)
    rules = rules_cls()

    try:
        game = Game(state=req.fen, rules=rules, time_control=req.time_control)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid FEN: {e}")

    games[game_id] = game
    game_variants[game_id] = req.variant
    
    await save_game_to_db(game_id)
    
    return {"game_id": game_id, "fen": game.state.fen, "turn": game.state.turn}


@app.get("/api/game/{game_id}")
async def get_game_state(game_id: str):
    game = await get_game(game_id)
    return {
        "game_id": game_id,
        "fen": game.state.fen,
        "turn": game.state.turn.value,
        "is_over": game.is_over,
        "move_history": game.move_history,
        "winner": game.winner,
        "variant": game_variants.get(game_id)
    }


@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await manager.connect(websocket, game_id)
    try:
        game = await get_game(game_id)

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
                    await save_game_to_db(game_id)
                except (ValueError, IllegalMoveException) as e:
                    await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
                    continue

            elif message["type"] == "undo":
                try:
                    game.undo_move()
                    await save_game_to_db(game_id)
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
            
            # Check for timeout using live clock method
            current_clocks = game.get_current_clocks()
            if current_clocks:
                for color, time_left in current_clocks.items():
                    if time_left <= 0:
                        status = "timeout"
                        current_clocks[color] = 0

            await manager.broadcast(game_id, json.dumps({
                "type": "game_state",
                "fen": game.state.fen,
                "turn": game.state.turn.value,
                "is_over": is_over or status == "timeout",
                "in_check": game.rules.is_check(),
                "winner": winner_color.value if winner_color else (game.state.turn.opposite.value if status == "timeout" else None),
                "move_history": game.move_history,
                "clocks": {c.value: t for c, t in current_clocks.items()} if current_clocks else None,
                "status": status
            }))

    except WebSocketDisconnect:
        manager.disconnect(websocket, game_id)
    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
        manager.disconnect(websocket, game_id)


@app.post("/api/moves/legal")
async def get_legal_moves_for_square(req: SquareRequest):
    game = await get_game(req.game_id)

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
async def get_all_legal_moves(req: GameRequest):
    game = await get_game(req.game_id)
    all_legal_moves = [m.uci for m in game.rules.get_legal_moves()]
    return {
        "moves": all_legal_moves,
        "status": "success",
    }
