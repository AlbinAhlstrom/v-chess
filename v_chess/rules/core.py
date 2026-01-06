from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from v_chess.enums import Color, MoveLegalityReason, BoardLegalityReason, GameOverReason
from v_chess.move import Move

if TYPE_CHECKING:
    from v_chess.game_state import GameState


class Rules(ABC):
    """Abstract base class for chess variant rules.
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
    def validate_move(self, state: "GameState", move: Move) -> MoveLegalityReason:
        """Validates if a move is fully legal.

        Args:
            state: The current GameState.
            move: The move to validate.

        Returns:
            The reason for the move's legality status.
        """
        ...

    @abstractmethod
    def validate_board_state(self, state: "GameState") -> BoardLegalityReason:
        """Validates the overall board state.

        Returns:
            The reason for the board's legality status.
        """
        ...

    @abstractmethod
    def get_game_over_reason(self, state: "GameState") -> GameOverReason:
        """Determines why the game ended.

        Returns:
            The reason for the game ending.
        """
        ...

    @abstractmethod
    def get_winner(self, state: "GameState") -> Color | None:
        """Determines the winner of the game.

        Returns:
            The color of the winner, or None if it's a draw or ongoing.
        """
        ...

    def is_check(self, state: "GameState") -> bool:
        """Checks if the current player is in check.

        Returns:
            True if the player is in check, False otherwise.
        """
        return False

    def is_game_over(self, state: "GameState") -> bool:
        """Checks if the game has ended."""
        cls = getattr(self, "GameOverReason", GameOverReason)
        return self.get_game_over_reason(state) != cls.ONGOING

    def is_legal(self, state: "GameState") -> bool:
        """Checks the legality of the entire board state.

        Args:
            state: The GameState to check.

        Returns:
            True if the board is legal, False otherwise.
        """
        cls = getattr(self, "BoardLegalityReason", BoardLegalityReason)
        return self.validate_board_state(state) == cls.VALID
