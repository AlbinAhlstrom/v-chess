from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
import json
import asyncio
import random
from uuid import uuid4
import traceback

from v_chess.game import Game
from v_chess.move import Move
from v_chess.square import Square
from v_chess.enums import Color
from backend.database import async_session, GameModel
from backend.socket_manager import manager
from backend.state import games, game_variants, seeks, quick_match_queue, pending_takebacks, RULES_MAP
from backend.services.game_service import get_game, get_player_info, save_game_to_db, trigger_ai_move
from v_chess.rules.standard import StandardRules

router = APIRouter()

@router.websocket("/lobby")
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
                    "id": seek_id, "user_id": seek_user_id,
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
                if not current_user_id: continue
                variant = message.get("variant", "standard")
                async with async_session() as session:
                    rating_info = await get_player_info(session, current_user_id, variant)
                    user_rating = rating_info["rating"]
                quick_match_queue[:] = [p for p in quick_match_queue if p["user_id"] != current_user_id]
                quick_match_queue.append({
                    "user_id": current_user_id, "variant": variant, "time_control": message.get("time_control"),
                    "rating": user_rating, "range": message.get("range", 200), "joined_at": asyncio.get_event_loop().time()
                })
            elif message["type"] == "leave_quick_match":
                if current_user_id: quick_match_queue[:] = [p for p in quick_match_queue if p["user_id"] != current_user_id]
            elif message["type"] == "join_seek":
                seek_id = message.get("seek_id")
                if seek_id in seeks:
                    seek = seeks.pop(seek_id)
                    game_id = str(uuid4())
                    variant = seek["variant"]
                    if variant == "random": variant = random.choice([v for v in RULES_MAP.keys() if v != 'random'])
                    rules = RULES_MAP.get(variant.lower(), StandardRules)()
                    game = Game(rules=rules, time_control=seek["time_control"])
                    games[game_id], game_variants[game_id] = game, variant
                    seeker_id, joiner_id = seek["user_id"], message.get("user", {}).get("id")
                    if seek.get("color") == "white": white_id, black_id = seeker_id, joiner_id
                    elif seek.get("color") == "black": white_id, black_id = joiner_id, seeker_id
                    else:
                        if random.choice([True, False]): white_id, black_id = seeker_id, joiner_id
                        else: white_id, black_id = joiner_id, seeker_id
                    async with async_session() as session:
                        async with session.begin():
                            model = GameModel(
                                id=game_id, variant=variant, fen=game.state.fen, 
                                move_history=json.dumps(game.move_history), uci_history=json.dumps(game.uci_history),
                                time_control=json.dumps(game.time_control) if game.time_control else None, 
                                white_player_id=white_id, black_player_id=black_id, is_over=False
                            )
                            session.add(model)
                    await manager.broadcast_lobby(json.dumps({"type": "seek_accepted", "seek_id": seek_id, "game_id": game_id}))
    except WebSocketDisconnect: 
        if current_user_id: quick_match_queue[:] = [p for p in quick_match_queue if p["user_id"] != current_user_id]
        manager.disconnect_lobby(websocket)
    except Exception as e: 
        if current_user_id: quick_match_queue[:] = [p for p in quick_match_queue if p["user_id"] != current_user_id]
        print(f"Lobby WS error: {e}"); manager.disconnect_lobby(websocket)

@router.websocket("/{game_id}")
async def game_websocket(websocket: WebSocket, game_id: str):
    await manager.connect(websocket, game_id)
    game = await get_game(game_id)
    async with async_session() as session:
        model = (await session.execute(select(GameModel).where(GameModel.id == game_id))).scalar_one_or_none()
        white_id, black_id = (model.white_player_id, model.black_player_id) if model else (None, None)
    
    user_session = websocket.scope.get("session", {}).get("user")
    user_id = str(user_session.get("id")) if user_session else None
    
    await manager.broadcast(game_id, json.dumps({
        "type": "game_state", "fen": game.state.fen, "turn": game.state.turn.value, 
        "is_over": game.is_over, "in_check": game.rules.is_check(), "winner": game.winner, 
        "move_history": game.move_history, "uci_history": game.uci_history,
        "clocks": {c.value: t for c, t in game.clocks.items()} if game.clocks else None,
        "explosion_square": str(game.state.explosion_square) if hasattr(game.state, 'explosion_square') and game.state.explosion_square else None
    }))

    if not game.is_over:
        if (game.state.turn == Color.WHITE and white_id == "computer") or (game.state.turn == Color.BLACK and black_id == "computer"):
            asyncio.create_task(trigger_ai_move(game_id, game))

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message["type"] == "move":
                async with async_session() as session:
                    model = (await session.execute(select(GameModel).where(GameModel.id == game_id))).scalar_one_or_none()
                    white_id, black_id = (model.white_player_id, model.black_player_id) if model else (None, None)
                
                is_white_turn, is_black_turn = game.state.turn == Color.WHITE, game.state.turn == Color.BLACK
                if (is_white_turn and white_id == "computer") or (is_black_turn and black_id == "computer"):
                    asyncio.create_task(trigger_ai_move(game_id, game)); continue
                
                if is_white_turn and white_id and white_id != "computer" and user_id != white_id: continue
                if is_black_turn and black_id and black_id != "computer" and user_id != black_id: continue

                move_uci = message["uci"]
                if "@" not in move_uci:
                    start_sq, end_sq = Square(move_uci[:2]), Square(move_uci[2:4])
                    piece = game.state.board.get_piece(start_sq)
                    if piece and piece.fen.lower() == "p" and len(move_uci) == 4 and end_sq.is_promotion_row(piece.color): move_uci += "q"
                
                move_obj = Move(move_uci, player_to_move=game.state.turn)
                game.take_turn(move_obj, offer_draw=message.get("offer_draw", False))
                rating_diffs = await save_game_to_db(game_id)
                if game_id in pending_takebacks: del pending_takebacks[game_id]
                await manager.broadcast(game_id, json.dumps({"type": "takeback_cleared"}))
                await manager.broadcast(game_id, json.dumps({"type": "draw_cleared"}))

                await manager.broadcast(game_id, json.dumps({
                    "type": "game_state", "fen": game.state.fen, "turn": game.state.turn.value, 
                    "is_over": game.is_over, "in_check": game.rules.is_check(), "winner": game.winner, 
                    "move_history": game.move_history, "uci_history": game.uci_history,
                    "clocks": {c.value: t for c, t in game.get_current_clocks().items()} if game.clocks else None, 
                    "rating_diffs": rating_diffs,
                    "explosion_square": str(game.state.explosion_square) if getattr(game.state, 'explosion_square', None) else None,
                    "is_drop": move_obj.is_drop
                }))

                if not game.is_over:
                    if (game.state.turn == Color.WHITE and white_id == "computer") or (game.state.turn == Color.BLACK and black_id == "computer"):
                        asyncio.create_task(trigger_ai_move(game_id, game))
            elif message["type"] == "undo":
                if (white_id is None and black_id is None) or (user_id in [white_id, black_id]):
                    game.undo_move(); await save_game_to_db(game_id)
                    await manager.broadcast(game_id, json.dumps({
                        "type": "game_state", "fen": game.state.fen, "turn": game.state.turn.value, 
                        "is_over": game.is_over, "in_check": game.rules.is_check(), "winner": game.winner, 
                        "move_history": game.move_history, "uci_history": game.uci_history,
                        "clocks": {c.value: t for c, t in game.get_current_clocks().items()} if game.clocks else None, 
                        "rating_diffs": None, "explosion_square": None, "is_drop": False
                    }))
            elif message["type"] == "resign":
                if user_id in [white_id, black_id] or (not white_id and not black_id):
                    game.resign(Color.WHITE if user_id == white_id else (Color.BLACK if user_id == black_id else game.state.turn))
                    rating_diffs = await save_game_to_db(game_id)
                    await manager.broadcast(game_id, json.dumps({
                        "type": "game_state", "fen": game.state.fen, "turn": game.state.turn.value, 
                        "is_over": game.is_over, "in_check": game.rules.is_check(), "winner": game.winner, 
                        "move_history": game.move_history, "uci_history": game.uci_history,
                        "clocks": {c.value: t for c, t in game.get_current_clocks().items()} if game.clocks else None, 
                        "rating_diffs": rating_diffs,
                        "explosion_square": str(game.state.explosion_square) if getattr(game.state, 'explosion_square', None) else None,
                        "is_drop": False
                    }))
            elif message["type"] == "draw_offer":
                await manager.broadcast(game_id, json.dumps({"type": "draw_offered", "by_user_id": user_id}))
            elif message["type"] == "draw_accept":
                game.agree_draw(); rating_diffs = await save_game_to_db(game_id)
                await manager.broadcast(game_id, json.dumps({
                        "type": "game_state", "fen": game.state.fen, "turn": game.state.turn.value, 
                        "is_over": game.is_over, "in_check": game.rules.is_check(), "winner": game.winner, 
                        "move_history": game.move_history, "uci_history": game.uci_history,
                        "clocks": {c.value: t for c, t in game.get_current_clocks().items()} if game.clocks else None, 
                        "rating_diffs": rating_diffs,
                        "explosion_square": str(game.state.explosion_square) if getattr(game.state, 'explosion_square', None) else None,
                        "is_drop": False, "status": "draw_agreed"
                }))
            elif message["type"] == "takeback_offer":
                if user_id in [white_id, black_id]:
                    pending_takebacks[game_id] = user_id
                    await manager.broadcast(game_id, json.dumps({"type": "takeback_offered", "by_user_id": user_id}))
            elif message["type"] == "takeback_accept":
                if user_id in [white_id, black_id]:
                    offering_user_id = pending_takebacks.get(game_id)
                    if offering_user_id is None: game.undo_move()
                    else:
                        offering_color = Color.WHITE if offering_user_id == white_id else Color.BLACK
                        num_undo = 2 if game.state.turn == offering_color else 1
                        for _ in range(num_undo):
                            if game.history: game.undo_move()
                        if game_id in pending_takebacks: del pending_takebacks[game_id]
                    await save_game_to_db(game_id)
                    await manager.broadcast(game_id, json.dumps({"type": "takeback_cleared"}))
                    await manager.broadcast(game_id, json.dumps({
                        "type": "game_state", "fen": game.state.fen, "turn": game.state.turn.value, 
                        "is_over": game.is_over, "in_check": game.rules.is_check(), "winner": game.winner, 
                        "move_history": game.move_history, "uci_history": game.uci_history,
                        "clocks": {c.value: t for c, t in game.get_current_clocks().items()} if game.clocks else None, 
                        "rating_diffs": None, "explosion_square": None, "is_drop": False, "status": "takeback_accepted"
                    }))
            elif message["type"] == "takeback_decline":
                if user_id in [white_id, black_id]:
                    if game_id in pending_takebacks: del pending_takebacks[game_id]
                    await manager.broadcast(game_id, json.dumps({"type": "takeback_cleared"}))
    except WebSocketDisconnect: manager.disconnect(websocket, game_id)
    except Exception as e: print(f"[WS] ERROR: {e}"); traceback.print_exc(); manager.disconnect(websocket, game_id)
