from dataclasses import replace
from v_chess.enums import GameOverReason, MoveLegalityReason, BoardLegalityReason, Color
from v_chess.game_state import ThreeCheckGameState
from v_chess.move import Move
from .standard import StandardRules


class ThreeCheckRules(StandardRules):
    MoveLegalityReason = MoveLegalityReason.load("ThreeCheck")
    BoardLegalityReason = BoardLegalityReason.load("ThreeCheck")
    GameOverReason = GameOverReason.load("ThreeCheck")

    @property
    def name(self) -> str:
        return "Three-Check"

    def apply_move(self, move: Move) -> ThreeCheckGameState:
        # Get the next state from standard logic
        # Note: This returns a standard GameState usually, unless we override something deep.
        # But we need to upgrade it to ThreeCheckGameState or modify it.
        # StandardRules.apply_move returns a NEW GameState object.
        
        # We need to replicate apply_move or wrap it.
        # If we wrap it, we get a GameState, which we then have to convert to ThreeCheckGameState.
        # But `apply_move` does a lot of work (moving pieces, updating castling, clocks).
        # Let's call super, then upgrade the result.
        
        next_state_base = super().apply_move(move)
        
        # Determine current checks from previous state (if it was ThreeCheckGameState)
        current_checks = (0, 0)
        if isinstance(self.state, ThreeCheckGameState):
            current_checks = self.state.checks
            
        # Check if this move GAVE check.
        # next_state_base has the board AFTER the move.
        # So we check if the CURRENT turn player (who is now next_state_base.turn) is in check?
        # No, `apply_move` flips the turn.
        # So if White moves, next_state.turn is Black.
        # We want to know if Black is in check (White gave check).
        
        # We need a temporary Rules object attached to next_state to check for check.
        # StandardRules.apply_move attaches a new Rules object to next_state.
        
        is_check = next_state_base.rules.is_check()
        
        white_checks, black_checks = current_checks
        
        # The player who JUST moved is self.state.turn.
        if is_check:
            if self.state.turn == Color.WHITE:
                white_checks += 1
            else:
                black_checks += 1
                
        # Create new ThreeCheckGameState
        next_state = ThreeCheckGameState(
            board=next_state_base.board,
            turn=next_state_base.turn,
            castling_rights=next_state_base.castling_rights,
            ep_square=next_state_base.ep_square,
            halfmove_clock=next_state_base.halfmove_clock,
            fullmove_count=next_state_base.fullmove_count,
            rules=next_state_base.rules,
            repetition_count=next_state_base.repetition_count,
            checks=(white_checks, black_checks)
        )
        
        # Re-link rules to the new state subclass
        next_state.rules.state = next_state
        
        # Also, the rules object attached to next_state is of type `self.__class__` (ThreeCheckRules)
        # because `apply_move` uses `new_rules = self.__class__()`.
        
        return next_state

    def get_game_over_reason(self) -> GameOverReason:
        # Check for 3 checks first
        if isinstance(self.state, ThreeCheckGameState):
            if self.state.checks[0] >= 3 or self.state.checks[1] >= 3:
                return self.GameOverReason.THREE_CHECKS
                
        return super().get_game_over_reason()

    def get_winner(self) -> Color | None:
        if self.get_game_over_reason() == self.GameOverReason.THREE_CHECKS:
            # Who has 3 checks?
            if isinstance(self.state, ThreeCheckGameState):
                if self.state.checks[0] >= 3:
                    return Color.WHITE
                if self.state.checks[1] >= 3:
                    return Color.BLACK
        return super().get_winner()
