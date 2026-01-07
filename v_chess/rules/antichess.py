from typing import List, Callable, Optional
from v_chess.enums import Color, MoveLegalityReason, BoardLegalityReason, GameOverReason
from v_chess.move import Move
from v_chess.piece import King, Pawn
from v_chess.game_state import GameState
from v_chess.game_over_conditions import (
    evaluate_repetition, evaluate_fifty_move_rule, evaluate_antichess_win
)
from v_chess.move_validators import (
    validate_piece_presence, validate_turn, 
    validate_moveset, validate_friendly_capture, validate_pawn_capture, 
    validate_path, validate_promotion, validate_mandatory_capture,
    validate_antichess_castling
)
from v_chess.state_validators import (
    pawn_on_backrank, pawn_count_standard, en_passant_target_validity
)
from v_chess.special_moves import (
    PieceMoveRule, GlobalMoveRule, basic_moves,
    pawn_promotions, pawn_double_push
)
from .standard import StandardRules


class AntichessRules(StandardRules):
    @property
    def game_over_conditions(self) -> List[Callable[[GameState, "StandardRules"], Optional[GameOverReason]]]:
        return [
            evaluate_repetition,
            evaluate_fifty_move_rule,
            evaluate_antichess_win
        ]

    @property
    def move_validators(self) -> List[Callable[[GameState, Move, "StandardRules"], Optional[MoveLegalityReason]]]:
        """Returns a list of move validators."""
        return [
            validate_piece_presence,
            validate_turn,
            validate_mandatory_capture,
            validate_moveset,
            validate_friendly_capture,
            validate_pawn_capture,
            validate_path,
            validate_promotion,
            validate_antichess_castling
        ]

    @property
    def state_validators(self) -> List[Callable[[GameState, "StandardRules"], Optional[BoardLegalityReason]]]:
        """Returns a list of board state validators."""
        return [
            pawn_on_backrank,
            pawn_count_standard,
            en_passant_target_validity
        ]

    @property
    def available_moves(self) -> List[Callable]:
        """Returns a list of rules for generating moves."""
        return [
            basic_moves,
            pawn_promotions,
            pawn_double_push
        ]

    def is_check(self, state: GameState) -> bool:
        return False

    def inactive_player_in_check(self, state: GameState) -> bool:
        return False

    def get_winner(self, state: GameState) -> Color | None:
        reason = self.get_game_over_reason(state)
        if reason == GameOverReason.ALL_PIECES_CAPTURED:
             white_pieces = any(p.color == Color.WHITE for p in state.board.values())
             if not white_pieces: return Color.WHITE
             return Color.BLACK
        if reason == GameOverReason.STALEMATE:
             return state.turn
        return None

    def castling_legality_reason(self, state: GameState, move: Move, piece: King) -> MoveLegalityReason:
        return MoveLegalityReason.CASTLING_DISABLED

    def get_legal_castling_moves(self, state: GameState) -> list[Move]:
        return []