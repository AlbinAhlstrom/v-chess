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
from backend.engine import engine_manager
from sqlalchemy import select, update, or_, and_, desc
import json
import os
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Request
from fastapi.responses import RedirectResponse, HTMLResponse
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
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
        return None

    async with async_session() as session:
        async with session.begin():
            stmt = select(GameModel).where(GameModel.id == game_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            clocks_data = None
            if game.clocks:
                clocks_data = json.dumps({k.value: v for k, v in game.clocks.items()})

            rating_diffs = None
            if model:
                if game.is_over and not model.is_over:
                    rating_diffs = await update_game_ratings(session, model, game.winner)
                    if rating_diffs:
                        model.white_rating_diff = rating_diffs["white_diff"]
                        model.black_rating_diff = rating_diffs["black_diff"]
                
                model.fen = game.state.fen
                model.move_history = json.dumps(game.move_history)
                model.uci_history = json.dumps(game.uci_history)
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
                    uci_history=json.dumps(game.uci_history),
                    time_control=json.dumps(game.time_control) if game.time_control else None,
                    clocks=clocks_data,
                    last_move_at=game.last_move_at,
                    is_over=game.is_over,
                    winner=game.winner
                )
                session.add(model)
            
            return rating_diffs

async def match_players():
    global quick_match_queue, seeks
    if not quick_match_queue:
        return

    to_remove_qm = set()
    to_remove_seeks = set()
    matches = []

    # 1. Match QM users against Lobby seeks
    for i, p1 in enumerate(quick_match_queue):
        for seek_id, s in seeks.items():
            if seek_id in to_remove_seeks: continue
            
            # Prevent matching with self
            if p1["user_id"] == s["user_id"]: continue
            
            # Check criteria (Random/Any matches any variant)
            v_match = (p1["variant"] == s["variant"]) or (p1["variant"] == "random") or (s["variant"] == "random")
            
            if v_match and p1["time_control"] == s["time_control"]:
                # For seeks, we need to know the rating of the creator
                async with async_session() as session:
                    s_rating_info = await get_player_info(session, s["user_id"], s["variant"])
                    s_rating = s_rating_info["rating"]
                
                rating_diff = abs(p1["rating"] - s_rating)
                if rating_diff <= p1["range"]:
                    # Determine final variant
                    match_variant = s["variant"]
                    if match_variant == "random":
                        if p1["variant"] == "random":
                            match_variant = random.choice([v for v in RULES_MAP.keys() if v != 'random'])
                        else:
                            match_variant = p1["variant"]

                    matches.append({
                        "p1": p1,
                        "p2": {
                            "user_id": s["user_id"],
                            "color": s.get("color", "random")
                        },
                        "is_seek": True,
                        "seek_id": seek_id,
                        "variant": match_variant,
                        "time_control": s["time_control"]
                    })
                    to_remove_qm.add(i)
                    to_remove_seeks.add(seek_id)
                    break

    # 2. Match QM users against other QM users
    for i in range(len(quick_match_queue)):
        if i in to_remove_qm: continue
        for j in range(i + 1, len(quick_match_queue)):
            if j in to_remove_qm: continue
            
            p1 = quick_match_queue[i]
            p2 = quick_match_queue[j]

            v_match = (p1["variant"] == p2["variant"]) or (p1["variant"] == "random") or (p2["variant"] == "random")

            if v_match and p1["time_control"] == p2["time_control"]:
                rating_diff = abs(p1["rating"] - p2["rating"])
                if rating_diff <= p1["range"] and rating_diff <= p2["range"]:
                    # Determine final variant
                    match_variant = p1["variant"]
                    if match_variant == "random":
                        if p2["variant"] == "random":
                            match_variant = random.choice([v for v in RULES_MAP.keys() if v != 'random'])
                        else:
                            match_variant = p2["variant"]

                    matches.append({
                        "p1": p1,
                        "p2": p2,
                        "is_seek": False,
                        "variant": match_variant,
                        "time_control": p1["time_control"]
                    })
                    to_remove_qm.add(i)
                    to_remove_qm.add(j)
                    break
    
    # Process all matches
    for m in matches:
        try:
            p1, p2 = m["p1"], m["p2"]
            game_id = str(uuid4())
            variant = m["variant"]
            rules_cls = RULES_MAP.get(variant.lower(), StandardRules)
            rules = rules_cls()
            game = Game(rules=rules, time_control=m["time_control"])
            games[game_id] = game
            game_variants[game_id] = variant
            
            # Color logic
            white_id, black_id = None, None
            if m.get("is_seek"):
                # p2 is the seeker, p1 is the QM joiner
                seeker_color = p2.get("color", "random")
                if seeker_color == "white": white_id, black_id = p2["user_id"], p1["user_id"]
                elif seeker_color == "black": white_id, black_id = p1["user_id"], p2["user_id"]
                else:
                    if random.choice([True, False]): white_id, black_id = p1["user_id"], p2["user_id"]
                    else: white_id, black_id = p2["user_id"], p1["user_id"]
            else:
                # Both QM, randomize
                if random.choice([True, False]): white_id, black_id = p1["user_id"], p2["user_id"]
                else: white_id, black_id = p2["user_id"], p1["user_id"]
                
            async with async_session() as session:
                async with session.begin():
                    model = GameModel(
                        id=game_id, 
                        variant=variant, 
                        fen=game.state.fen, 
                        move_history=json.dumps(game.move_history), 
                        uci_history=json.dumps(game.uci_history),
                        time_control=json.dumps(game.time_control) if game.time_control else None, 
                        white_player_id=white_id, 
                        black_player_id=black_id, 
                        is_over=False
                    )
                    session.add(model)
            
            # Notify players
            # If it was a seek, remove it from lobby UI for everyone
            if m.get("is_seek"):
                del seeks[m["seek_id"]]
                await manager.broadcast_lobby(json.dumps({"type": "seek_removed", "seek_id": m["seek_id"]}))

            await manager.broadcast_lobby(json.dumps({
                "type": "quick_match_found",
                "game_id": game_id,
                "users": [p1["user_id"], p2["user_id"]]
            }))
        except Exception as e:
            print(f"ERROR in match_players processing match: {e}")
            traceback.print_exc()

    # Update QM queue
    quick_match_queue[:] = [p for idx, p in enumerate(quick_match_queue) if idx not in to_remove_qm]

async def quick_match_monitor():
    print("Quick match monitor started.")
    while True:
        try:
            await match_players()
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Error in quick match monitor: {e}")
            await asyncio.sleep(1)

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
                            rating_diffs = await save_game_to_db(game_id)
                            await manager.broadcast(game_id, json.dumps({
                                "type": "game_state",
                                "fen": game.state.fen,
                                "turn": game.state.turn.value,
                                "is_over": True,
                                "in_check": game.rules.is_check(),
                                "winner": winner.value,
                                "move_history": game.move_history,
                                "uci_history": game.uci_history,
                                "clocks": {c.value: 0 if c == color else t for c, t in current_clocks.items()},
                                "status": "timeout",
                                "rating_diffs": rating_diffs
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
            if model.uci_history:
                game.uci_history = json.loads(model.uci_history)
            if model.clocks:
                clocks_dict = json.loads(model.clocks)
                game.clocks = {Color(k): v for k, v in clocks_dict.items()}
            game.last_move_at = model.last_move_at
            games[model.id] = game
            game_variants[model.id] = model.variant
    task = asyncio.create_task(timeout_monitor())
    qm_task = asyncio.create_task(quick_match_monitor())
    yield
    task.cancel()
    qm_task.cancel()
    try:
        await asyncio.gather(task, qm_task)
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    print("WARNING: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set. Google Login will not work.")

is_prod = os.environ.get("ENV") == "prod"
print(f"Starting server in {'PRODUCTION' if is_prod else 'DEVELOPMENT'} mode")

app.add_middleware(
    SessionMiddleware, 
    secret_key=SECRET_KEY,
    session_cookie="v_chess_session",
    same_site="lax", # Always use lax for local development stability
    https_only=False # Allow http for local dev
)
oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    },
    authorize_params={
        "prompt": "select_account"
    }
)

origins = [
    "https://v-chess.com",
    "https://www.v-chess.com",
    "https://api.v-chess.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

if not is_prod:
    origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app|https://.*\.v-chess\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
quick_match_queue: list[dict] = []
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
                    "user_name": user.get("username") or user.get("name") if user else "Anonymous",
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
            elif message["type"] == "join_quick_match":
                if not current_user_id:
                    continue
                variant = message.get("variant", "standard")
                async with async_session() as session:
                    rating_info = await get_player_info(session, current_user_id, variant)
                    user_rating = rating_info["rating"]
                
                # Remove if already in queue
                quick_match_queue[:] = [p for p in quick_match_queue if p["user_id"] != current_user_id]
                
                quick_match_queue.append({
                    "user_id": current_user_id,
                    "variant": variant,
                    "time_control": message.get("time_control"),
                    "rating": user_rating,
                    "range": message.get("range", 200),
                    "joined_at": asyncio.get_event_loop().time()
                })
            elif message["type"] == "leave_quick_match":
                if current_user_id:
                    quick_match_queue[:] = [p for p in quick_match_queue if p["user_id"] != current_user_id]
            elif message["type"] == "join_seek":
                seek_id = message.get("seek_id")
                if seek_id in seeks:
                    seek = seeks.pop(seek_id)
                    game_id = str(uuid4())
                    variant = seek["variant"]
                    if variant == "random":
                        variant = random.choice([v for v in RULES_MAP.keys() if v != 'random'])
                        
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
                            model = GameModel(
                                id=game_id, 
                                variant=variant, 
                                fen=game.state.fen, 
                                move_history=json.dumps(game.move_history), 
                                uci_history=json.dumps(game.uci_history),
                                time_control=json.dumps(game.time_control) if game.time_control else None, 
                                white_player_id=white_id, 
                                black_player_id=black_id, 
                                is_over=False
                            )
                            session.add(model)
                    await manager.broadcast_lobby(json.dumps({"type": "seek_accepted", "seek_id": seek_id, "game_id": game_id}))
    except WebSocketDisconnect: 
        if current_user_id:
            quick_match_queue[:] = [p for p in quick_match_queue if p["user_id"] != current_user_id]
        manager.disconnect_lobby(websocket)
    except Exception as e: 
        if current_user_id:
            quick_match_queue[:] = [p for p in quick_match_queue if p["user_id"] != current_user_id]
        print(f"Lobby WS error: {e}"); manager.disconnect_lobby(websocket)

async def get_game(game_id: str) -> Game:
    if game_id not in games:
        print(f"[DB] Game {game_id} not in memory, checking DB...")
        async with async_session() as session:
            stmt = select(GameModel).where(GameModel.id == game_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model:
                print(f"[DB] Found game {game_id} in DB. Restoring...")
                rules_cls = RULES_MAP.get(model.variant.lower(), StandardRules)
                rules = rules_cls()
                time_control = json.loads(model.time_control) if model.time_control else None
                game = Game(state=model.fen, rules=rules, time_control=time_control)
                game.move_history = json.loads(model.move_history)
                if model.uci_history:
                    game.uci_history = json.loads(model.uci_history)
                if model.clocks:
                    clocks_dict = json.loads(model.clocks)
                    game.clocks = {Color(k): v for k, v in clocks_dict.items()}
                game.last_move_at = model.last_move_at
                games[game_id] = game
                game_variants[game_id] = model.variant
            else: 
                print(f"[DB] Game {game_id} NOT FOUND in DB.")
                raise HTTPException(status_code=404, detail=f"Game {game_id} not found")
    return games[game_id]

async def get_player_info(session, user_id, variant, default_name="Anonymous", fallback_rating=1500):
    if not user_id:
        return {"name": default_name, "rating": fallback_rating}
    
    if user_id == "computer":
        # Match player to the closest increment of 50
        rounded_rating = round(fallback_rating / 50) * 50
        return {"id": "computer", "name": "Stockfish AI", "rating": rounded_rating}
    
    user = (await session.execute(select(User).where(User.google_id == user_id))).scalar_one_or_none()
    if not user:
        print(f"WARNING: User with google_id={user_id} not found in DB.")
        return {"name": default_name, "rating": 1500}
        
    rating_obj = (await session.execute(select(Rating).where(Rating.user_id == user_id, Rating.variant == variant))).scalar_one_or_none()
    
    return {
        "id": user_id,
        "name": user.username or user.name,
        "picture": user.picture,
        "supporter_badge": user.supporter_badge,
        "rating": int(rating_obj.rating) if rating_obj else 1500
    }

class NewGameRequest(BaseModel):
    variant: str = "standard"
    fen: Optional[str] = None
    time_control: Optional[dict] = None

@app.get("/auth/login")
async def login(request: Request):
    dynamic_uri = str(request.url_for("auth"))
    redirect_uri = REDIRECT_URI or dynamic_uri
    
    if is_prod: 
        redirect_uri = redirect_uri.replace("http://", "https://")
    
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/auth")
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        print(f"OAuth Error: {error.error}")
        return HTMLResponse(f'<h1>OAuth Error</h1><pre>{error.error}</pre>')
    
    user_info = token.get("userinfo")
    if user_info:
        try:
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
                    request.session["user"] = {
                        "id": str(user.google_id), 
                        "db_id": int(user.id), 
                        "name": str(user.name), 
                        "username": str(user.username) if user.username else None,
                        "email": str(user.email), 
                        "picture": user.picture,
                        "default_time": float(user.default_time),
                        "default_increment": float(user.default_increment),
                        "default_time_control_enabled": bool(user.default_time_control_enabled)
                    }
        except Exception as e:
            print("Error saving user to DB:")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail="Database error during authentication")
            
    return RedirectResponse(url=os.environ.get("FRONTEND_URL", "http://localhost:3000"))

@app.get("/auth/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url=os.environ.get("FRONTEND_URL", "http://localhost:3000"))

async def ensure_user_in_db(user_session):
    if not user_session:
        return None
    
    google_id = user_session.get("id")
    if not google_id:
        return None
        
    try:
        async with async_session() as session:
            async with session.begin():
                stmt = select(User).where(User.google_id == google_id)
                result = await session.execute(stmt)
                db_user = result.scalar_one_or_none()
                
                if not db_user:
                    print(f"Resurrecting user {google_id} from session data...")
                    db_user = User(
                        google_id=google_id,
                        username=user_session.get("username"),
                        email=user_session.get("email", ""),
                        name=user_session.get("name", "Unknown"),
                        picture=user_session.get("picture"),
                        supporter_badge=user_session.get("supporter_badge"),
                        default_time=user_session.get("default_time", 10.0),
                        default_increment=user_session.get("default_increment", 0.0),
                        default_time_control_enabled=user_session.get("default_time_control_enabled", True)
                    )
                    session.add(db_user)
                return db_user
    except Exception as e:
        print(f"Error resurrecting user {google_id}: {e}")
        traceback.print_exc()
        return None

@app.get("/api/me")
async def me(request: Request):
    user_session = request.session.get("user")
    if user_session:
        db_user = await ensure_user_in_db(user_session)
        if db_user:
            user_session["supporter_badge"] = db_user.supporter_badge
            user_session["username"] = str(db_user.username) if db_user.username else None
            user_session["default_time"] = float(db_user.default_time)
            user_session["default_increment"] = float(db_user.default_increment)
            user_session["default_time_control_enabled"] = bool(db_user.default_time_control_enabled)
    return {"user": user_session}

class SetUsernameRequest(BaseModel):
    username: str

@app.post("/api/user/set_username")
async def set_username(req: SetUsernameRequest, request: Request):
    user_session = request.session.get("user")
    if not user_session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    username = req.username.strip()
    if len(username) < 3 or len(username) > 20:
        raise HTTPException(status_code=400, detail="Username must be between 3 and 20 characters")
    
    import re
    if not re.match(r"^[a-zA-Z0-9_\-]+$", username):
        raise HTTPException(status_code=400, detail="Username can only contain letters, numbers, underscores, and hyphens")

    google_id = user_session.get("id")
    async with async_session() as session:
        async with session.begin():
            # Check if taken
            stmt = select(User).where(User.username == username)
            existing = (await session.execute(stmt)).scalar_one_or_none()
            if existing:
                raise HTTPException(status_code=400, detail="Username already taken")
            
            stmt = select(User).where(User.google_id == google_id)
            user = (await session.execute(stmt)).scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            user.username = username
            
            # Update session
            user_session["username"] = username
            request.session["user"] = user_session
            
    return {"status": "success", "username": username}

class UserSettingsRequest(BaseModel):
    default_time: float
    default_increment: float
    default_time_control_enabled: bool

@app.post("/api/user/settings")
async def update_user_settings(req: UserSettingsRequest, request: Request):
    user_session = request.session.get("user")
    if not user_session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    google_id = user_session.get("id")
    async with async_session() as session:
        async with session.begin():
            stmt = select(User).where(User.google_id == google_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            user.default_time = req.default_time
            user.default_increment = req.default_increment
            user.default_time_control_enabled = req.default_time_control_enabled
            
            # Update session
            user_session["default_time"] = float(user.default_time)
            user_session["default_increment"] = float(user.default_increment)
            user_session["default_time_control_enabled"] = bool(user.default_time_control_enabled)
            request.session["user"] = user_session
            
    return {"status": "success"}

@app.get("/api/ratings/{user_id}")
async def get_user_ratings(user_id: str):
    async with async_session() as session:
        stmt = select(Rating).where(Rating.user_id == user_id)
        result = await session.execute(stmt)
        ratings = result.scalars().all()
        
        rating_list = [{"variant": r.variant, "rating": r.rating, "rd": r.rd} for r in ratings]
        overall = sum(r.rating for r in ratings) / len(ratings) if ratings else 1500.0
        
        return {"ratings": rating_list, "overall": overall}

@app.get("/api/user/{user_id}")
async def get_user_profile(user_id: str, request: Request):
    # If the requested profile is the logged-in user, ensure they are in DB
    user_session = request.session.get("user")
    if user_session and str(user_session.get("id")) == user_id:
        await ensure_user_in_db(user_session)

    async with async_session() as session:
        stmt = select(User).where(User.google_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            # Fallback for anonymous or missing users instead of 404
            return {
                "user": {
                    "id": user_id,
                    "name": "Anonymous",
                    "picture": None,
                    "supporter_badge": None,
                    "created_at": None
                },
                "ratings": [],
                "overall": 1500.0
            }
            
        stmt_ratings = select(Rating).where(Rating.user_id == user_id)
        result_ratings = await session.execute(stmt_ratings)
        ratings = result_ratings.scalars().all()
        
        rating_list = [{"variant": r.variant, "rating": r.rating, "rd": r.rd} for r in ratings]
        overall = sum(r.rating for r in ratings) / len(ratings) if ratings else 1500.0
        
        print(f"DEBUG: Returning profile for {user_id}. Badge: {user.supporter_badge}")
        return {
            "user": {
                "id": user.google_id,
                "name": user.username or user.name,
                "username": user.username,
                "picture": user.picture,
                "supporter_badge": user.supporter_badge,
                "created_at": user.created_at
            },
            "ratings": rating_list,
            "overall": overall
        }

@app.get("/api/user/{user_id}/games")
async def get_user_games(
    user_id: str, 
    request: Request,
    skip: int = 0, 
    limit: int = 50, 
    variant: Optional[str] = None, 
    result: Optional[str] = None
):
    async with async_session() as session:
        filters = [
            or_(GameModel.white_player_id == user_id, GameModel.black_player_id == user_id),
            GameModel.is_over == True
        ]

        if variant and variant != "all":
            filters.append(GameModel.variant == variant)

        if result:
            if result == "win":
                filters.append(or_(
                    and_(GameModel.white_player_id == user_id, GameModel.winner == "white"),
                    and_(GameModel.black_player_id == user_id, GameModel.winner == "black")
                ))
            elif result == "loss":
                filters.append(or_(
                    and_(GameModel.white_player_id == user_id, GameModel.winner == "black"),
                    and_(GameModel.black_player_id == user_id, GameModel.winner == "white")
                ))
            elif result == "draw":
                filters.append(GameModel.winner == "draw")

        stmt = (
            select(GameModel)
            .where(*filters)
            .order_by(desc(GameModel.created_at))
            .offset(skip)
            .limit(limit)
        )
        
        games_result = await session.execute(stmt)
        games_rows = games_result.scalars().all()
        
        # Collect opponent IDs to batch fetch (optimization)
        opponent_ids = set()
        for g in games_rows:
            opp_id = g.black_player_id if g.white_player_id == user_id else g.white_player_id
            if opp_id and opp_id != "computer":
                opponent_ids.add(opp_id)
        
        # Batch fetch users
        users_map = {}
        if opponent_ids:
            u_stmt = select(User).where(User.google_id.in_(opponent_ids))
            u_res = await session.execute(u_stmt)
            for u in u_res.scalars():
                users_map[u.google_id] = u

        history = []
        for g in games_rows:
            is_white = (g.white_player_id == user_id)
            my_color = "white" if is_white else "black"
            
            # Determine result string
            game_result = "draw"
            if g.winner:
                if g.winner == "draw":
                    game_result = "draw"
                elif g.winner == my_color:
                    game_result = "win"
                else:
                    game_result = "loss"

            # Opponent info
            opp_id = g.black_player_id if is_white else g.white_player_id
            opp_name = "Anonymous"
            opp_rating = None # We assume stored in game model snapshot if we had it, but we rely on current rating or nothing for now? 
            # Actually, we don't store snapshot rating in GameModel explicitly aside from diffs.
            # We can use the user's current rating or just show name.
            # Ideally we should store snapshot rating. For now, let's use the name from User table.
            
            if opp_id == "computer":
                opp_name = "Stockfish AI"
            elif opp_id in users_map:
                u = users_map[opp_id]
                opp_name = u.username or u.name
            
            # Rating diff
            my_diff = g.white_rating_diff if is_white else g.black_rating_diff

            history.append({
                "id": g.id,
                "variant": g.variant,
                "created_at": g.created_at,
                "my_color": my_color,
                "result": game_result,
                "opponent": {
                    "id": opp_id,
                    "name": opp_name
                },
                "rating_diff": my_diff
            })

        return {"games": history}

@app.get("/api/leaderboard/{variant}")
async def get_leaderboard(variant: str):
    async with async_session() as session:
        # Get top 50 players for the variant
        # Join Rating with User to get names and pictures
        stmt = (
            select(Rating, User)
            .join(User, Rating.user_id == User.google_id)
            .where(Rating.variant == variant.lower())
            .order_by(Rating.rating.desc())
            .limit(50)
        )
        result = await session.execute(stmt)
        rows = result.all()
        
        leaderboard = []
        for rating_obj, user_obj in rows:
            leaderboard.append({
                "user_id": user_obj.google_id,
                "name": user_obj.username or user_obj.name,
                "picture": user_obj.picture,
                "supporter_badge": user_obj.supporter_badge,
                "rating": int(rating_obj.rating),
                "rd": int(rating_obj.rd)
            })
            
        return {"variant": variant, "leaderboard": leaderboard}

class LegalMovesRequest(BaseModel):
    game_id: str
    square: str

class NewGameRequest(BaseModel):
    variant: str = "standard"
    fen: Optional[str] = None
    time_control: Optional[dict] = None
    play_as: Optional[str] = "white" # "white", "black", or "random"
    is_computer: bool = False

@app.post("/api/game/new")
async def new_game(req: NewGameRequest, request: Request):
    try:
        game_id = str(uuid4())
        variant = req.variant
        if variant == "random":
            variant = random.choice([v for v in RULES_MAP.keys() if v != 'random'])
            
        rules = RULES_MAP.get(variant.lower(), StandardRules)()
        game = Game(state=req.fen, rules=rules, time_control=req.time_control)
        games[game_id], game_variants[game_id] = game, variant
        
        user_session = request.session.get("user")
        user_id = str(user_session.get("id")) if user_session else None
        
        white_id, black_id = None, None
        if req.is_computer:
            play_as = req.play_as
            if play_as == "random":
                play_as = random.choice(["white", "black"])
            
            if play_as == "white":
                white_id, black_id = user_id, "computer"
            else:
                white_id, black_id = "computer", user_id
        
        async with async_session() as session:
            async with session.begin():
                model = GameModel(
                    id=game_id, 
                    variant=req.variant, 
                    fen=game.state.fen, 
                    move_history=json.dumps(game.move_history), 
                    uci_history=json.dumps(game.uci_history),
                    time_control=json.dumps(game.time_control) if game.time_control else None, 
                    white_player_id=white_id, 
                    black_player_id=black_id, 
                    is_over=False
                )
                session.add(model)
        
        return {"game_id": game_id, "fen": game.state.fen, "turn": game.state.turn}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/game/{game_id}")
async def get_game_state(game_id: str):
    game = await get_game(game_id)
    variant = game_variants.get(game_id, "standard")
    async with async_session() as session:
        model = (await session.execute(select(GameModel).where(GameModel.id == game_id))).scalar_one_or_none()
        
        # Fetch human rating first to use as fallback for computer
        human_id = model.white_player_id if model and model.black_player_id == "computer" else (model.black_player_id if model else None)
        human_rating = 1500
        if human_id and human_id != "computer":
            human_info = await get_player_info(session, human_id, variant)
            human_rating = human_info["rating"]

        white_player = await get_player_info(session, model.white_player_id if model else None, variant, default_name="White", fallback_rating=human_rating)
        black_player = await get_player_info(session, model.black_player_id if model else None, variant, default_name="Black", fallback_rating=human_rating)

        rating_diffs = None
        if model and model.white_rating_diff is not None:
            rating_diffs = {
                "white_diff": int(model.white_rating_diff),
                "black_diff": int(model.black_rating_diff)
            }

        return {
            "game_id": game_id, 
            "fen": game.state.fen, 
            "turn": game.state.turn.value, 
            "is_over": game.is_over, 
            "move_history": game.move_history, 
            "uci_history": game.uci_history,
            "winner": game.winner, 
            "variant": variant, 
            "white_player": white_player,
            "black_player": black_player,
            "rating_diffs": rating_diffs
        }

async def trigger_ai_move(game_id: str, game: Game):
    if game.is_over:
        print(f"[AI] Game {game_id} is already over. Not moving.")
        return

    print(f"[AI] START: Triggering AI move for game {game_id}. Turn: {game.state.turn}")
    variant = game_variants.get(game_id, "standard")
    fen = game.state.fen
    
    # Calculate difficulty based on human opponent's rating
    user_rating = 1500
    try:
        async with async_session() as session:
            model = (await session.execute(select(GameModel).where(GameModel.id == game_id))).scalar_one_or_none()
            if model:
                # Find the human player's ID
                human_id = model.white_player_id if model.black_player_id == "computer" else model.black_player_id
                if human_id and human_id != "computer":
                    rating_info = await get_player_info(session, human_id, variant)
                    user_rating = rating_info["rating"]
    except Exception as e:
        print(f"[AI] Error fetching rating for difficulty: {e}")

    # Scaling Logic:
    # 1. Use UCI_Elo for a base level
    # 2. Use Nodes limit to simulate tactical blindness
    # Match player to the closest increment of 50
    bot_rating = round(user_rating / 50) * 50
    node_limit = max(500, (bot_rating ** 2) // 40)
    elo_target = bot_rating

    print(f"[AI] Calling engine for FEN: {fen}, variant: {variant}, elo={elo_target}, nodes={node_limit}")
    
    try:
        # best_move is UCI string
        best_move_uci = await engine_manager.get_best_move(fen, variant=variant, elo=elo_target, nodes=node_limit)
        print(f"[AI] Engine returned best move: {best_move_uci}")
        
        if best_move_uci:
            # Add a small 'thinking' delay for lower ratings to feel more human
            if user_rating < 1800:
                delay = random.uniform(0.5, 2.0)
                await asyncio.sleep(delay)

            print(f"[AI] APPLYING move {best_move_uci} to game {game_id}")
            move_obj = Move(best_move_uci, player_to_move=game.state.turn)
            game.take_turn(move_obj)
            rating_diffs = await save_game_to_db(game_id)
            print(f"[AI] BROADCASTING move {best_move_uci}")
            await manager.broadcast(game_id, json.dumps({
                "type": "game_state", 
                "fen": game.state.fen, 
                "turn": game.state.turn.value, 
                "is_over": game.is_over, 
                "in_check": game.rules.is_check(), 
                "winner": game.winner, 
                "move_history": game.move_history, 
                                "uci_history": game.uci_history,
                                "clocks": {c.value: t for c, t in game.get_current_clocks().items()} if game.clocks else None, 
                                "rating_diffs": rating_diffs,
                                "explosion_square": str(game.state.explosion_square) if getattr(game.state, 'explosion_square', None) else None,
                                "is_drop": move_obj.is_drop
                            }))
        else:
            print(f"[AI] WARNING: Engine returned no move!")
    except Exception as e:
        print(f"[AI] ERROR in trigger_ai_move: {e}")
        traceback.print_exc()

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await manager.connect(websocket, game_id)
    game = await get_game(game_id)
    async with async_session() as session:
        model = (await session.execute(select(GameModel).where(GameModel.id == game_id))).scalar_one_or_none()
        white_id, black_id = (model.white_player_id, model.black_player_id) if model else (None, None)
    
    user_session = websocket.scope.get("session", {}).get("user")
    user_id = str(user_session.get("id")) if user_session else None
    
    print(f"[WS] Connection for {game_id}. user_id={user_id}, model_white={white_id}, model_black={black_id}")

    # Broadcast initial state
    await manager.broadcast(game_id, json.dumps({
        "type": "game_state", 
        "fen": game.state.fen, 
        "turn": game.state.turn.value, 
        "is_over": game.is_over, 
        "in_check": game.rules.is_check(), 
        "winner": game.winner, 
        "move_history": game.move_history, 
        "uci_history": game.uci_history,
        "clocks": {c.value: t for c, t in game.clocks.items()} if game.clocks else None,
        "explosion_square": str(game.state.explosion_square) if hasattr(game.state, 'explosion_square') and game.state.explosion_square else None
    }))

    # If it's computer's turn, trigger it
    if not game.is_over:
        is_ai_turn = (game.state.turn == Color.WHITE and white_id == "computer") or \
                     (game.state.turn == Color.BLACK and black_id == "computer")
        if is_ai_turn:
            print(f"[WS] AI's turn! Starting AI task.")
            asyncio.create_task(trigger_ai_move(game_id, game))

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message["type"] == "move":
                # Refresh IDs from DB in case they changed (though they shouldn't)
                async with async_session() as session:
                    model = (await session.execute(select(GameModel).where(GameModel.id == game_id))).scalar_one_or_none()
                    white_id, black_id = (model.white_player_id, model.black_player_id) if model else (None, None)

                print(f"[WS] Move received: {message.get('uci')}. Turn: {game.state.turn}. White: {white_id}, Black: {black_id}, User: {user_id}")
                
                is_white_turn = game.state.turn == Color.WHITE
                is_black_turn = game.state.turn == Color.BLACK
                
                # STRICT AI TURN CHECK
                if (is_white_turn and white_id == "computer") or (is_black_turn and black_id == "computer"):
                    print(f"[WS] REJECTED: It is computer's turn.")
                    # Re-trigger AI just in case it stalled
                    asyncio.create_task(trigger_ai_move(game_id, game))
                    continue
                
                # Matchmaking checks
                if is_white_turn and white_id and white_id != "computer" and user_id != white_id:
                    print(f"[WS] REJECTED: User {user_id} is not White {white_id}")
                    continue
                if is_black_turn and black_id and black_id != "computer" and user_id != black_id:
                    print(f"[WS] REJECTED: User {user_id} is not Black {black_id}")
                    continue

                move_uci = message["uci"]
                offer_draw = message.get("offer_draw", False)
                try:
                    # Handle automatic promotion for pawns if not specified
                    if "@" not in move_uci:
                        start_sq, end_sq = Square(move_uci[:2]), Square(move_uci[2:4])
                        piece = game.state.board.get_piece(start_sq)
                        if piece and piece.fen.lower() == "p" and len(move_uci) == 4 and end_sq.is_promotion_row(piece.color): 
                            move_uci += "q"
                    
                    print(f"[WS] Applying human move: {move_uci} for game {game_id}")
                    move_obj = Move(move_uci, player_to_move=game.state.turn)
                    game.take_turn(move_obj, offer_draw=offer_draw)
                    rating_diffs = await save_game_to_db(game_id)
                    print(f"[WS] Human move BROADCAST: {move_uci}")
                    
                    await manager.broadcast(game_id, json.dumps({
                        "type": "game_state", 
                        "fen": game.state.fen, 
                        "turn": game.state.turn.value, 
                        "is_over": game.is_over, 
                        "in_check": game.rules.is_check(), 
                        "winner": game.winner, 
                        "move_history": game.move_history, 
                        "uci_history": game.uci_history,
                        "clocks": {c.value: t for c, t in game.get_current_clocks().items()} if game.clocks else None, 
                        "rating_diffs": rating_diffs,
                        "explosion_square": str(game.state.explosion_square) if getattr(game.state, 'explosion_square', None) else None,
                        "is_drop": move_obj.is_drop
                    }))

                    # Trigger AI move
                    if not game.is_over:
                        if (game.state.turn == Color.WHITE and white_id == "computer") or \
                           (game.state.turn == Color.BLACK and black_id == "computer"):
                            asyncio.create_task(trigger_ai_move(game_id, game))

                except Exception as e: 
                    print(f"[WS] Move error: {e}")
                    await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
            elif message["type"] == "undo":
                is_local_game = (white_id is None and black_id is None)
                if is_local_game or (user_id in [white_id, black_id]):
                    try:
                        game.undo_move()
                        await save_game_to_db(game_id)
                        await manager.broadcast(game_id, json.dumps({
                            "type": "game_state", 
                            "fen": game.state.fen, 
                            "turn": game.state.turn.value, 
                            "is_over": game.is_over, 
                            "in_check": game.rules.is_check(), 
                            "winner": game.winner, 
                            "move_history": game.move_history, 
                            "uci_history": game.uci_history,
                            "clocks": {c.value: t for c, t in game.get_current_clocks().items()} if game.clocks else None, 
                            "rating_diffs": None,
                            "explosion_square": None,
                            "is_drop": False
                        }))
                    except Exception as e:
                        print(f"[WS] Undo error: {e}")
                        await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
            elif message["type"] == "resign":
                if user_id in [white_id, black_id] or (not white_id and not black_id): # Allow anyone in anonymous games
                    game.game_over_reason_override, game.winner_override = GameOverReason.SURRENDER, (Color.BLACK.value if user_id == white_id else Color.WHITE.value)
                    rating_diffs = await save_game_to_db(game_id)
                    await manager.broadcast(game_id, json.dumps({
                        "type": "game_state", 
                        "fen": game.state.fen, 
                        "turn": game.state.turn.value, 
                        "is_over": game.is_over, 
                        "in_check": game.rules.is_check(), 
                        "winner": game.winner, 
                        "move_history": game.move_history, 
                        "uci_history": game.uci_history,
                        "clocks": {c.value: t for c, t in game.get_current_clocks().items()} if game.clocks else None, 
                        "rating_diffs": rating_diffs,
                        "explosion_square": str(game.state.explosion_square) if getattr(game.state, 'explosion_square', None) else None,
                        "is_drop": False
                    }))
    except WebSocketDisconnect:
        manager.disconnect(websocket, game_id)
    except Exception as e:
        print(f"[WS] CRITICAL ERROR in websocket loop: {e}")
        traceback.print_exc()
        manager.disconnect(websocket, game_id)

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
