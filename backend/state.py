from v_chess.game import Game
from v_chess.rules import (
    AntichessRules, StandardRules, AtomicRules, Chess960Rules,
    CrazyhouseRules, HordeRules, KingOfTheHillRules, RacingKingsRules,
    ThreeCheckRules
)

# Global in-memory storage
games: dict[str, Game] = {}
game_variants: dict[str, str] = {}  # game_id -> variant name
seeks: dict[str, dict] = {}
quick_match_queue: list[dict] = []
pending_takebacks: dict[str, str] = {}

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
