from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from v_chess.enums import Color, MoveLegalityReason, BoardLegalityReason, GameOverReason
from v_chess.move import Move

if TYPE_CHECKING:
    from v_chess.game_state import GameState


class Rules(ABC):
    """Abstract base class for chess variant rules.

    Attributes:
        state: The current GameState context.
    """
    def __init__(self, state: "GameState | None" = None):
        """Initializes the rules with an optional state.

        Args:
            state: The initial game state.
        """
        self.state = state
        if self.has_check and self.is_check.__func__ == Rules.is_check:
             raise TypeError(f"Class {self.__class__.__name__} has check but does not override is_check.")

    @property
    @abstractmethod
    def name(self) -> str:
        """The human-readable name of the variant."""
        ...

    @property
    @abstractmethod
    def fen_type(self) -> str:
        """The FEN notation type used (e.g., 'standard')."""
        ...

    @property
    @abstractmethod
    def has_check(self) -> bool:
        """Whether the variant includes the concept of check."""
        ...

    @property
    def starting_fen(self) -> str:
        """The default starting FEN for the variant."""
        from v_chess.game_state import GameState
        return GameState.STARTING_FEN

    def get_legal_moves(self) -> list[Move]:
        """Returns all legal moves in the current position."""
        return [move for move in self.get_theoretical_moves() if self.is_legal(move)]

    @abstractmethod
    def get_theoretical_moves(self) -> list[Move]:
        """Returns all moves that are theoretically possible on an empty board."""
        ...

    def has_legal_moves(self) -> bool:
        """Returns True if there is at least one legal move."""
        return len(self.get_legal_moves()) > 0

    @abstractmethod
    def apply_move(self, move: Move) -> "GameState":
        """Executes a move and returns the resulting state.

        Args:
            move: The move to apply.

        Returns:
            The new GameState.
        """
        ...

    @abstractmethod
    def validate_move(self, move: Move) -> MoveLegalityReason:
        """Validates if a move is fully legal.

        Args:
            move: The move to validate.

        Returns:
            The reason for the move's legality status.
        """
        ...

    @abstractmethod
    def move_pseudo_legality_reason(self, move: Move) -> MoveLegalityReason:
        """Checks if a move is pseudo-legal.

        Args:
            move: The move to check.

        Returns:
            The reason for the move's pseudo-legality status.
        """
        ...

    @abstractmethod
    def validate_board_state(self) -> BoardLegalityReason:
        """Validates the overall board state.

        Returns:
            The reason for the board's legality status.
        """
        ...

    @abstractmethod
    def get_game_over_reason(self) -> GameOverReason:
        """Determines why the game ended.

        Returns:
            The reason for the game ending.
        """
        ...

    @abstractmethod
    def get_winner(self) -> Color | None:
        """Determines the winner of the game.

        Returns:
            The color of the winner, or None if it's a draw or ongoing.
        """
        ...

    @abstractmethod
    def get_legal_castling_moves(self) -> list[Move]:
        """Returns a list of all legal castling moves."""
        ...

    @abstractmethod
    def get_legal_en_passant_moves(self) -> list[Move]:
        """Returns a list of all legal en passant moves."""
        ...

    @abstractmethod
    def get_legal_promotion_moves(self) -> list[Move]:
        """Returns a list of all legal pawn promotion moves."""
        ...

    def is_check(self) -> bool:
        """Checks if the current player is in check.

        Returns:
            True if the player is in check, False otherwise.
        """
        return False

    def is_game_over(self) -> bool:
        """Checks if the game has ended."""
        cls = getattr(self, "GameOverReason", GameOverReason)
        return self.get_game_over_reason() != cls.ONGOING

    @property
    def is_fifty_moves(self) -> bool:
        """Whether the 50-move rule has been triggered."""
        return self.state.halfmove_clock >= 100

    @property
    def is_checkmate(self) -> bool:
        """Whether the game is over by checkmate."""
        cls = getattr(self, "GameOverReason", GameOverReason)
        reason = getattr(cls, "CHECKMATE", None)
        return reason is not None and self.get_game_over_reason() == reason

    @property
    def is_stalemate(self) -> bool:
        """Whether the game is over by stalemate."""
        cls = getattr(self, "GameOverReason", GameOverReason)
        reason = getattr(cls, "STALEMATE", None)
        return reason is not None and self.get_game_over_reason() == reason

    @property
    def is_draw(self) -> bool:
        """Whether the game is over and resulted in a draw."""
        cls = getattr(self, "GameOverReason", GameOverReason)
        draw_reasons = []
        for attr in ("STALEMATE", "REPETITION", "FIFTY_MOVE_RULE", "MUTUAL_AGREEMENT", "INSUFFICIENT_MATERIAL"):
            reason = getattr(cls, attr, None)
            if reason is not None:
                draw_reasons.append(reason)
        
        return self.get_game_over_reason() in draw_reasons

    def is_legal(self, move: Move | None = None) -> bool:
        """Checks the legality of a move or the entire board.

        Args:
            move: The move to check. If None, checks the board state.

        Returns:
            True if the move/board is legal, False otherwise.
        """
        if isinstance(move, Move):
            cls = getattr(self, "MoveLegalityReason", MoveLegalityReason)
            return self.validate_move(move) == cls.LEGAL
        else:
            cls = getattr(self, "BoardLegalityReason", BoardLegalityReason)
            return self.validate_board_state() == cls.VALID
