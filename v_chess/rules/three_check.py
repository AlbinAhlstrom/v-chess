from v_chess.enums import GameOverReason, Color, MoveLegalityReason, BoardLegalityReason
from v_chess.game_state import GameState, ThreeCheckGameState
from v_chess.move import Move
from .standard import StandardRules


class ThreeCheckRules(StandardRules):
    """Rules for Three-Check chess variant."""
    MoveLegalityReason = MoveLegalityReason.load("ThreeCheck")
    BoardLegalityReason = BoardLegalityReason.load("ThreeCheck")
    GameOverReason = GameOverReason.load("ThreeCheck")

    @property
    def name(self) -> str:
        """The human-readable name of the variant."""
        return "Three-Check"

    def apply_move(self, state: GameState, move: Move) -> ThreeCheckGameState:
        """Applies a move and updates the check counter."""
        next_state_base = super().apply_move(state, move)

        # Determine current checks from previous state (if it was ThreeCheckGameState)
        current_checks = (0, 0)
        if isinstance(state, ThreeCheckGameState):
            current_checks = state.checks

        # Check if this move GAVE check.
        # super().is_check(next_state_base) checks if the player who is NEXT to move is in check.
        is_check = self.is_check(next_state_base)

        white_checks, black_checks = current_checks

        # The player who JUST moved is state.turn.
        if is_check:
            if state.turn == Color.WHITE:
                white_checks += 1
            else:
                black_checks += 1

        # Create new ThreeCheckGameState
        return ThreeCheckGameState(
            board=next_state_base.board,
            turn=next_state_base.turn,
            castling_rights=next_state_base.castling_rights,
            ep_square=next_state_base.ep_square,
            halfmove_clock=next_state_base.halfmove_clock,
            fullmove_count=next_state_base.fullmove_count,
            repetition_count=next_state_base.repetition_count,
            checks=(white_checks, black_checks)
        )

    def get_game_over_reason(self, state: GameState) -> GameOverReason:
        """Determines why the game ended, including the 3-check condition."""
        # Check for 3 checks first
        if isinstance(state, ThreeCheckGameState):
            if state.checks[0] >= 3 or state.checks[1] >= 3:
                return self.GameOverReason.THREE_CHECKS

        return super().get_game_over_reason(state)

    def get_winner(self, state: GameState) -> Color | None:
        """Determines the winner of the game."""
        reason = self.get_game_over_reason(state)
        if reason == self.GameOverReason.THREE_CHECKS:
            # Who has 3 checks?
            if isinstance(state, ThreeCheckGameState):
                if state.checks[0] >= 3:
                    return Color.WHITE
                if state.checks[1] >= 3:
                    return Color.BLACK
        return super().get_winner(state)