from fastapi import APIRouter
from backend.api.endpoints import auth, users, games, websockets

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/api", tags=["users"])
api_router.include_router(games.router, prefix="/api", tags=["games"])
api_router.include_router(websockets.router, prefix="/ws", tags=["websockets"])
