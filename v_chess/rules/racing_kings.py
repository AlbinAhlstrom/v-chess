from typing import List, Callable, Optional
from v_chess.enums import GameOverReason, MoveLegalityReason, BoardLegalityReason, Color
from v_chess.game_state import GameState
from v_chess.move import Move
from v_chess.piece import King
from v_chess.game_over_conditions import evaluate_racing_kings_win, evaluate_repetition, evaluate_fifty_move_rule, evaluate_stalemate
from v_chess.move_validators import (
    validate_piece_presence, validate_turn, 
    validate_moveset, validate_friendly_capture, validate_pawn_capture, 
    validate_path, validate_promotion, validate_racing_kings_move
)
from v_chess.state_validators import (
    standard_king_count, pawn_on_backrank,
    pawn_count_standard, piece_count_promotion_consistency, castling_rights_consistency,
    en_passant_target_validity, racing_kings_check_illegality
)
from v_chess.special_moves import (
    basic_moves, pawn_promotions, pawn_double_push
)
from .standard import StandardRules


class RacingKingsRules(StandardRules):
    @property
    def game_over_conditions(self) -> List[Callable[[GameState, "StandardRules"], Optional[GameOverReason]]]:
        return [
            evaluate_racing_kings_win,
            evaluate_repetition,
            evaluate_fifty_move_rule,
            evaluate_stalemate
        ]

    @property
    def move_validators(self) -> List[Callable[[GameState, Move, "StandardRules"], Optional[MoveLegalityReason]]]:
        """Returns a list of move validators."""
        return [
            validate_piece_presence,
            validate_turn,
            validate_moveset,
            validate_friendly_capture,
            validate_pawn_capture,
            validate_path,
            validate_promotion,
            validate_racing_kings_move
        ]

    @property
    def state_validators(self) -> List[Callable[[GameState, "StandardRules"], Optional[BoardLegalityReason]]]:
        """Returns a list of board state validators."""
        return [
            standard_king_count,
            pawn_on_backrank,
            pawn_count_standard,
            piece_count_promotion_consistency,
            castling_rights_consistency,
            en_passant_target_validity,
            racing_kings_check_illegality
        ]

    @property
    def available_moves(self) -> List[Callable]:
        """Returns a list of rules for generating moves."""
        return [
            basic_moves,
            pawn_promotions,
            pawn_double_push
        ]

    @property
    def starting_fen(self) -> str:
        return "8/8/8/8/8/8/krbnNBRK/qrbnNBRQ w - - 0 1"

    def is_check(self, state: GameState) -> bool:
        return self._is_color_in_check(state.board, state.turn)

    def get_winner(self, state: GameState) -> Color | None:
        reason = self.get_game_over_reason(state)
        if reason == GameOverReason.KING_TO_EIGHTH_RANK:
            wk_on_8 = False
            for sq, p in state.board.items():
                if isinstance(p, King) and p.color == Color.WHITE and sq.row == 0:
                    wk_on_8 = True
                    break
            if wk_on_8: return Color.WHITE
            return Color.BLACK
        return super().get_winner(state)
