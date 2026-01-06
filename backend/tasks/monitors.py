import asyncio
import json
from v_chess.enums import Color
from backend.state import games
from backend.socket_manager import manager
from backend.services.game_service import save_game_to_db
from backend.services.matchmaking_service import match_players

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
                                "in_check": game.is_check,
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
