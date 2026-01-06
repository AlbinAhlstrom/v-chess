from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Callable, Optional

from v_chess.enums import Color, MoveLegalityReason, BoardLegalityReason, GameOverReason
from v_chess.move import Move

if TYPE_CHECKING:
    from v_chess.game_state import GameState


class Rules(ABC):
    """Abstract base class for chess variant rules.

    Rules are stateless logic providers that answer questions about
    the legality and status of a given GameState.
    """
    GameOverReason = GameOverReason
    MoveLegalityReason = MoveLegalityReason
    BoardLegalityReason = BoardLegalityReason

    @property
    @abstractmethod
    def starting_fen(self) -> str:
        """The default starting FEN for the variant."""
        ...

    @property
    @abstractmethod
    def game_over_conditions(self) -> List[Callable[["GameState", "Rules"], Optional[GameOverReason]]]:
        """Returns a list of conditions that can end the game."""
        ...

    @property
    @abstractmethod
    def move_validators(self) -> List[Callable[["GameState", "Move", "Rules"], Optional[MoveLegalityReason]]]:
        """Returns a list of move validators."""
        ...

    @property
    @abstractmethod
    def state_validators(self) -> List[Callable[["GameState", "Rules"], Optional[BoardLegalityReason]]]:
        """Returns a list of board state validators."""
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

    def validate_board_state(self, state: "GameState") -> BoardLegalityReason:
        """Validates the overall board state using the component pipeline."""
        for v in self.state_validators:
            reason = v(state, self)
            if reason:
                return reason
        return BoardLegalityReason.VALID

    def validate_move(self, state: "GameState", move: Move) -> MoveLegalityReason:
        """Validates a move using the component pipeline."""
        for v in self.move_validators:
            reason = v(state, move, self)
            if reason:
                return reason
        return MoveLegalityReason.LEGAL

    def move_pseudo_legality_reason(self, state: "GameState", move: Move) -> MoveLegalityReason:
        """Checks pseudo-legality using the validator pipeline."""
        for v in self.move_validators:
            # Skip validators that check for 'full' legality (safety, variant goals)
            name = v.__name__.lower()
            if "safety" in name or "mandatory" in name or "atomic" in name or "racing" in name:
                continue
            reason = v(state, move, self)
            if reason:
                return reason
        return MoveLegalityReason.LEGAL

    def get_game_over_reason(self, state: "GameState") -> GameOverReason:
        """Determines why the game ended."""
        for condition in self.game_over_conditions:
            reason = condition(state, self)
            if reason:
                return reason
        return GameOverReason.ONGOING

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

    def has_legal_moves(self, state: "GameState") -> bool:
        """Checks if there is at least one legal move."""
        return any(self.validate_move(state, move) == MoveLegalityReason.LEGAL for move in self.get_theoretical_moves(state))

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
        reason = self.get_game_over_reason(state)
        cls = getattr(self, "GameOverReason", GameOverReason)
        checkmate_reason = getattr(cls, "CHECKMATE", GameOverReason.CHECKMATE)
        return reason == checkmate_reason

    def is_stalemate(self, state: "GameState") -> bool:
        """Checks if the game is over by stalemate."""
        reason = self.get_game_over_reason(state)
        cls = getattr(self, "GameOverReason", GameOverReason)
        stalemate_reason = getattr(cls, "STALEMATE", GameOverReason.STALEMATE)
        return reason == stalemate_reason

    def is_draw(self, state: "GameState") -> bool:
        """Checks if the game resulted in a draw."""
        reason = self.get_game_over_reason(state)
        cls = getattr(self, "GameOverReason", GameOverReason)
        
        # Explicit check against ONGOING to avoid accidental matches
        if reason == GameOverReason.ONGOING:
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
