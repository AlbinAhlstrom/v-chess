from typing import List, Callable, Optional
from v_chess.enums import GameOverReason, MoveLegalityReason, BoardLegalityReason, Color, CastlingRight
from v_chess.move import Move
from v_chess.piece import King, Rook
from v_chess.square import Square
from v_chess.game_state import GameState
from v_chess.move_validators import (
    validate_piece_presence, validate_turn, 
    validate_moveset, validate_friendly_capture, validate_pawn_capture, 
    validate_path, validate_promotion, validate_king_safety,
    validate_chess960_castling
)
from v_chess.state_validators import (
    standard_king_count, pawn_on_backrank,
    pawn_count_standard, piece_count_promotion_consistency, castling_rights_consistency,
    en_passant_target_validity, inactive_player_check_safety
)
from v_chess.special_moves import (
    PieceMoveRule, GlobalMoveRule, basic_moves,
    pawn_promotions, pawn_double_push, chess960_castling
)
from .standard import StandardRules
from dataclasses import replace


class Chess960Rules(StandardRules):
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
            validate_chess960_castling,
            validate_king_safety
        ]

    @property
    def available_moves(self) -> List[Callable]:
        """Returns a list of rules for generating moves."""
        return [
            basic_moves,
            pawn_promotions,
            pawn_double_push,
            chess960_castling
        ]

    @property
    def starting_fen(self) -> str:
        import random
        # 1. Place Bishops on opposite colors
        # Light squares: 1, 3, 5, 7. Dark: 0, 2, 4, 6.
        b1 = random.choice([1, 3, 5, 7])
        b2 = random.choice([0, 2, 4, 6])

        # 2. Place remaining pieces in empty squares
        remaining_indices = [i for i in range(8) if i not in (b1, b2)]

        # 3. Place Queen
        q_idx = random.choice(remaining_indices)
        remaining_indices.remove(q_idx)

        # 4. Place Knights
        n1_idx = random.choice(remaining_indices)
        remaining_indices.remove(n1_idx)
        n2_idx = random.choice(remaining_indices)
        remaining_indices.remove(n2_idx)

        # 5. Place Rooks and King (King must be between Rooks)
        # remaining_indices has 3 elements left.
        # Sort them: [r1, k, r2]
        remaining_indices.sort()
        r1_idx, k_idx, r2_idx = remaining_indices

        # 6. Build the backrank string
        backrank = [''] * 8
        backrank[b1] = 'B'; backrank[b2] = 'B'
        backrank[q_idx] = 'Q'
        backrank[n1_idx] = 'N'; backrank[n2_idx] = 'N'
        backrank[r1_idx] = 'R'; backrank[r2_idx] = 'R'
        backrank[k_idx] = 'K'

        row_str = "".join(backrank)

        # 7. Build full FEN
        # white backrank row_str.lower() for black
        # Castling rights in 960 use the column letters of the rooks
        # e.g. HAha if rooks are on h and a.
        w_rook_cols = f"{chr(ord('A') + r2_idx)}{chr(ord('A') + r1_idx)}"
        b_rook_cols = f"{chr(ord('a') + r2_idx)}{chr(ord('a') + r1_idx)}"

        fen = f"{row_str.lower()}/pppppppp/8/8/8/8/PPPPPPPP/{row_str} w {w_rook_cols}{b_rook_cols} - 0 1"
        return fen

    def post_move_actions(self, old_state: GameState, move: Move, new_state: GameState) -> GameState:
        # Standard castling rights cleanup in Game handles implicit rook loss.
        # But 960 KxR castling might need explicit rights removal if Game didn't catch it.
        # Game handles KxR castling logic explicitly now.
        
        # We just need to ensure correct rights cleanup if the Game missed something specific to 960 notation
        # But Game looks up rights by piece/rook square.
        
        # Is there anything else?
        # Maybe remove rights if a rook moves/is captured? StandardRules logic handles this via Game.
        
        return new_state

    def invalid_castling_rights(self, state: GameState) -> list[CastlingRight]:
        invalid = []
        for right in state.castling_rights:
            if right == CastlingRight.NONE: continue
            row = 7 if right.color == Color.WHITE else 0
            
            # Find the king on the correct rank
            king_sq = next((sq for sq, p in state.board.items() 
                            if isinstance(p, King) and p.color == right.color and sq.row == row), None)
            if not king_sq:
                invalid.append(right)
                continue

            # In Chess960, K/Q might refer to the outermost rooks relative to the king
            # if they are not at h/a.
            rooks_on_rank = [sq for sq, p in state.board.items()
                             if isinstance(p, Rook) and p.color == right.color and sq.row == row]
            
            if not rooks_on_rank:
                invalid.append(right)
                continue

            # Check if specified rook exists
            rook_sq = right.expected_rook_square
            rook = state.board.get_piece(rook_sq)
            
            if not (isinstance(rook, Rook) and rook.color == right.color):
                # Fallback for K/Q shorthand in non-standard positions
                if right in (CastlingRight.WHITE_SHORT, CastlingRight.BLACK_SHORT):
                    # K: needs at least one rook to the right of king
                    if not any(r_sq.col > king_sq.col for r_sq in rooks_on_rank):
                        invalid.append(right)
                elif right in (CastlingRight.WHITE_LONG, CastlingRight.BLACK_LONG):
                    # Q: needs at least one rook to the left of king
                    if not any(r_sq.col < king_sq.col for r_sq in rooks_on_rank):
                        invalid.append(right)
                else:
                    # Specific column right (A-H), already failed standard check above
                    invalid.append(right)
                    
        return invalid

    def castling_legality_reason(self, state: GameState, move: Move, piece: King) -> MoveLegalityReason:
        target_king_sq = move.end
        row = 7 if piece.color == Color.WHITE else 0
        
        # Check if target is Rook (KxR notation)
        target_piece = state.board.get_piece(target_king_sq)
        if isinstance(target_piece, Rook) and target_piece.color == piece.color:
             # Map to standard target based on direction
             if target_king_sq.col > move.start.col:
                 target_king_sq = Square(row, 6) # Kingside
             else:
                 target_king_sq = Square(row, 2) # Queenside

        is_kingside = target_king_sq.col > move.start.col

        right = None
        if target_king_sq == Square(row, 6): # Kingside
             for r in state.castling_rights:
                 if r.color == piece.color and r.expected_rook_square.col > move.start.col:
                     right = r; break
        elif target_king_sq == Square(row, 2): # Queenside
             for r in state.castling_rights:
                 if r.color == piece.color and r.expected_rook_square.col < move.start.col:
                     right = r; break

        if not right: return MoveLegalityReason.NO_CASTLING_RIGHT

        rook_sq = right.expected_rook_square
        target_king = Square(row, 6) if is_kingside else Square(row, 2)
        target_rook = Square(row, 5) if is_kingside else Square(row, 3)

        k_min, k_max = min(move.start.col, target_king.col), max(move.start.col, target_king.col)
        for c in range(k_min, k_max + 1):
            sq = Square(row, c)
            if sq == move.start: continue
            p = state.board.get_piece(sq)
            if p and sq != rook_sq: return MoveLegalityReason.PATH_BLOCKED

        r_min, r_max = min(rook_sq.col, target_rook.col), max(rook_sq.col, target_rook.col)
        for c in range(r_min, r_max + 1):
            sq = Square(row, c)
            if sq == rook_sq: continue
            p = state.board.get_piece(sq)
            if p and sq != move.start: return MoveLegalityReason.PATH_BLOCKED

        if self.is_check(state): return MoveLegalityReason.CASTLING_FROM_CHECK

        step = 1 if target_king.col > move.start.col else -1
        curr_col = move.start.col + step
        while True:
            sq = Square(row, curr_col)
            if self.is_under_attack(state.board, sq, piece.color.opposite):
                return MoveLegalityReason.CASTLING_THROUGH_CHECK
            if curr_col == target_king.col: break
            curr_col += step

        return MoveLegalityReason.LEGAL