from fastapi import APIRouter, Request, HTTPException
from sqlalchemy import select, or_, and_, desc
from typing import Optional
import re

from backend.database import async_session, User, Rating, GameModel
from backend.schemas import SetUsernameRequest, UserSettingsRequest
from backend.services.user_service import ensure_user_in_db
from backend.services.game_service import get_player_info

router = APIRouter()

@router.get("/me")
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

@router.post("/user/set_username")
async def set_username(req: SetUsernameRequest, request: Request):
    user_session = request.session.get("user")
    if not user_session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    username = req.username.strip()
    if len(username) < 3 or len(username) > 20:
        raise HTTPException(status_code=400, detail="Username must be between 3 and 20 characters")
    
    if not re.match(r"^[a-zA-Z0-9_\-]+$", username):
        raise HTTPException(status_code=400, detail="Username can only contain letters, numbers, underscores, and hyphens")

    google_id = user_session.get("id")
    async with async_session() as session:
        async with session.begin():
            stmt = select(User).where(User.username == username)
            existing = (await session.execute(stmt)).scalar_one_or_none()
            if existing:
                raise HTTPException(status_code=400, detail="Username already taken")
            
            stmt = select(User).where(User.google_id == google_id)
            user = (await session.execute(stmt)).scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            user.username = username
            user_session["username"] = username
            request.session["user"] = user_session
            
    return {"status": "success", "username": username}

@router.post("/user/settings")
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
            
            user_session["default_time"] = float(user.default_time)
            user_session["default_increment"] = float(user.default_increment)
            user_session["default_time_control_enabled"] = bool(user.default_time_control_enabled)
            request.session["user"] = user_session
            
    return {"status": "success"}

@router.get("/ratings/{user_id}")
async def get_user_ratings(user_id: str):
    async with async_session() as session:
        stmt = select(Rating).where(Rating.user_id == user_id)
        result = await session.execute(stmt)
        ratings = result.scalars().all()
        
        rating_list = [{"variant": r.variant, "rating": r.rating, "rd": r.rd} for r in ratings]
        overall = sum(r.rating for r in ratings) / len(ratings) if ratings else 1500.0
        
        return {"ratings": rating_list, "overall": overall}

@router.get("/user/{user_id}")
async def get_user_profile(user_id: str, request: Request):
    user_session = request.session.get("user")
    if user_session and str(user_session.get("id")) == user_id:
        await ensure_user_in_db(user_session)

    async with async_session() as session:
        stmt = select(User).where(User.google_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return {
                "user": {"id": user_id, "name": "Anonymous", "picture": None, "supporter_badge": None, "created_at": None},
                "ratings": [], "overall": 1500.0
            }
            
        stmt_ratings = select(Rating).where(Rating.user_id == user_id)
        result_ratings = await session.execute(stmt_ratings)
        ratings = result_ratings.scalars().all()
        
        rating_list = [{"variant": r.variant, "rating": r.rating, "rd": r.rd} for r in ratings]
        overall = sum(r.rating for r in ratings) / len(ratings) if ratings else 1500.0
        
        return {
            "user": {
                "id": user.google_id, "name": user.username or user.name, "username": user.username,
                "picture": user.picture, "supporter_badge": user.supporter_badge, "created_at": user.created_at
            },
            "ratings": rating_list, "overall": overall
        }

@router.get("/user/{user_id}/games")
async def get_user_games(
    user_id: str, skip: int = 0, limit: int = 50, variant: Optional[str] = None, result: Optional[str] = None
):
    async with async_session() as session:
        filters = [
            or_(GameModel.white_player_id == user_id, GameModel.black_player_id == user_id),
            GameModel.is_over == True
        ]
        if variant and variant != "all": filters.append(GameModel.variant == variant)
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
            elif result == "draw": filters.append(GameModel.winner == "draw")

        stmt = select(GameModel).where(*filters).order_by(desc(GameModel.created_at)).offset(skip).limit(limit)
        games_rows = (await session.execute(stmt)).scalars().all()
        
        opponent_ids = {g.black_player_id if g.white_player_id == user_id else g.white_player_id for g in games_rows}
        opponent_ids.discard(None); opponent_ids.discard("computer")
        
        users_map = {}
        if opponent_ids:
            u_stmt = select(User).where(User.google_id.in_(opponent_ids))
            for u in (await session.execute(u_stmt)).scalars():
                users_map[u.google_id] = u

        history = []
        for g in games_rows:
            is_white = (g.white_player_id == user_id)
            my_color = "white" if is_white else "black"
            game_result = "draw"
            if g.winner:
                if g.winner == "draw": game_result = "draw"
                elif g.winner == my_color: game_result = "win"
                else: game_result = "loss"

            opp_id = g.black_player_id if is_white else g.white_player_id
            opp_name = "Anonymous"
            if opp_id == "computer": opp_name = "Stockfish AI"
            elif opp_id in users_map: opp_name = users_map[opp_id].username or users_map[opp_id].name
            
            history.append({
                "id": g.id, "variant": g.variant, "created_at": g.created_at, "my_color": my_color,
                "result": game_result, "opponent": {"id": opp_id, "name": opp_name},
                "rating_diff": g.white_rating_diff if is_white else g.black_rating_diff
            })
        return {"games": history}

@router.get("/leaderboard/{variant}")
async def get_leaderboard(variant: str):
    async with async_session() as session:
        stmt = (
            select(Rating, User)
            .join(User, Rating.user_id == User.google_id)
            .where(Rating.variant == variant.lower())
            .order_by(Rating.rating.desc()).limit(50)
        )
        rows = (await session.execute(stmt)).all()
        leaderboard = [{
            "user_id": user_obj.google_id, "name": user_obj.username or user_obj.name, "picture": user_obj.picture,
            "supporter_badge": user_obj.supporter_badge, "rating": int(rating_obj.rating), "rd": int(rating_obj.rd)
        } for rating_obj, user_obj in rows]
        return {"variant": variant, "leaderboard": leaderboard}
