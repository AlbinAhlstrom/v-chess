from typing import List, Callable, Optional
from v_chess.enums import GameOverReason, MoveLegalityReason, BoardLegalityReason, Color
from v_chess.game_state import GameState, CrazyhouseGameState
from v_chess.move import Move
from v_chess.piece import Pawn, Piece
from v_chess.square import Square
from v_chess.game_over_conditions import (
    evaluate_repetition, evaluate_fifty_move_rule, 
    evaluate_checkmate, evaluate_stalemate
)
from v_chess.move_validators import (
    validate_piece_presence, validate_turn, 
    validate_moveset, validate_friendly_capture, validate_pawn_capture, 
    validate_path, validate_promotion, validate_standard_castling, 
    validate_king_safety, validate_crazyhouse_drop
)
from v_chess.state_validators import (
    standard_king_count, pawn_on_backrank,
    pawn_count_standard, piece_count_promotion_consistency, castling_rights_consistency,
    en_passant_target_validity, inactive_player_check_safety
)
from v_chess.special_moves import (
    PieceMoveRule, GlobalMoveRule, basic_moves,
    pawn_promotions, pawn_double_push, standard_castling, crazyhouse_drops
)
from .standard import StandardRules
from dataclasses import replace


class CrazyhouseRules(StandardRules):
    """Rules for Crazyhouse chess variant."""

    @property
    def move_validators(self) -> List[Callable[[GameState, Move, "StandardRules"], Optional[MoveLegalityReason]]]:
        """Returns a list of move validators."""
        return [
            validate_crazyhouse_drop,
            validate_piece_presence,
            validate_turn,
            validate_moveset,
            validate_friendly_capture,
            validate_pawn_capture,
            validate_path,
            validate_promotion,
            validate_standard_castling,
            validate_king_safety
        ]

    @property
    def available_moves(self) -> List[Callable]:
        """Returns a list of rules for generating moves."""
        return [
            basic_moves,
            pawn_promotions,
            pawn_double_push,
            standard_castling,
            crazyhouse_drops
        ]

    @property
    def state_validators(self) -> List[Callable[[GameState, "StandardRules"], Optional[BoardLegalityReason]]]:
        """Returns a list of board state validators."""
        return [
            standard_king_count,
            pawn_on_backrank,
            castling_rights_consistency,
            en_passant_target_validity,
            inactive_player_check_safety
        ]

    @property
    def fen_type(self) -> str:
        """The FEN notation type used."""
        return "crazyhouse"

    def post_move_actions(self, old_state: GameState, move: Move, new_state: GameState) -> GameState:
        """Updates pockets after a move (capture or drop)."""
        # Ensure we are working with a CrazyhouseGameState
        current_pockets = ((), ())
        if isinstance(old_state, CrazyhouseGameState):
            current_pockets = old_state.pockets
            
        new_pockets = [list(current_pockets[0]), list(current_pockets[1])]
        
        if move.is_drop:
            # Remove dropped piece from pocket
            pocket_idx = 0 if old_state.turn == Color.WHITE else 1
            my_pocket = new_pockets[pocket_idx]
            
            found = False
            for i, p in enumerate(my_pocket):
                if type(p) == type(move.drop_piece):
                    my_pocket.pop(i)
                    found = True
                    break
            
            if not found:
                # Should have been caught by validate_move/pseudo check
                pass
                
        else:
            # Check capture
            moving_piece = old_state.board.get_piece(move.start)
            target_piece = old_state.board.get_piece(move.end)
            
            captured_piece = None
            if target_piece:
                captured_piece = target_piece
            elif isinstance(moving_piece, Pawn) and move.end == old_state.ep_square:
                # En Passant
                from v_chess.enums import Direction
                direction = Direction.DOWN if moving_piece.color == Color.WHITE else Direction.UP
                captured_sq = move.end.adjacent(direction)
                captured_piece = old_state.board.get_piece(captured_sq)
                
            if captured_piece:
                pocket_color_idx = 0 if old_state.turn == Color.WHITE else 1
                captured_piece_type = type(captured_piece)
                new_piece = captured_piece_type(old_state.turn)
                new_pockets[pocket_color_idx].append(new_piece)
                new_pockets[pocket_color_idx].sort(key=lambda p: p.fen.upper())

        return CrazyhouseGameState(
            board=new_state.board,
            turn=new_state.turn,
            castling_rights=new_state.castling_rights,
            ep_square=new_state.ep_square,
            halfmove_clock=new_state.halfmove_clock,
            fullmove_count=new_state.fullmove_count,
            repetition_count=new_state.repetition_count,
            pockets=(tuple(new_pockets[0]), tuple(new_pockets[1]))
        )
