from uuid import uuid4
from typing import Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import asyncio
import traceback

from oop_chess.game import Game, IllegalMoveException
from oop_chess.move import Move
from oop_chess.square import Square
from oop_chess.enums import Color
from oop_chess.rules import (
    AntichessRules, StandardRules, AtomicRules, Chess960Rules,
    CrazyhouseRules, HordeRules, KingOfTheHillRules, RacingKingsRules,
    ThreeCheckRules
)
from backend.database import init_db, async_session, GameModel, User
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

app = FastAPI()

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    print("WARNING: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set. Google Login will not work.")

# Configure session middleware
# In production, we need SameSite=None and Secure=True for cross-domain cookies
is_prod = os.environ.get("ENV") == "prod"
app.add_middleware(
    SessionMiddleware, 
    secret_key=SECRET_KEY,
    session_cookie="v_chess_session",
    same_site="none" if is_prod else "lax",
    https_only=is_prod
)
oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    },
    authorize_params={
        'prompt': 'select_account'
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app|https://.*\.v-chess\.com",
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

# Seek storage: seek_id -> seek_data
seeks: dict[str, dict] = {}


@app.websocket("/ws/lobby")
async def lobby_websocket(websocket: WebSocket):
    await manager.connect_lobby(websocket)
    try:
        # Send initial seek list
        await websocket.send_text(json.dumps({
            "type": "seeks",
            "seeks": list(seeks.values())
        }))

        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "create_seek":
                seek_id = str(uuid4())
                user = message.get("user")
                seek_data = {
                    "id": seek_id,
                    "user_id": user.get("id") if user else None,
                    "user_name": user.get("name") if user else "Anonymous",
                    "variant": message.get("variant", "standard"),
                    "time_control": message.get("time_control"),
                    "created_at": asyncio.get_event_loop().time()
                }
                seeks[seek_id] = seek_data
                await manager.broadcast_lobby(json.dumps({
                    "type": "seek_created",
                    "seek": seek_data
                }))

            elif message["type"] == "cancel_seek":
                seek_id = message.get("seek_id")
                if seek_id in seeks:
                    del seeks[seek_id]
                    await manager.broadcast_lobby(json.dumps({
                        "type": "seek_removed",
                        "seek_id": seek_id
                    }))

            elif message["type"] == "join_seek":
                print(f"DEBUG: Received join_seek for {message.get('seek_id')} from {message.get('user')}", flush=True)
                try:
                    seek_id = message.get("seek_id")
                    joining_user = message.get("user")
                    if seek_id in seeks:
                        print(f"DEBUG: Found seek {seek_id}, creating game...", flush=True)
                        seek = seeks.pop(seek_id)
                        
                        # Create a new game
                        game_id = str(uuid4())
                        variant = seek["variant"]
                        rules_cls = RULES_MAP.get(variant.lower(), StandardRules)
                        rules = rules_cls()
                        
                        # For now: Seeker is White, Joiner is Black
                        game = Game(rules=rules, time_control=seek["time_control"])
                        games[game_id] = game
                        game_variants[game_id] = variant
                        
                        # Assign players in DB
                        async with async_session() as session:
                            async with session.begin():
                                model = GameModel(
                                    id=game_id,
                                    variant=variant,
                                    fen=game.state.fen,
                                    move_history=json.dumps(game.move_history),
                                    time_control=json.dumps(game.time_control) if game.time_control else None,
                                    white_player_id=seek["user_id"],
                                    black_player_id=joining_user.get("id") if joining_user else None,
                                    is_over=False
                                )
                                session.add(model)

                        print(f"DEBUG: Game {game_id} created in DB. Broadcasting...", flush=True)
                        await manager.broadcast_lobby(json.dumps({
                            "type": "seek_accepted",
                            "seek_id": seek_id,
                            "game_id": game_id
                        }))
                except Exception as e:
                    print(f"CRITICAL ERROR in join_seek: {e}", flush=True)
                    traceback.print_exc()

    except WebSocketDisconnect:
        manager.disconnect_lobby(websocket)
    except Exception as e:
        print(f"Lobby WebSocket error: {e}")
        manager.disconnect_lobby(websocket)


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


@app.get("/auth/login")
async def login(request: Request):
    # Use REDIRECT_URI if provided in .env, otherwise generate one
    redirect_uri = REDIRECT_URI
    if not redirect_uri:
        redirect_uri = request.url_for('auth')
        # If in production, force https
        if os.environ.get("ENV") == "prod":
            redirect_uri = str(redirect_uri).replace("http://", "https://")

    print(f"DEBUG: Using redirect_uri: {redirect_uri}")
    return await oauth.google.authorize_redirect(request, str(redirect_uri))


@app.get("/auth/auth")
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return {"error": error.error}

    user_info = token.get('userinfo')
    if user_info:
        async with async_session() as session:
            async with session.begin():
                stmt = select(User).where(User.google_id == user_info['sub'])
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if not user:
                    user = User(
                        google_id=user_info['sub'],
                        email=user_info['email'],
                        name=user_info['name'],
                        picture=user_info.get('picture')
                    )
                    session.add(user)
                    await session.flush() # Get user.id
                else:
                    user.name = user_info['name']
                    user.picture = user_info.get('picture')

                request.session['user'] = {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "picture": user.picture
                }

    # Redirect to frontend
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    return RedirectResponse(url=frontend_url)


@app.get("/auth/logout")
async def logout(request: Request):
    request.session.clear()
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    return RedirectResponse(url=frontend_url)


@app.get("/api/me")
async def me(request: Request):
    user = request.session.get('user')
    return {"user": user}


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
    
    async with async_session() as session:
        stmt = select(GameModel).where(GameModel.id == game_id)
        result = await session.execute(stmt)
        model = result.scalar_one_or_none()
        
        white_player_id = model.white_player_id if model else None
        black_player_id = model.black_player_id if model else None

    return {
        "game_id": game_id,
        "fen": game.state.fen,
        "turn": game.state.turn.value,
        "is_over": game.is_over,
        "move_history": game.move_history,
        "winner": game.winner,
        "variant": game_variants.get(game_id),
        "white_player_id": white_player_id,
        "black_player_id": black_player_id
    }


@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await manager.connect(websocket, game_id)
    try:
        game = await get_game(game_id)

        # Fetch player assignments to validate moves
        white_player_id = None
        black_player_id = None
        async with async_session() as session:
            stmt = select(GameModel).where(GameModel.id == game_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model:
                white_player_id = model.white_player_id
                black_player_id = model.black_player_id

        user = websocket.session.get("user")
        user_id = user.get("id") if user else None

        winner_color = game.rules.get_winner()
        is_over = game.rules.is_game_over()

        # DEBUG: Broadcast player IDs
        print(f"DEBUG: WS Connected. Game: {game_id}, WhiteID: {white_player_id}, BlackID: {black_player_id}, UserID: {user_id}", flush=True)

        await manager.broadcast(game_id, json.dumps({
            "type": "game_state",
            "fen": game.state.fen,
            "turn": game.state.turn.value,
            "is_over": is_over,
            "in_check": game.rules.is_check(),
            "winner": winner_color.value if winner_color else None,
            "move_history": game.move_history,
            "clocks": {c.value: t for c, t in game.clocks.items()} if game.clocks else None,
            "status": "connected",
            "debug_players": {"white": white_player_id, "black": black_player_id, "you": user_id}
        }))

        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "move":
                # Validate turn ownership
                print(f"DEBUG: Move request. Turn: {game.state.turn}, UserID: {user_id}, White: {white_player_id}, Black: {black_player_id}", flush=True)
                
                if game.state.turn == Color.WHITE and white_player_id is not None:
                    if user_id != white_player_id:
                        print(f"DEBUG: Blocked White move. {user_id} != {white_player_id}", flush=True)
                        await websocket.send_text(json.dumps({"type": "error", "message": "Not your turn!"}))
                        continue
                elif game.state.turn == Color.BLACK and black_player_id is not None:
                    if user_id != black_player_id:
                        print(f"DEBUG: Blocked Black move. {user_id} != {black_player_id}", flush=True)
                        await websocket.send_text(json.dumps({"type": "error", "message": "Not your turn!"}))
                        continue

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
