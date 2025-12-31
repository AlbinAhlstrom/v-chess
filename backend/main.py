import asyncio
import sys
import os

# Add project root to sys.path to find v_chess and backend packages
# This allows running from within the backend directory or from the root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
import json
from sqlalchemy import select

from backend.database import init_db, async_session, GameModel
from backend.core.config import SECRET_KEY, IS_PROD
from backend.api.router import api_router
from backend.tasks.monitors import timeout_monitor, quick_match_monitor
from backend.state import games, game_variants, RULES_MAP
from v_chess.game import Game
from v_chess.enums import Color
from v_chess.rules.standard import StandardRules

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    await init_db()
    
    # Restore active games
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

    # Start monitors
    timeout_task = asyncio.create_task(timeout_monitor())
    match_task = asyncio.create_task(quick_match_monitor())
    
    yield
    
    # Cleanup
    timeout_task.cancel()
    match_task.cancel()
    try:
        await asyncio.gather(timeout_task, match_task)
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

# Middleware
app.add_middleware(
    SessionMiddleware, 
    secret_key=SECRET_KEY,
    session_cookie="v_chess_session",
    same_site="lax",
    https_only=False
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
if not IS_PROD:
    origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app|https://.*\.v-chess\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
