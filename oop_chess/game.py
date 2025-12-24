from __future__ import annotations
import time
from dataclasses import replace
from typing import Optional, Dict
from oop_chess.game_state import GameState
from oop_chess.move import Move
from oop_chess.rules import Rules
from oop_chess.exceptions import IllegalMoveException, IllegalBoardException
from oop_chess.enums import MoveLegalityReason, BoardLegalityReason, GameOverReason, Color


class Game:
    """Represents a chess game.

    Responsible for turn management and history.
    """
    def __init__(self, state: GameState | str | None = None, rules: Rules | None = None, time_control: Dict = None):
        if rules and state is None:
            # If rules are provided but no state, use the variant's starting setup
            self.state = GameState.from_fen(rules.starting_fen)
        elif isinstance(state, GameState):
            self.state = state
        elif isinstance(state, str):
            self.state = GameState.from_fen(state)
        elif state is None:
            self.state = GameState.starting_setup()

        if rules:
            # Sync rules with state
            rules.state = self.state
            self.state = replace(self.state, rules=rules)
            self.rules = rules
        else:
            self.rules = self.state.rules
            self.rules.state = self.state

        self.history: list[GameState] = []
        self.move_history: list[str] = []

        # Timing
        self.time_control = time_control # {starting_time: min, increment: sec} OR {limit: sec, increment: sec}
        self.clocks = None
        self.last_move_at = None
        self.is_over_by_timeout = False
        
        if self.time_control:
            if 'limit' in self.time_control:
                start_sec = float(self.time_control['limit'])
            elif 'starting_time' in self.time_control:
                start_sec = float(self.time_control['starting_time'] * 60)
            else:
                start_sec = 600.0 # Default 10 min

            self.clocks = {
                Color.WHITE: start_sec,
                Color.BLACK: start_sec
            }

    def add_to_history(self):
        self.history.append(self.state)

    def render(self):
        """Print the board."""
        self.state.board.print()

    def take_turn(self, move: Move):
        """Make a move by finding the corresponding legal move."""
        if self.is_over_by_timeout:
             raise IllegalMoveException("Game is over by timeout.")

        board_status = self.rules.validate_board_state()
        if board_status != BoardLegalityReason.VALID:
             raise IllegalBoardException(f"Board state is illegal. Reason: {board_status}")

        move_status = self.rules.validate_move(move)
        if move_status != MoveLegalityReason.LEGAL:
            raise IllegalMoveException(f"Illegal move: {move_status.value}")

        san = move.get_san(self)

        # Update Clocks (Absolute time for persistence)
        now = time.time()
        if self.clocks:
            if self.last_move_at is None:
                # First move of the game: just start the clock for the next player
                self.last_move_at = now
            else:
                elapsed = now - self.last_move_at
                self.clocks[self.state.turn] -= elapsed
                self.clocks[self.state.turn] += self.time_control.get('increment', 0)
                self.last_move_at = now

        self.add_to_history()
        new_state = self.rules.apply_move(move)

        current_fen_key = " ".join(new_state.fen.split()[:4])

        count = 1
        for past_state in self.history:
            past_fen_key = " ".join(past_state.fen.split()[:4])
            if past_fen_key == current_fen_key:
                count += 1

        self.state = replace(new_state, repetition_count=count)
        self.state.rules.state = self.state
        self.rules = self.state.rules

        is_check = self.rules.is_check()
        is_game_over = self.rules.is_game_over()

        if is_game_over and is_check:
             san += "#"
        elif is_check:
             san += "+"

        self.move_history.append(san)

    def get_current_clocks(self) -> Optional[Dict[Color, float]]:
        """Returns the clocks accounting for time passed since the last move."""
        if not self.clocks or self.last_move_at is None:
            return self.clocks
            
        current_clocks = self.clocks.copy()
        # Deduct time passed from the player currently on move
        elapsed = time.time() - self.last_move_at
        current_clocks[self.state.turn] = max(0.0, current_clocks[self.state.turn] - elapsed)
        return current_clocks

    def undo_move(self) -> str:
        """Revert to the previous board state."""
        if not self.history:
            raise ValueError("No moves to undo.")

        self.state = self.history.pop()
        self.rules = self.state.rules
        if self.move_history:
            self.move_history.pop()
        print(f"Undo move. Restored FEN: {self.state.fen}")
        return self.state.fen

    @property
    def repetitions_of_position(self) -> int:
        return self.state.repetition_count

    @property
    def is_check(self) -> bool:
        return self.rules.is_check()

    @property
    def is_checkmate(self) -> bool:
        return self.rules.is_checkmate

    @property
    def is_over(self) -> bool:
        return self.rules.is_game_over() or self.is_over_by_timeout

    @property
    def is_draw(self) -> bool:
        return self.rules.is_draw

    @property
    def legal_moves(self) -> list[Move]:
        return self.rules.get_legal_moves()

    @property
    def game_over_reason(self) -> GameOverReason:
        return self.rules.get_game_over_reason()

    @property
    def winner(self) -> Optional[str]:
        color = self.rules.get_winner()
        return color.value if color else None

    def is_move_legal(self, move: Move) -> bool:
        return self.rules.validate_move(move) == MoveLegalityReason.LEGAL

    def is_move_pseudo_legal(self, move: Move) -> tuple[bool, MoveLegalityReason]:
        reason = self.rules.move_pseudo_legality_reason(move)
        return reason == MoveLegalityReason.LEGAL, reason