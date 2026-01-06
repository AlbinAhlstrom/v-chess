from v_chess.enums import GameOverReason, MoveLegalityReason, BoardLegalityReason, Color, Direction
from v_chess.game_state import GameState
from v_chess.move import Move
from v_chess.piece import Pawn, King
from .standard import StandardRules
from dataclasses import replace


class AtomicRules(StandardRules):
    MoveLegalityReason = MoveLegalityReason.load("Atomic")
    BoardLegalityReason = BoardLegalityReason.load("Atomic")
    GameOverReason = GameOverReason.load("Atomic")

    @property
    def name(self) -> str:
        return "Atomic"

    def post_move_actions(self, old_state: GameState, move: Move, new_state: GameState) -> GameState:
        # Check if it was a capture
        # We need to look at the OLD board to see if the target square was occupied
        # OR if it was an en passant capture
        
        moving_piece = old_state.board.get_piece(move.start)
        target_piece = old_state.board.get_piece(move.end)
        is_en_passant = isinstance(moving_piece, Pawn) and move.end == old_state.ep_square
        
        if not (target_piece or is_en_passant):
            return new_state
            
        # Capture logic: Explosion
        # The move has already been applied to new_state.board (attacker moved to dest)
        # But in Atomic, the attacker also explodes (disappears).
        
        final_board = new_state.board.copy()
        
        # 1. Remove capturing piece (which is now at move.end in new_state)
        # Wait, en passant moves the pawn to move.end.
        # Standard apply_move puts piece at move.end.
        final_board.remove_piece(move.end)
        
        # 2. Neighbors explosion
        neighbors = [
            move.end.adjacent(d) for d in Direction.straight_and_diagonal()
        ]
        
        for sq in neighbors:
            if not sq.is_none_square:
                p = final_board.get_piece(sq)
                if p and not isinstance(p, Pawn):
                    final_board.remove_piece(sq)
                    
        # Update castling rights
        new_rights = self._update_castling_rights_after_explosion(old_state, final_board)
        
        return replace(new_state, 
                       board=final_board, 
                       castling_rights=new_rights,
                       ep_square=None, # EP lost on capture
                       halfmove_clock=0, # Reset on capture
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

    def validate_move(self, state: GameState, move: Move) -> MoveLegalityReason:
        # 1. Standard pseudo-legality
        pseudo = self.move_pseudo_legality_reason(state, move)
        if pseudo != MoveLegalityReason.LEGAL:
            return pseudo

        # 2. Kings cannot capture
        piece = state.board.get_piece(move.start)
        if isinstance(piece, King):
            if state.board.get_piece(move.end) or move.end == state.ep_square:
                return self.MoveLegalityReason.OWN_PIECE_CAPTURE

        # 3. Simulate move to check for king explosion
        # We need to simulate the full Game orchestration for this specific move
        # But we are in Rules. We can use post_move_actions manually.
        
        # Base transition (simplified)
        # This duplicates some logic from Game.apply_move but is necessary for validation
        # without circular dependency. Or we assume Game handles simulation?
        # No, validate_move is called by Game before applying.
        
        # We need to see the FUTURE state.
        # We can create a dummy "standard" transition locally.
        
        # ... Or better, we trust the test/game loop to handle simulation?
        # No, validate_move MUST return whether the move is legal.
        
        # Let's perform a lightweight simulation
        from v_chess.rules.standard import StandardRules
        # StandardRules.apply_move is gone. 
        # But we inherit from StandardRules. 
        # StandardRules methods are now predicates.
        
        # We need a way to generate "next_state" to check King status.
        # Can we call self.post_move_actions on a hypothetical standard result?
        # Yes.
        
        # Hypothetical Standard Result
        std_next_board = state.board.copy()
        std_next_board.move_piece(piece, move.start, move.end)
        # (Ignore castling/EP/promo details for King check, mostly)
        # Actually EP matters for explosion location.
        
        # To reuse the robust logic in Game.apply_move, we are stuck.
        # BUT we removed apply_move from Rules.
        
        # Solution: Implement a lightweight `_simulate_apply(state, move)` in Rules?
        # Or just do the board update here.
        
        # Simplest valid board update for atomic check:
        sim_board = state.board.copy()
        sim_board.move_piece(piece, move.start, move.end)
        
        # Handle EP capture removal for accurate explosion
        is_ep = isinstance(piece, Pawn) and move.end == state.ep_square
        if is_ep:
            d = Direction.DOWN if piece.color == Color.WHITE else Direction.UP
            sim_board.remove_piece(move.end.adjacent(d))
            
        # Create a dummy next state to pass to post_move_actions
        dummy_next = replace(state, board=sim_board, turn=state.turn.opposite)
        
        # Apply explosion logic
        final_state = self.post_move_actions(state, move, dummy_next)
        
        # Check own king
        own_king_exists = any(isinstance(p, King) and p.color == state.turn 
                              for p in final_state.board.values())

        if not own_king_exists:
            return self.MoveLegalityReason.KING_EXPLODED

        opp_king_exists = any(isinstance(p, King) and p.color == state.turn.opposite 
                               for p in final_state.board.values())

        if not opp_king_exists:
            return self.MoveLegalityReason.LEGAL # Win move!

        # Standard check validation
        # Atomic specific: if kings are connected, check is ignored?
        if self.inactive_player_in_check(final_state):
             return self.MoveLegalityReason.KING_LEFT_IN_CHECK

        # 5. Kings cannot be adjacent
        if self._kings_adjacent(final_state.board):
            return self.MoveLegalityReason.KING_EXPLODED

        return self.MoveLegalityReason.LEGAL

    def _kings_adjacent(self, board) -> bool:
        wk = [sq for sq, p in board.items() if isinstance(p, King) and p.color == Color.WHITE]
        bk = [sq for sq, p in board.items() if isinstance(p, King) and p.color == Color.BLACK]
        if not wk or not bk: return False
        return wk[0].is_adjacent_to(bk[0])

    def validate_board_state(self, state: GameState) -> BoardLegalityReason:
        res = super().validate_board_state(state)

        if res == BoardLegalityReason.VALID or res == BoardLegalityReason.OPPOSITE_CHECK:
            if self._kings_adjacent(state.board):
                return self.BoardLegalityReason.KINGS_ADJACENT

        return res

    def get_game_over_reason(self, state: GameState) -> GameOverReason:
        wk = any(isinstance(p, King) and p.color == Color.WHITE for p in state.board.values())
        bk = any(isinstance(p, King) and p.color == Color.BLACK for p in state.board.values())

        if not wk or not bk:
            return self.GameOverReason.KING_EXPLODED

        return super().get_game_over_reason(state)

    def get_winner(self, state: GameState) -> Color | None:
        reason = self.get_game_over_reason(state)
        if reason == self.GameOverReason.KING_EXPLODED:
            wk = any(isinstance(p, King) and p.color == Color.WHITE for p in state.board.values())
            if not wk: return Color.BLACK
            return Color.WHITE
        return super().get_winner(state)
