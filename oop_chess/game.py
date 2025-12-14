from typing import Optional
from dataclasses import replace

from oop_chess.board import Board
from oop_chess.game_state import GameState
from oop_chess.move import Move
from oop_chess.rules import Rules, StandardRules
from oop_chess.exceptions import IllegalMoveException, IllegalBoardException
from oop_chess.enums import MoveLegalityReason


class Game:
    """Represents a chess game.

    Responsible for turn management.
    """

    def __init__(self, fen: str | Board | None = None, board: Optional[Board] = None, state: Optional[GameState] = None, rules: Optional[Rules] = None):
        if isinstance(fen, Board):
            board = fen
            fen = None

        if state:
            self.state = state
        elif fen:
            self.state = GameState.from_fen(fen)
        elif board:
            self.state = replace(GameState.starting_setup(), board=board)
        else:
            self.state = GameState.starting_setup()

        self.rules = rules or StandardRules()

        self.history: list[GameState] = []
        self.move_history: list[str] = []

    @property
    def is_over(self):
        return self.rules.is_game_over(self.state)

    @property
    def is_checkmate(self):
        return self.rules.is_checkmate(self.state)

    @property
    def is_check(self):
        return self.rules.is_check(self.state)

    @property
    def is_draw(self):
         return self.rules.is_draw(self.state)

    def add_to_history(self):
        self.history.append(self.state)

    @property
    def legal_moves(self) -> list[Move]:
        return self.rules.get_legal_moves(self.state)

    def is_move_legal(self, move: Move) -> bool:
        return self.rules.is_move_legal(self.state, move)

    def is_move_pseudo_legal(self, move: Move) -> tuple[bool, str]:
        """Determine if a move is pseudolegal.

        This method is primarily used for testing and debugging.
        """
        reason = self.rules.move_pseudo_legality_reason(self.state, move)
        return reason == MoveLegalityReason.LEGAL, reason.value

    def render(self):
        """Print the board."""
        self.state.board.print()

    def take_turn(self, move: Move):
        """Make a move by finding the corresponding legal move."""
        if not self.rules.is_board_state_legal(self.state):
            raise IllegalBoardException(f"Board state is illegal. Reason: {self.rules.status(self.state)}")

        reason = self.rules.move_legality_reason(self.state, move)
        if reason != "Move is legal":
            raise IllegalMoveException(f"Illegal move: {reason}")

        san = move.get_san(self)

        self.add_to_history()
        self.state = self.rules.apply_move(self.state, move)

        if self.is_checkmate:
            san += "#"
        elif self.is_check:
            san += "+"

        self.move_history.append(san)

    def undo_move(self) -> str:
        """Revert to the previous board state."""
        if not self.history:
            raise ValueError("No moves to undo.")

        self.state = self.history.pop()
        if self.move_history:
            self.move_history.pop()
        print(f"Undo move. Restored FEN: {self.state.fen}")
        return self.state.fen

    @property
    def repetitions_of_position(self) -> int:
        current_fen_key = " ".join(self.state.fen.split()[:4])
        count = 1
        for past_state in self.history:
            past_fen_key = " ".join(past_state.fen.split()[:4])
            if past_fen_key == current_fen_key:
                count += 1
        return count

