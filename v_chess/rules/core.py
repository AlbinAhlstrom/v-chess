from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from v_chess.enums import Color, MoveLegalityReason, BoardLegalityReason, GameOverReason
from v_chess.move import Move

if TYPE_CHECKING:
    from v_chess.game_state import GameState


class Rules(ABC):
    """Abstract base class for chess variant rules."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The human-readable name of the variant."""
        ...

    @property
    @abstractmethod()
    def starting_fen(self) -> str:
        """The default starting FEN for the variant."""
        ...

    @property
    @abstractmethod
    def has_check(self) -> bool:
        """Whether the variant includes the concept of check."""
        ...

    def get_legal_moves(self, state: "GameState") -> list[Move]:
        """Returns all legal moves in the current position."""
        return [move for move in self.get_theoretical_moves(state) if self.is_legal(state, move)]

    @abstractmethod
    def get_theoretical_moves(self, state: "GameState") -> list[Move]:
        """Returns all moves that are theoretically possible on an empty board."""
        ...

    def has_legal_moves(self, state: "GameState") -> bool:
        """Returns True if there is at least one legal move."""
        # Optimization: use any() to avoid generating all moves
        return any(self.is_legal(state, move) for move in self.get_theoretical_moves(state))

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
    def move_pseudo_legality_reason(self, state: "GameState", move: Move) -> MoveLegalityReason:
        """Checks if a move is pseudo-legal.

        Args:
            state: The current GameState.
            move: The move to check.

        Returns:
            The reason for the move's pseudo-legality status.
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

    @abstractmethod
    def get_legal_castling_moves(self, state: "GameState") -> list[Move]:
        """Returns a list of all legal castling moves."""
        ...

    @abstractmethod
    def get_legal_en_passant_moves(self, state: "GameState") -> list[Move]:
        """Returns a list of all legal en passant moves."""
        ...

    @abstractmethod
    def get_legal_promotion_moves(self, state: "GameState") -> list[Move]:
        """Returns a list of all legal pawn promotion moves."""
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

    def is_fifty_moves(self, state: "GameState") -> bool:
        """Whether the 50-move rule has been triggered."""
        return state.halfmove_clock >= 100

    def is_checkmate(self, state: "GameState") -> bool:
        """Whether the game is over by checkmate."""
        cls = getattr(self, "GameOverReason", GameOverReason)
        reason = getattr(cls, "CHECKMATE", None)
        return reason is not None and self.get_game_over_reason(state) == reason

    def is_stalemate(self, state: "GameState") -> bool:
        """Whether the game is over by stalemate."""
        cls = getattr(self, "GameOverReason", GameOverReason)
        reason = getattr(cls, "STALEMATE", None)
        return reason is not None and self.get_game_over_reason(state) == reason

    def is_draw(self, state: "GameState") -> bool:
        """Whether the game is over and resulted in a draw."""
        cls = getattr(self, "GameOverReason", GameOverReason)
        draw_reasons = []
        for attr in ("STALEMATE", "REPETITION", "FIFTY_MOVE_RULE", "MUTUAL_AGREEMENT", "INSUFFICIENT_MATERIAL"):
            reason = getattr(cls, attr, None)
            if reason is not None:
                draw_reasons.append(reason)

        return self.get_game_over_reason(state) in draw_reasons

    def is_legal(self, state: "GameState", move: Move | None = None) -> bool:
        """Checks the legality of a move or the entire board.

        Args:
            state: The GameState to check.
            move: The move to check. If None, checks the board state.

        Returns:
            True if the move/board is legal, False otherwise.
        """
        if isinstance(move, Move):
            cls = getattr(self, "MoveLegalityReason", MoveLegalityReason)
            return self.validate_move(state, move) == cls.LEGAL
        else:
            cls = getattr(self, "BoardLegalityReason", BoardLegalityReason)
            return self.validate_board_state(state) == cls.VALID
