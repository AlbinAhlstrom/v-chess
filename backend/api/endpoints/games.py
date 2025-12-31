from fastapi import APIRouter, Request, HTTPException
from sqlalchemy import select
from uuid import uuid4
import json
import random

from backend.database import async_session, GameModel
from backend.schemas import NewGameRequest, GameRequest, LegalMovesRequest
from backend.services.game_service import get_game, get_player_info
from backend.state import games, game_variants, RULES_MAP
from v_chess.rules.standard import StandardRules
from v_chess.game import Game
from v_chess.square import Square

router = APIRouter()

@router.post("/game/new")
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
            if play_as == "white": white_id, black_id = user_id, "computer"
            else: white_id, black_id = "computer", user_id
        
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
        
        return {"game_id": game_id, "fen": game.state.fen, "turn": game.state.turn}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/game/{game_id}/fens")
async def get_game_fens(game_id: str):
    game = await get_game(game_id)
    fens = [s.fen for s in game.history] + [game.state.fen]
    return {"fens": fens}

@router.get("/game/{game_id}")
async def get_game_state(game_id: str):
    game = await get_game(game_id)
    variant = game_variants.get(game_id, "standard")
    async with async_session() as session:
        model = (await session.execute(select(GameModel).where(GameModel.id == game_id))).scalar_one_or_none()
        human_id = model.white_player_id if model and model.black_player_id == "computer" else (model.black_player_id if model else None)
        human_rating = 1500
        if human_id and human_id != "computer":
            human_info = await get_player_info(session, human_id, variant)
            human_rating = human_info["rating"]

        white_player = await get_player_info(session, model.white_player_id if model else None, variant, default_name="White", fallback_rating=human_rating)
        black_player = await get_player_info(session, model.black_player_id if model else None, variant, default_name="Black", fallback_rating=human_rating)

        return {
            "game_id": game_id, "fen": game.state.fen, "turn": game.state.turn.value, 
            "is_over": game.is_over, "move_history": game.move_history, 
            "uci_history": game.uci_history, "winner": game.winner, "variant": variant, 
            "white_player": white_player, "black_player": black_player,
            "rating_diffs": {"white_diff": int(model.white_rating_diff), "black_diff": int(model.black_rating_diff)} if model and model.white_rating_diff is not None else None
        }

@router.post("/moves/all_legal")
async def get_all_legal_moves(req: GameRequest):
    game = await get_game(req.game_id)
    return {"moves": [m.uci for m in game.rules.get_legal_moves()], "status": "success"}

@router.post("/moves/legal")
async def get_legal_moves(req: LegalMovesRequest):
    game = await get_game(req.game_id)
    try: square = Square(req.square)
    except ValueError: raise HTTPException(status_code=400, detail="Invalid square")
    piece = game.state.board.get_piece(square)
    if not piece: return {"moves": [], "status": "success"}
    if piece.color != game.state.turn: raise HTTPException(status_code=400, detail="Piece belongs to the opponent")
    return {"moves": [m.uci for m in game.rules.get_legal_moves() if m.start == square], "status": "success"}
