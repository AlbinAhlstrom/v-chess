from typing import List, Callable, Optional
from v_chess.enums import GameOverReason, MoveLegalityReason, BoardLegalityReason, Color
from v_chess.game_state import GameState
from v_chess.piece import King
from v_chess.game_over_conditions import evaluate_king_center_win
from .standard import StandardRules


class KingOfTheHillRules(StandardRules):
    MoveLegalityReason = MoveLegalityReason.load("KingOfTheHill")
    BoardLegalityReason = BoardLegalityReason.load("KingOfTheHill")
    GameOverReason = GameOverReason.load("KingOfTheHill")

    @property
    def name(self) -> str:
        return "King of the Hill"
        
    @property
    def game_over_conditions(self) -> List[Callable[[GameState, "StandardRules"], Optional[GameOverReason]]]:
        return [evaluate_king_center_win] + super().game_over_conditions

    def get_winner(self, state: GameState) -> Color | None:
        reason = self.get_game_over_reason(state)
        if reason == self.GameOverReason.KING_ON_HILL:
            return state.turn.opposite
        return super().get_winner(state)