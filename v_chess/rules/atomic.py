from typing import List, Callable, Optional
from v_chess.enums import GameOverReason, MoveLegalityReason, BoardLegalityReason, Color, Direction
from v_chess.game_state import GameState
from v_chess.move import Move
from v_chess.piece import Pawn, King
from v_chess.game_over_conditions import evaluate_atomic_king_exploded
from v_chess.move_validators import (
    validate_piece_presence, validate_turn, 
    validate_moveset, validate_friendly_capture, validate_pawn_capture, 
    validate_path, validate_promotion, validate_atomic_move
)
from v_chess.state_validators import (
    validate_standard_king_count, validate_pawn_position,
    validate_pawn_count, validate_piece_count, validate_castling_rights,
    validate_en_passant, validate_inactive_player_check, validate_atomic_adjacency
)
from .standard import StandardRules
from dataclasses import replace


class AtomicRules(StandardRules):
    MoveLegalityReason = MoveLegalityReason.load("Atomic")
    BoardLegalityReason = BoardLegalityReason.load("Atomic")
    GameOverReason = GameOverReason.load("Atomic")

    @property
    def name(self) -> str:
        return "Atomic"
        
    @property
    def game_over_conditions(self) -> List[Callable[[GameState, "StandardRules"], Optional[GameOverReason]]]:
        return [evaluate_atomic_king_exploded] + super().game_over_conditions

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
            validate_atomic_move
        ]

    @property
    def state_validators(self) -> List[Callable[[GameState, "StandardRules"], Optional[BoardLegalityReason]]]:
        """Returns a list of board state validators."""
        return [
            validate_atomic_adjacency,
            validate_standard_king_count,
            validate_pawn_position,
            validate_pawn_count,
            validate_piece_count,
            validate_castling_rights,
            validate_en_passant,
            validate_inactive_player_check
        ]

    def post_move_actions(self, old_state: GameState, move: Move, new_state: GameState) -> GameState:
        moving_piece = old_state.board.get_piece(move.start)
        target_piece = old_state.board.get_piece(move.end)
        is_en_passant = isinstance(moving_piece, Pawn) and move.end == old_state.ep_square
        
        if not (target_piece or is_en_passant):
            return new_state
            
        final_board = new_state.board.copy()
        final_board.remove_piece(move.end)
        
        neighbors = [
            move.end.adjacent(d) for d in Direction.straight_and_diagonal()
        ]
        
        for sq in neighbors:
            if not sq.is_none_square:
                p = final_board.get_piece(sq)
                if p and not isinstance(p, Pawn):
                    final_board.remove_piece(sq)
                    
        new_rights = self._update_castling_rights_after_explosion(old_state, final_board)
        
        return replace(new_state, 
                       board=final_board, 
                       castling_rights=new_rights,
                       ep_square=None, 
                       halfmove_clock=0, 
                       explosion_square=move.end)

    def _update_castling_rights_after_explosion(self, state: GameState, board) -> tuple:
        from v_chess.enums import CastlingRight
        new_rights = []
        for right in state.castling_rights:
            if right == CastlingRight.NONE: continue
            king = board.get_piece(right.expected_king_square)
            rook = board.get_piece(right.expected_rook_square)
            if isinstance(king, King) and king.color == right.color and \
               board.get_piece(right.expected_rook_square) and \
               board.get_piece(right.expected_rook_square).color == right.color:
                new_rights.append(right)
        return tuple(new_rights)

    def _kings_adjacent(self, board) -> bool:
        wk = [sq for sq, p in board.items() if isinstance(p, King) and p.color == Color.WHITE]
        bk = [sq for sq, p in board.items() if isinstance(p, King) and p.color == Color.BLACK]
        if not wk or not bk: return False
        return wk[0].is_adjacent_to(bk[0])

    def get_winner(self, state: GameState) -> Color | None:
        reason = self.get_game_over_reason(state)
        if reason == self.GameOverReason.KING_EXPLODED:
            wk = any(isinstance(p, King) and p.color == Color.WHITE for p in state.board.values())
            if not wk: return Color.BLACK
            return Color.WHITE
        return super().get_winner(state)
