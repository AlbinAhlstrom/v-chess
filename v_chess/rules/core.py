from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from v_chess.enums import Color, MoveLegalityReason, BoardLegalityReason, GameOverReason
from v_chess.move import Move

if TYPE_CHECKING:
    from v_chess.game_state import GameState


class Rules(ABC):
    """Abstract base class for chess variant rules.

    Rules are stateless logic providers that answer questions about
    the legality and status of a given GameState.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The human-readable name of the variant."""
        ...

    @property
    @abstractmethod
    def starting_fen(self) -> str:
        """The default starting FEN for the variant."""
        ...

    @property
    @abstractmethod
    def has_check(self) -> bool:
        """Whether the variant includes the concept of check/king safety."""
        ...

    @abstractmethod
    def get_theoretical_moves(self, state: "GameState") -> list[Move]:
        """Returns all moves that are theoretically possible on an empty board."""
        ...

    @abstractmethod
    def apply_move(self, state: "GameState", move: Move) -> "GameState":
        """Executes a move and returns the resulting state.

        Args:
            state: The current GameState.
            move: The move to apply.

        Returns:
            The new GameState.
        """
        ...

    @abstractmethod
    def validate_board_state(self, state: "GameState") -> BoardLegalityReason:
        """Validates the overall board state according to variant rules."""
        ...

    @abstractmethod
    def validate_move(self, state: "GameState", move: Move) -> MoveLegalityReason:
        """Validates if a move is legal according to variant-specific logic.

        Note: Basic pseudo-legality (moveset, collisions) is handled by the Game orchestrator.
        """
        ...

    @abstractmethod
    def move_pseudo_legality_reason(self, state: "GameState", move: Move) -> MoveLegalityReason:
        """Checks if a move is pseudo-legal (geometry, blocking)."""
        ...

    @abstractmethod
    def get_game_over_reason(self, state: "GameState") -> GameOverReason:
        """Determines why the game ended."""
        ...

    @abstractmethod
    def get_winner(self, state: "GameState") -> Color | None:
        """Determines the winner of the game."""
        ...

    def get_extra_theoretical_moves(self, state: "GameState") -> list[Move]:
        """Returns variant-specific theoretical moves (e.g., drops, special pawn moves)."""
        return []

    def post_move_actions(self, old_state: "GameState", move: Move, new_state: "GameState") -> "GameState":
        """Applies variant-specific side effects after a standard board transition.

        Examples: Atomic explosions, Crazyhouse pocket updates.
        """
        return new_state

    # -------------------------------------------------------------------------
    # Convenience / Helper methods exposed to Game
    # -------------------------------------------------------------------------

    def is_game_over(self, state: "GameState") -> bool:
        """Convenience method to check if the game has ended."""
        cls = getattr(self, "GameOverReason", GameOverReason)
        return self.get_game_over_reason(state) != cls.ONGOING

    def is_legal(self, state: "GameState") -> bool:
        """Convenience method to check the legality of the entire board state."""
        cls = getattr(self, "BoardLegalityReason", BoardLegalityReason)
        return self.validate_board_state(state) == cls.VALID

    def is_check(self, state: "GameState") -> bool:
        """Checks if the current player is in check."""
        return False

    def is_checkmate(self, state: "GameState") -> bool:
        """Checks if the game is over by checkmate."""
        cls = getattr(self, "GameOverReason", GameOverReason)
        reason = getattr(cls, "CHECKMATE", None)
        return reason is not None and self.get_game_over_reason(state) == reason

    def is_stalemate(self, state: "GameState") -> bool:
        """Checks if the game is over by stalemate."""
        cls = getattr(self, "GameOverReason", GameOverReason)
        reason = getattr(cls, "STALEMATE", None)
        return reason is not None and self.get_game_over_reason(state) == reason

    def is_draw(self, state: "GameState") -> bool:
        """Checks if the game resulted in a draw."""
        reason = self.get_game_over_reason(state)
        cls = getattr(self, "GameOverReason", GameOverReason)

        # Explicit check against ONGOING to avoid accidental matches
        if reason == cls.ONGOING:
            return False

        draw_reasons = []
        for attr in ("STALEMATE", "REPETITION", "FIFTY_MOVE_RULE", "MUTUAL_AGREEMENT", "INSUFFICIENT_MATERIAL"):
            r = getattr(cls, attr, None)
            if r is not None:
                draw_reasons.append(r)

        return reason in draw_reasons

    def is_fifty_moves(self, state: "GameState") -> bool:
        """Whether the 50-move rule has been triggered."""
        return state.halfmove_clock >= 100
