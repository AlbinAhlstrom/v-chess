import json
import random
import asyncio
from uuid import uuid4
from sqlalchemy import select

from v_chess.game import Game
from v_chess.rules.standard import StandardRules
from backend.database import async_session, GameModel
from backend.state import quick_match_queue, seeks, games, game_variants, RULES_MAP
from backend.socket_manager import manager
from backend.services.game_service import get_player_info, save_game_to_db

async def match_players():
    if not quick_match_queue:
        return

    to_remove_qm = set()
    to_remove_seeks = set()
    matches = []

    # 1. Match QM users against Lobby seeks
    for i, p1 in enumerate(quick_match_queue):
        for seek_id, s in seeks.items():
            if seek_id in to_remove_seeks: continue
            if p1["user_id"] == s["user_id"]: continue
            
            v_match = (p1["variant"] == s["variant"]) or (p1["variant"] == "random") or (s["variant"] == "random")
            
            if v_match and p1["time_control"] == s["time_control"]:
                async with async_session() as session:
                    s_rating_info = await get_player_info(session, s["user_id"], s["variant"])
                    s_rating = s_rating_info["rating"]
                
                rating_diff = abs(p1["rating"] - s_rating)
                if rating_diff <= p1["range"]:
                    match_variant = s["variant"]
                    if match_variant == "random":
                        if p1["variant"] == "random":
                            match_variant = random.choice([v for v in RULES_MAP.keys() if v != 'random'])
                        else:
                            match_variant = p1["variant"]

                    matches.append({
                        "p1": p1,
                        "p2": {"user_id": s["user_id"], "color": s.get("color", "random")},
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
                    match_variant = p1["variant"]
                    if match_variant == "random":
                        if p2["variant"] == "random":
                            match_variant = random.choice([v for v in RULES_MAP.keys() if v != 'random'])
                        else:
                            match_variant = p2["variant"]

                    matches.append({
                        "p1": p1, "p2": p2, "is_seek": False,
                        "variant": match_variant, "time_control": p1["time_control"]
                    })
                    to_remove_qm.add(i)
                    to_remove_qm.add(j)
                    break
    
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
            
            white_id, black_id = None, None
            if m.get("is_seek"):
                seeker_color = p2.get("color", "random")
                if seeker_color == "white": white_id, black_id = p2["user_id"], p1["user_id"]
                elif seeker_color == "black": white_id, black_id = p1["user_id"], p2["user_id"]
                else:
                    if random.choice([True, False]): white_id, black_id = p1["user_id"], p2["user_id"]
                    else: white_id, black_id = p2["user_id"], p1["user_id"]
            else:
                if random.choice([True, False]): white_id, black_id = p1["user_id"], p2["user_id"]
                else: white_id, black_id = p2["user_id"], p1["user_id"]
                
            async with async_session() as session:
                async with session.begin():
                    model = GameModel(
                        id=game_id, variant=variant, fen=game.state.fen, 
                        move_history=json.dumps(game.move_history), 
                        uci_history=json.dumps(game.uci_history),
                        time_control=json.dumps(game.time_control) if game.time_control else None, 
                        white_player_id=white_id, black_player_id=black_id, is_over=False
                    )
                    session.add(model)
            
            if m.get("is_seek"):
                del seeks[m["seek_id"]]
                await manager.broadcast_lobby(json.dumps({"type": "seek_removed", "seek_id": m["seek_id"]}))

            await manager.broadcast_lobby(json.dumps({
                "type": "quick_match_found", "game_id": game_id,
                "users": [p1["user_id"], p2["user_id"]]
            }))
        except Exception as e:
            print(f"ERROR in match_players processing match: {e}")

    quick_match_queue[:] = [p for idx, p in enumerate(quick_match_queue) if idx not in to_remove_qm]
