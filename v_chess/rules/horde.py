from typing import List, Callable, Optional
from v_chess.enums import GameOverReason, MoveLegalityReason, BoardLegalityReason, Color, Direction
from v_chess.game_state import GameState
from v_chess.move import Move
from v_chess.piece import Pawn, King
from v_chess.square import Square
from v_chess.game_over_conditions import evaluate_horde_win
from v_chess.move_validators import (
    validate_piece_presence, validate_turn,
    validate_moveset, validate_friendly_capture, validate_pawn_capture,
    validate_path, validate_promotion, validate_standard_castling,
    validate_king_safety, validate_horde_pawn
)
from v_chess.state_validators import (
    black_king_count_horde, black_pawn_count_horde,
    piece_count_promotion_consistency, castling_rights_consistency,
    en_passant_target_validity, inactive_player_check_safety
)
from v_chess.special_moves import (
    PieceMoveRule, GlobalMoveRule, basic_moves,
    pawn_promotions, pawn_double_push, standard_castling, horde_pawn_double_push
)
from .standard import StandardRules


class HordeRules(StandardRules):
    """Rules for Horde chess variant."""

    @property
    def game_over_conditions(self) -> List[Callable[[GameState, "StandardRules"], Optional[GameOverReason]]]:
        return [evaluate_horde_win] + super().game_over_conditions

    @property
    def move_validators(self) -> List[Callable[[GameState, Move, "StandardRules"], Optional[MoveLegalityReason]]]:
        """Returns a list of move validators."""
        return [
            validate_piece_presence,
            validate_turn,
            validate_horde_pawn,
            validate_moveset,
            validate_friendly_capture,
            validate_pawn_capture,
            validate_path,
            validate_promotion,
            validate_standard_castling,
            validate_king_safety
        ]

    @property
    def state_validators(self) -> List[Callable[[GameState, "StandardRules"], Optional[BoardLegalityReason]]]:
        """Returns a list of board state validators."""
        return [
            black_king_count_horde,
            black_pawn_count_horde,
            castling_rights_consistency,
            en_passant_target_validity,
            inactive_player_check_safety
        ]

    @property
    def available_moves(self) -> List[Callable]:
        """Returns a list of rules for generating moves."""
        return [
            basic_moves,
            pawn_promotions,
            pawn_double_push,
            horde_pawn_double_push,
            standard_castling
        ]

    @property
    def starting_fen(self) -> str:
        """The default starting FEN for Horde."""
        return "rnbqkbnr/pppppppp/8/1PP2PP1/PPPPPPPP/PPPPPPPP/PPPPPPPP/PPPPPPPP w kq - 0 1"

    def is_check(self, state: GameState) -> bool:
        """Checks if the current player is in check (always False for White)."""
        if state.turn == Color.WHITE:
            return False # White has no King
        return super().is_check(state)

    def get_winner(self, state: GameState) -> Color | None:
        """Determines the winner of the game."""
        reason = self.get_game_over_reason(state)
        if reason == GameOverReason.CHECKMATE:
            return Color.WHITE
        if reason == GameOverReason.ALL_PIECES_CAPTURED:
            return Color.BLACK
        return super().get_winner(state)