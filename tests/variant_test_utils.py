import re
import os
import random
from dataclasses import dataclass
import pytest

from v_chess.game import Game
from v_chess.move import Move
from v_chess.rules import (
    AntichessRules, StandardRules, AtomicRules, Chess960Rules,
    CrazyhouseRules, HordeRules, KingOfTheHillRules, RacingKingsRules,
    ThreeCheckRules
)

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

@dataclass
class VariantPGNGame:
    moves: list[str]
    variant: str
    fen: str | None
    white: str
    black: str

def parse_variant_pgn(game_string: str) -> VariantPGNGame:
    variant_match = re.search(r'\[Variant "(.*?)"\].*?', game_string)
    fen_match = re.search(r'\[FEN "(.*?)"\].*?', game_string)
    white_match = re.search(r'\[White "(.*?)"\].*?', game_string)
    black_match = re.search(r'\[Black "(.*?)"\].*?', game_string)

    variant = variant_match.group(1).lower() if variant_match else "standard"
    fen = fen_match.group(1) if fen_match else None
    white = white_match.group(1) if white_match else "N/A"
    black = black_match.group(1) if black_match else "N/A"

    moves_section = game_string.split('\n\n')[-1]
    moves_section = re.sub(r'\{{[^}}]*\}}', '', moves_section)
    moves_section = re.sub(r'\d+\.\.\.\s*', '', moves_section)
    moves_section = re.sub(r'\d+\.\s*', '', moves_section)
    moves_section = re.sub(r'(0-1|1-0|1/2-1/2)\s*$', '', moves_section).strip()

    san_moves = [move for move in moves_section.split() if move]

    return VariantPGNGame(moves=san_moves, variant=variant, fen=fen, white=white, black=black)

def load_games_by_variant():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pgn_path = os.path.join(current_dir, "variant_games.pgn")
    
    by_variant = {}
    if os.path.exists(pgn_path):
        with open(pgn_path, "r") as f:
            pgn_content = f.read()
        
        game_strings = re.split(r'\n(?=\[Event)', pgn_content.strip())
        for gs in game_strings:
            if gs.strip():
                g = parse_variant_pgn(gs)
                v_key = g.variant.replace(" ", "").replace("-", "").lower()
                if v_key not in by_variant:
                    by_variant[v_key] = []
                by_variant[v_key].append(g)
    return by_variant

def run_game_test(game_data):
    v_key = game_data.variant.replace(" ", "").replace("-", "").lower()
    rules_cls = RULES_MAP.get(v_key, StandardRules)
    rules = rules_cls()
    game = Game(state=game_data.fen, rules=rules)
    
    for san in game_data.moves:
        try:
            move = Move.from_san(san, game)
            game.take_turn(move)
        except Exception as e:
            pytest.fail(f"Failed at move '{san}' in {game_data.variant} game ({game_data.white} vs {game_data.black}). FEN: {game.state.fen}. Error: {e}")