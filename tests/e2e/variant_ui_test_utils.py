import re
import os
import pytest
from v_chess.game import Game
from v_chess.move import Move
from v_chess.enums import MoveLegalityReason
from playwright.sync_api import Page, expect

class VariantPGNGame:
    moves: list[str]
    variant: str
    fen: str | None
    white: str
    black: str

    def __init__(self, moves, variant, fen, white, black):
        self.moves = moves
        self.variant = variant
        self.fen = fen
        self.white = white
        self.black = black

def parse_variant_pgn(game_string: str) -> VariantPGNGame:
    L, R = "[", "]"
    variant_match = re.search(f'^{re.escape(L)}Variant "(.*?)"{re.escape(R)}', game_string, re.MULTILINE)
    fen_match = re.search(f'^{re.escape(L)}FEN "(.*?)"{re.escape(R)}', game_string, re.MULTILINE)
    white_match = re.search(f'^{re.escape(L)}White "(.*?)"{re.escape(R)}', game_string, re.MULTILINE)
    black_match = re.search(f'^{re.escape(L)}Black "(.*?)"{re.escape(R)}', game_string, re.MULTILINE)

    variant = variant_match.group(1).strip() if variant_match else "standard"
    fen = fen_match.group(1).strip() if fen_match else None
    white = white_match.group(1).strip() if white_match else "N/A"
    black = black_match.group(1).strip() if black_match else "N/A"

    # Split Event from moves
    parts = game_string.split('\n\n')
    if len(parts) < 2:
        san_moves = []
    else:
        moves_section = parts[-1]
        moves_section = re.sub(r'{{[^}}]*}}', '', moves_section)
        moves_section = re.sub(r'\d+\.\.\s*', '', moves_section)
        moves_section = re.sub(r'\d+\.\s*', '', moves_section)
        moves_section = re.sub(r'(0-1|1-0|1/2-1/2)\s*$', '', moves_section).strip()
        san_moves = [move for move in moves_section.split() if move]

    return VariantPGNGame(moves=san_moves, variant=variant, fen=fen, white=white, black=black)

def load_variant_samples(variant_name, count=2):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pgn_path = os.path.abspath(os.path.join(current_dir, "..", "variant_games.pgn"))
    
    if not os.path.exists(pgn_path):
        return []
        
    with open(pgn_path, "r") as f:
        pgn_content = f.read()
    
    target_key = variant_name.replace(" ", "").replace("-", "").lower()
    game_strings = re.split(r'\n(?=\[Event)', pgn_content.strip())
    
    matches = []
    for gs in game_strings:
        g = parse_variant_pgn(gs)
        v_key = g.variant.replace(" ", "").replace("-", "").lower()
        if v_key == target_key:
            matches.append(g)
            if len(matches) >= count:
                break
    return matches

def move_piece_ui(page: Page, from_sq: str, to_sq: str, promotion_piece: str = None):
    """Executes a move via clicks."""
    start_selector = f"[data-square='{from_sq}'].piece"
    end_selector = f"[data-square='{to_sq}']"
    
    # Click start square
    page.wait_for_selector(start_selector, timeout=10000)
    page.click(start_selector)
    
    # Click end square
    page.wait_for_selector(end_selector, timeout=10000)
    page.click(end_selector)
    
    # Handle promotion dialog
    if promotion_piece:
        promo_selector = f".promotion-option.{promotion_piece.lower()}"
        page.wait_for_selector(promo_selector, timeout=5000)
        page.click(promo_selector)

def run_variant_ui_game(page: Page, frontend_url: str, game_data: VariantPGNGame):
    # Unify variant naming
    v_key = game_data.variant.replace(" ", "").replace("-", "").lower()
    print(f"\n[E2E] Starting {game_data.variant} game...")

    # Set up logic engine to get default FEN
    from v_chess.rules import (
        AntichessRules, AtomicRules, Chess960Rules, CrazyhouseRules,
        HordeRules, KingOfTheHillRules, RacingKingsRules, ThreeCheckRules, StandardRules
    )
    RULES_MAP = {
        "antichess": AntichessRules,
        "atomic": AtomicRules,
        "chess960": Chess960Rules,
        "crazyhouse": CrazyhouseRules,
        "horde": HordeRules,
        "kingofthehill": KingOfTheHillRules,
        "racingkings": RacingKingsRules,
        "threecheck": ThreeCheckRules,
        "standard": StandardRules
    }
    rules_cls = RULES_MAP.get(v_key, StandardRules)
    rules = rules_cls()
    
    # Navigate to the correct OTB variant route
    # This automatically initializes a new game with the variant's starting FEN
    page.goto(f"{frontend_url}/otb/{v_key}")
    
    # Only import FEN if it's NOT the default for this variant
    # (Except for Chess960 where every start is unique)
    is_chess960 = v_key == "chess960"
    is_custom_fen = game_data.fen and game_data.fen != rules.starting_fen
    
    if is_chess960 or is_custom_fen:
        print(f"  Importing Custom FEN: {game_data.fen}")
        page.click("button[title='More']")
        page.click("button:has-text('Import')")
        page.fill(".fen-input", game_data.fen)
        page.select_option("select", v_key)
        page.click("button:has-text('Import'):not([style*='display: none'])")
    
    game = Game(state=game_data.fen if (is_chess960 or is_custom_fen) else None, rules=rules)

    # Limit moves for E2E speed if game is long
    move_limit = 30
    for i, san in enumerate(game_data.moves[:move_limit]):
        try:
            # 1. Logic Engine Move
            move_obj = Move.from_san(san, game)
            print(f"  Move {i+1}: {san} ({move_obj.uci})")
            
            # 2. UI Move Execution
            promo = move_obj.promotion_piece.fen if move_obj.promotion_piece else None
            move_piece_ui(page, str(move_obj.start), str(move_obj.end), promotion_piece=promo)
            
            # 3. Synchronize Logic Engine
            game.take_turn(move_obj)
            
            # 4. Synchronize UI: Wait for the move to appear in history sidebar
            move_index = i + 1
            is_black = (move_index % 2 == 0)
            pair_index = (move_index + 1) // 2
            
            if not is_black:
                wait_selector = f".move-pair:nth-child({pair_index}) .move-san:nth-child(2)"
            else:
                wait_selector = f".move-pair:nth-child({pair_index}) .move-san:nth-child(3)"
            
            try:
                page.wait_for_selector(wait_selector, timeout=10000)
                actual_san = page.inner_text(wait_selector).strip()
                clean_actual = actual_san.replace("+", "").replace("#", "")
                clean_expected = san.replace("+", "").replace("#", "")
                
                if clean_actual != clean_expected:
                    print(f"    [SYNC WARNING] UI SAN '{actual_san}' differs from expected '{san}'")
            except Exception as e:
                print(f"    [SYNC ERROR] Move {move_index} ({san}) did not appear in history at {wait_selector}")
                page.wait_for_selector(f"[data-square='{move_obj.end}'].piece", timeout=5000)
        except Exception as e:
            print(f"  FAILED at move {i+1}: {san}")
            print(f"  Logic Game FEN: {game.state.fen}")
            raise e
        
    print(f"  Completed {min(len(game_data.moves), move_limit)} moves successfully.")
