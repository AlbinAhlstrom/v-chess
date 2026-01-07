from typing import List, Callable, Optional
from v_chess.enums import GameOverReason, MoveLegalityReason, BoardLegalityReason, Color
from v_chess.game_state import GameState, ThreeCheckGameState
from v_chess.move import Move
from v_chess.game_over_conditions import evaluate_three_check_win
from v_chess.special_moves import (
    PieceMoveRule, GlobalMoveRule, basic_moves,
    pawn_promotions, pawn_double_push, standard_castling
)
from .standard import StandardRules


class ThreeCheckRules(StandardRules):
    @property
    def game_over_conditions(self) -> List[Callable[[GameState, "StandardRules"], Optional[GameOverReason]]]:
        return [evaluate_three_check_win] + super().game_over_conditions

    @property
    def available_moves(self) -> List[Callable]:
        """Returns a list of rules for generating moves."""
        return [
            basic_moves,
            pawn_promotions,
            pawn_double_push,
            standard_castling
        ]

    def post_move_actions(self, old_state: GameState, move: Move, new_state: GameState) -> GameState:
        """Updates check counter after a move."""
        current_checks = (0, 0)
        if isinstance(old_state, ThreeCheckGameState):
            current_checks = old_state.checks

        is_check = self.is_check(new_state)

        white_checks, black_checks = current_checks

        if is_check:
            if old_state.turn == Color.WHITE:
                white_checks += 1
            else:
                black_checks += 1

        return ThreeCheckGameState(
            board=new_state.board,
            turn=new_state.turn,
            castling_rights=new_state.castling_rights,
            ep_square=new_state.ep_square,
            halfmove_clock=new_state.halfmove_clock,
            fullmove_count=new_state.fullmove_count,
            repetition_count=new_state.repetition_count,
            checks=(white_checks, black_checks)
        )

    def get_winner(self, state: GameState) -> Color | None:
        reason = self.get_game_over_reason(state)
        if reason == GameOverReason.THREE_CHECKS:
            if isinstance(state, ThreeCheckGameState):
                if state.checks[0] >= 3:
                    return Color.WHITE
                if state.checks[1] >= 3:
                    return Color.BLACK
        return super().get_winner(state)
