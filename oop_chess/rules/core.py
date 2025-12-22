from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from oop_chess.enums import Color, MoveLegalityReason, BoardLegalityReason, GameOverReason
from oop_chess.move import Move

if TYPE_CHECKING:
    from oop_chess.game_state import GameState


class Rules(ABC):
    def __init__(self, state: "GameState | None" = None):
        self.state = state
        if self.has_check and self.is_check.__func__ == Rules.is_check:
             raise TypeError(f"Class {self.__class__.__name__} has check but does not override is_check.")

    @property
    @abstractmethod
    def name(self) -> str:
        """A unique, human-readable name for this rules variant."""
        ...

    @property
    @abstractmethod
    def fen_type(self) -> str:
        """Specifies the FEN notation used ('standard' or 'x-fen')."""
        ...

    @property
    @abstractmethod
    def has_check(self) -> bool:
        """Indicates if this variant has the concept of 'check'."""
        ...

    @property
    def starting_fen(self) -> str:
        """The default starting position for this variant."""
        from oop_chess.game_state import GameState
        return GameState.STARTING_FEN

    @abstractmethod
    def get_legal_moves(self) -> list[Move]:
        """Returns all legal moves in the current state."""
        ...

    @abstractmethod
    def apply_move(self, move: Move) -> "GameState":
        """Returns the new state after applying the move."""
        ...

    @abstractmethod
    def validate_move(self, move: Move) -> MoveLegalityReason:
        """Returns the legality reason for a move."""
        ...

    @abstractmethod
    def move_pseudo_legality_reason(self, move: Move) -> MoveLegalityReason:
        """Returns the pseudo-legality reason for a move."""
        ...

    @abstractmethod
    def validate_board_state(self) -> BoardLegalityReason:
        """Returns the validity of the board state."""
        ...

    @abstractmethod
    def get_game_over_reason(self) -> GameOverReason:
        """Returns the reason the game is over."""
        ...

    @abstractmethod
    def get_winner(self) -> Color | None:
        """Returns the winner if the game is over, else None."""
        ...

    @abstractmethod
    def get_legal_castling_moves(self) -> list[Move]:
        """Returns legal castling moves for the current state."""
        ...

    @abstractmethod
    def get_legal_en_passant_moves(self) -> list[Move]:
        """Returns legal en passant moves for the current state."""
        ...

    @abstractmethod
    def get_legal_promotion_moves(self) -> list[Move]:
        """Returns legal promotion moves for the current state."""
        ...

    def is_check(self) -> bool:
        """Returns True if the current player is in check.

        If has_check is False, this method returns False.
        If has_check is True, this method MUST be overridden.
        """
        return False

    def is_game_over(self) -> bool:
        """Returns True if the game is over."""
        cls = getattr(self, "GameOverReason", GameOverReason)
        return self.get_game_over_reason() != cls.ONGOING

    @property
    def is_fifty_moves(self) -> bool:
        """Returns True if the 50-move rule applies (100 halfmoves)."""
        return self.state.halfmove_clock >= 100

    @property
    def is_checkmate(self) -> bool:
        """Returns True if the game is in checkmate."""
        cls = getattr(self, "GameOverReason", GameOverReason)
        return self.get_game_over_reason() == cls.CHECKMATE

    @property
    def is_stalemate(self) -> bool:
        """Returns True if the game is in stalemate."""
        cls = getattr(self, "GameOverReason", GameOverReason)
        return self.get_game_over_reason() == cls.STALEMATE

    @property
    def is_draw(self) -> bool:
        """Returns True if the game is a draw."""
        cls = getattr(self, "GameOverReason", GameOverReason)
        return self.get_game_over_reason() in (
            cls.STALEMATE,
            cls.REPETITION,
            cls.FIFTY_MOVE_RULE,
            cls.MUTUAL_AGREEMENT,
            cls.INSUFFICIENT_MATERIAL
        )

    def is_legal(self, move: Move | None = None) -> bool:
        """
        Checks if a move or board state is legal/valid.

        Args:
            move: The Move to validate, defaults to None. Will check board state if it is None.
        """
        if isinstance(move, Move):
            return self.validate_move(move) == MoveLegalityReason.LEGAL
        else:
            return self.validate_board_state() == BoardLegalityReason.VALID
