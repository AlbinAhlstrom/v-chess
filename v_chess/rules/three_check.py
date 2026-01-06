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

    def post_move_actions(self, old_state: GameState, move: Move, new_state: GameState) -> GameState:
        """Updates check counter after a move."""
        current_checks = (0, 0)
        if isinstance(old_state, ThreeCheckGameState):
            current_checks = old_state.checks

        # Check if the move GAVE check (in the NEW state)
        # new_state.turn is the player who will move NEXT.
        # So we check if is_check(new_state) is true.
        is_check = self.is_check(new_state)

        white_checks, black_checks = current_checks

        # The player who JUST moved is old_state.turn.
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
