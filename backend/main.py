from uuid import uuid4
from typing import Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import asyncio
import traceback
import random
from contextlib import asynccontextmanager

from v_chess.game import Game, IllegalMoveException
from v_chess.move import Move
from v_chess.square import Square
from v_chess.enums import Color, GameOverReason
from v_chess.rules import (
    AntichessRules, StandardRules, AtomicRules, Chess960Rules,
    CrazyhouseRules, HordeRules, KingOfTheHillRules, RacingKingsRules,
    ThreeCheckRules
)
from backend.database import init_db, async_session, GameModel, User, Rating
from backend.rating import update_game_ratings
from sqlalchemy import select, update
import json
import os
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Request
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
SECRET_KEY = os.environ.get("SECRET_KEY", "a-very-secret-key")
REDIRECT_URI = os.environ.get("REDIRECT_URI") # Optional override

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
                if game.is_over and not model.is_over:
                    await update_game_ratings(session, model, game.winner)
                
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
    print("Timeout monitor started.")
    while True:
        try:
            active_games = list(games.items())
            for game_id, game in active_games:
                if game.clocks and not game.is_over:
                    current_clocks = game.get_current_clocks()
                    for color, time_left in current_clocks.items():
                        if time_left <= 0:
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
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
    task = asyncio.create_task(timeout_monitor())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
        self.lobby_connections: list[WebSocket] = []
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
    async def connect_lobby(self, websocket: WebSocket):
        await websocket.accept()
        self.lobby_connections.append(websocket)
    def disconnect_lobby(self, websocket: WebSocket):
        if websocket in self.lobby_connections:
            self.lobby_connections.remove(websocket)
    async def broadcast_lobby(self, message: str):
        for connection in self.lobby_connections:
            try:
                await connection.send_text(message)
            except Exception:
                continue

manager = ConnectionManager()
seeks: dict[str, dict] = {}
pending_takebacks: dict[str, int] = {}

@app.websocket("/ws/lobby")
async def lobby_websocket(websocket: WebSocket):
    await manager.connect_lobby(websocket)
    user_session = websocket.scope.get("session", {}).get("user")
    current_user_id = str(user_session.get("id")) if user_session else None
    try:
        await websocket.send_text(json.dumps({"type": "seeks", "seeks": list(seeks.values())}))
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message["type"] == "create_seek":
                seek_id = str(uuid4())
                user = message.get("user")
                seek_user_id = user.get("id") if user else current_user_id
                seek_data = {
                    "id": seek_id,
                    "user_id": seek_user_id,
                    "user_name": user.get("name") if user else "Anonymous",
                    "variant": message.get("variant", "standard"),
                    "color": message.get("color", "random"),
                    "time_control": message.get("time_control"),
                    "created_at": asyncio.get_event_loop().time()
                }
                seeks[seek_id] = seek_data
                await manager.broadcast_lobby(json.dumps({"type": "seek_created", "seek": seek_data}))
            elif message["type"] == "cancel_seek":
                seek_id = message.get("seek_id")
                if seek_id in seeks and seeks[seek_id]["user_id"] == current_user_id:
                    del seeks[seek_id]
                    await manager.broadcast_lobby(json.dumps({"type": "seek_removed", "seek_id": seek_id}))
            elif message["type"] == "join_seek":
                seek_id = message.get("seek_id")
                if seek_id in seeks:
                    seek = seeks.pop(seek_id)
                    game_id = str(uuid4())
                    variant = seek["variant"]
                    rules_cls = RULES_MAP.get(variant.lower(), StandardRules)
                    rules = rules_cls()
                    game = Game(rules=rules, time_control=seek["time_control"])
                    games[game_id] = game
                    game_variants[game_id] = variant
                    seeker_id, joiner_id = seek["user_id"], message.get("user", {}).get("id")
                    if seek.get("color") == "white": white_id, black_id = seeker_id, joiner_id
                    elif seek.get("color") == "black": white_id, black_id = joiner_id, seeker_id
                    else:
                        if random.choice([True, False]): white_id, black_id = seeker_id, joiner_id
                        else: white_id, black_id = joiner_id, seeker_id
                    async with async_session() as session:
                        async with session.begin():
                            model = GameModel(id=game_id, variant=variant, fen=game.state.fen, move_history=json.dumps(game.move_history), time_control=json.dumps(game.time_control) if game.time_control else None, white_player_id=white_id, black_player_id=black_id, is_over=False)
                            session.add(model)
                    await manager.broadcast_lobby(json.dumps({"type": "seek_accepted", "seek_id": seek_id, "game_id": game_id}))
    except WebSocketDisconnect: manager.disconnect_lobby(websocket)
    except Exception as e: print(f"Lobby WS error: {e}"); manager.disconnect_lobby(websocket)

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
            else: raise HTTPException(status_code=404, detail="Game not found")
    return games[game_id]

class NewGameRequest(BaseModel):
    variant: str = "standard"
    fen: Optional[str] = None
    time_control: Optional[dict] = None

@app.get("/auth/login")
async def login(request: Request):
    redirect_uri = REDIRECT_URI or str(request.url_for("auth"))
    if is_prod: redirect_uri = redirect_uri.replace("http://", "https://")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/auth")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")
    if user_info:
        async with async_session() as session:
            async with session.begin():
                stmt = select(User).where(User.google_id == user_info["sub"])
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                if not user:
                    user = User(google_id=user_info["sub"], email=user_info["email"], name=user_info["name"], picture=user_info.get("picture"))
                    session.add(user)
                else:
                    user.name, user.picture = user_info["name"], user_info.get("picture")
                await session.flush()
                request.session["user"] = {"id": str(user.google_id), "db_id": int(user.id), "name": str(user.name), "email": str(user.email), "picture": user.picture}
    return RedirectResponse(url=os.environ.get("FRONTEND_URL", "http://localhost:3000"))

@app.get("/auth/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url=os.environ.get("FRONTEND_URL", "http://localhost:3000"))

@app.get("/api/me")
async def me(request: Request): return {"user": request.session.get("user")}

@app.get("/api/ratings/{user_id}")
async def get_user_ratings(user_id: str):
    async with async_session() as session:
        stmt = select(Rating).where(Rating.user_id == user_id)
        result = await session.execute(stmt)
        ratings = result.scalars().all()
        
        rating_list = [{"variant": r.variant, "rating": r.rating, "rd": r.rd} for r in ratings]
        overall = sum(r.rating for r in ratings) / len(ratings) if ratings else 1500.0
        
        return {"ratings": rating_list, "overall": overall}

class LegalMovesRequest(BaseModel):
    game_id: str
    square: str

@app.post("/api/game/new")
async def new_game(req: NewGameRequest):
    try:
        game_id = str(uuid4())
        rules = RULES_MAP.get(req.variant.lower(), StandardRules)()
        game = Game(state=req.fen, rules=rules, time_control=req.time_control)
        games[game_id], game_variants[game_id] = game, req.variant
        await save_game_to_db(game_id)
        return {"game_id": game_id, "fen": game.state.fen, "turn": game.state.turn}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/game/{game_id}")
async def get_game_state(game_id: str):
    game = await get_game(game_id)
    async with async_session() as session:
        model = (await session.execute(select(GameModel).where(GameModel.id == game_id))).scalar_one_or_none()
        return {"game_id": game_id, "fen": game.state.fen, "turn": game.state.turn.value, "is_over": game.is_over, "move_history": game.move_history, "winner": game.winner, "variant": game_variants.get(game_id), "white_player_id": model.white_player_id if model else None, "black_player_id": model.black_player_id if model else None}

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await manager.connect(websocket, game_id)
    game = await get_game(game_id)
    async with async_session() as session:
        model = (await session.execute(select(GameModel).where(GameModel.id == game_id))).scalar_one_or_none()
        white_id, black_id = (model.white_player_id, model.black_player_id) if model else (None, None)
    user_id = str(websocket.scope.get("session", {}).get("user", {}).get("id"))
    await manager.broadcast(game_id, json.dumps({"type": "game_state", "fen": game.state.fen, "turn": game.state.turn.value, "is_over": game.is_over, "in_check": game.rules.is_check(), "winner": game.winner, "move_history": game.move_history, "clocks": {c.value: t for c, t in game.clocks.items()} if game.clocks else None}))
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message["type"] == "move":
                if (game.state.turn == Color.WHITE and white_id and user_id != white_id) or (game.state.turn == Color.BLACK and black_id and user_id != black_id): continue
                move_uci = message["uci"]
                try:
                    start_sq, end_sq = Square(move_uci[:2]), Square(move_uci[2:4])
                    piece = game.state.board.get_piece(start_sq)
                    if piece and piece.fen.lower() == "p" and len(move_uci) == 4 and end_sq.is_promotion_row(piece.color): move_uci += "q"
                    game.take_turn(Move(move_uci, player_to_move=game.state.turn))
                    await save_game_to_db(game_id)
                except Exception as e: await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
            elif message["type"] == "resign":
                if user_id in [white_id, black_id]:
                    game.game_over_reason_override, game.winner_override = GameOverReason.SURRENDER, (Color.BLACK.value if user_id == white_id else Color.WHITE.value)
                    await save_game_to_db(game_id)
            await manager.broadcast(game_id, json.dumps({"type": "game_state", "fen": game.state.fen, "turn": game.state.turn.value, "is_over": game.is_over, "in_check": game.rules.is_check(), "winner": game.winner, "move_history": game.move_history, "clocks": {c.value: t for c, t in game.get_current_clocks().items()} if game.clocks else None}))
    except WebSocketDisconnect: manager.disconnect(websocket, game_id)

class GameRequest(BaseModel):
    game_id: str

@app.post("/api/moves/all_legal")
async def get_all_legal_moves(req: GameRequest):
    game = await get_game(req.game_id)
    return {"moves": [m.uci for m in game.rules.get_legal_moves()], "status": "success"}

@app.post("/api/moves/legal")
async def get_legal_moves(req: LegalMovesRequest):
    game = await get_game(req.game_id)
    try:
        square = Square(req.square)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid square")
        
    piece = game.state.board.get_piece(square)
    if not piece:
        return {"moves": [], "status": "success"}
    
    if piece.color != game.state.turn:
         raise HTTPException(status_code=400, detail="Piece belongs to the opponent")

    legal_moves = game.rules.get_legal_moves()
    moves = [m.uci for m in legal_moves if m.start == square]
    return {"moves": moves, "status": "success"}
