import json
import asyncio
import traceback
import random
from typing import Optional
from fastapi import HTTPException
from sqlalchemy import select
from uuid import uuid4

from v_chess.game import Game
from v_chess.move import Move
from v_chess.enums import Color
from backend.database import async_session, GameModel, User, Rating
from backend.rating import update_game_ratings
from backend.engine import engine_manager
from backend.state import games, game_variants, RULES_MAP
from backend.socket_manager import manager

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

async def get_game(game_id: str) -> Game:
    if game_id not in games:
        async with async_session() as session:
            stmt = select(GameModel).where(GameModel.id == game_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model:
                from v_chess.rules.standard import StandardRules
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
                raise HTTPException(status_code=404, detail=f"Game {game_id} not found")
    return games[game_id]

async def get_player_info(session, user_id, variant, default_name="Anonymous", fallback_rating=1500):
    if not user_id:
        return {"name": default_name, "rating": fallback_rating}
    
    if user_id == "computer":
        rounded_rating = round(fallback_rating / 50) * 50
        return {"id": "computer", "name": "Stockfish AI", "rating": rounded_rating}
    
    user = (await session.execute(select(User).where(User.google_id == user_id))).scalar_one_or_none()
    if not user:
        return {"name": default_name, "rating": 1500}
        
    rating_obj = (await session.execute(select(Rating).where(Rating.user_id == user_id, Rating.variant == variant))).scalar_one_or_none()
    
    return {
        "id": user_id,
        "name": user.username or user.name,
        "picture": user.picture,
        "supporter_badge": user.supporter_badge,
        "rating": int(rating_obj.rating) if rating_obj else 1500
    }

async def trigger_ai_move(game_id: str, game: Game):
    if game.is_over:
        return

    variant = game_variants.get(game_id, "standard")
    fen = game.state.fen
    
    user_rating = 1500
    try:
        async with async_session() as session:
            model = (await session.execute(select(GameModel).where(GameModel.id == game_id))).scalar_one_or_none()
            if model:
                human_id = model.white_player_id if model.black_player_id == "computer" else model.black_player_id
                if human_id and human_id != "computer":
                    rating_info = await get_player_info(session, human_id, variant)
                    user_rating = rating_info["rating"]
    except Exception as e:
        print(f"[AI] Error fetching rating for difficulty: {e}")

    bot_rating = round(user_rating / 50) * 50
    node_limit = max(500, (bot_rating ** 2) // 40)
    elo_target = bot_rating

    try:
        best_move_uci = await engine_manager.get_best_move(fen, variant=variant, elo=elo_target, nodes=node_limit)
        
        if best_move_uci:
            if user_rating < 1800:
                await asyncio.sleep(random.uniform(0.5, 2.0))

            move_obj = Move(best_move_uci, player_to_move=game.state.turn)
            game.take_turn(move_obj)
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
                "is_drop": move_obj.is_drop
            }))
    except Exception as e:
        print(f"[AI] ERROR in trigger_ai_move: {e}")
        traceback.print_exc()
