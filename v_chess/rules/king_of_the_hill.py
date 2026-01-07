from typing import List, Callable, Optional
from v_chess.enums import GameOverReason, MoveLegalityReason, BoardLegalityReason, Color
from v_chess.game_state import GameState
from v_chess.piece import King
from v_chess.game_over_conditions import evaluate_king_center_win
from v_chess.special_moves import (
    PieceMoveRule, GlobalMoveRule, basic_moves,
    pawn_promotions, pawn_double_push, standard_castling
)
from .standard import StandardRules


class KingOfTheHillRules(StandardRules):
    @property
    def game_over_conditions(self) -> List[Callable[[GameState, "StandardRules"], Optional[GameOverReason]]]:
        return [evaluate_king_center_win] + super().game_over_conditions

    @property
    def available_moves(self) -> List[Callable]:
        """Returns a list of rules for generating moves."""
        return [
            basic_moves,
            pawn_promotions,
            pawn_double_push,
            standard_castling
        ]

    def get_winner(self, state: GameState) -> Color | None:
        reason = self.get_game_over_reason(state)
        if reason == GameOverReason.KING_ON_HILL:
            return state.turn.opposite
        return super().get_winner(state)
