import time
from dataclasses import replace
from v_chess.game_state import GameState
from v_chess.move import Move
from v_chess.rules import Rules
from v_chess.exceptions import IllegalMoveException, IllegalBoardException
from v_chess.enums import MoveLegalityReason, BoardLegalityReason, GameOverReason, Color


class Game:
    """Represents a chess game.

    Responsible for turn management and history.
    """
    def __init__(self, state: GameState | str | None = None, rules: Rules | None = None, time_control: dict | None = None):
        """Initializes a new Game.

        Args:
            state: Initial GameState, FEN string, or None for starting setup.
            rules: Rules instance to enforce.
            time_control: Dictionary defining time limits (e.g., {'limit': 600, 'increment': 0}).
        """
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
            self.rules = rules
        else:
            from v_chess.rules import StandardRules
            self.rules = StandardRules()

        self.history: list[GameState] = []
        self.move_history: list[str] = [] # SAN
        self.uci_history: list[str] = [] # UCI (for highlighting)

        # Timing
        self.time_control = time_control # {starting_time: min, increment: sec} OR {limit: sec, increment: sec}
        self.clocks = None
        self.last_move_at = None
        self.is_over_by_timeout = False
        self.winner_override = None
        self.game_over_reason_override = None

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
        """Adds the current state to the history stack."""
        self.history.append(self.state)

    def render(self):
        """Print the board to the console."""
        self.state.board.print()

    def resign(self, player_color: Color):
        """Player resigns the game.

        Args:
            player_color: The color of the player resigning.
        """
        self.game_over_reason_override = GameOverReason.SURRENDER
        winner_color = player_color.opposite
        self.winner_override = winner_color.value

        result = "1-0" if winner_color == Color.WHITE else "0-1"
        self.move_history.append(result)

    def abort(self):
        """Aborts the game.

        The game ends with no winner and Aborted reason.
        """
        self.game_over_reason_override = GameOverReason.ABORTED
        self.winner_override = "aborted"
        self.move_history.append("aborted")

    def agree_draw(self):
        """Players agree to a draw.

        The game ends with a draw result.
        """
        self.game_over_reason_override = GameOverReason.MUTUAL_AGREEMENT
        self.winner_override = "draw"
        self.move_history.append("1/2-1/2")

    def take_turn(self, move: Move, offer_draw: bool = False):
        """Executes a move in the game.

        Validates the move, updates the board state, checks for game end conditions,
        and updates history.

        Args:
            move: The move to execute.
            offer_draw: Whether the move is accompanied by a draw offer.

        Raises:
            IllegalMoveException: If the move is not legal.
            IllegalBoardException: If the board state is invalid before the move.
        """
        if self.is_over:
             raise IllegalMoveException("Game is over.")

        board_status = self.rules.validate_board_state(self.state)
        if board_status != BoardLegalityReason.VALID:
             raise IllegalBoardException(f"Board state is illegal. Reason: {board_status}")

        move_status = self.rules.validate_move(self.state, move)
        if move_status != MoveLegalityReason.LEGAL:
            raise IllegalMoveException(f"Illegal move: {move_status.value} (attempted: {move.uci})")

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
        new_state = self.rules.apply_move(self.state, move)

        current_fen_key = " ".join(new_state.fen.split()[:4])

        count = 1
        for past_state in self.history:
            past_fen_key = " ".join(past_state.fen.split()[:4])
            if past_fen_key == current_fen_key:
                count += 1

        self.state = replace(new_state, repetition_count=count)

        is_game_over = self.is_over
        is_check = self.is_check

        if is_game_over:
            if self.game_over_reason == GameOverReason.CHECKMATE:
                 san += "#"
        elif is_check:
             san += "+"

        if offer_draw:
             san += "="

        self.move_history.append(san)
        self.uci_history.append(move.uci)

        if is_game_over:
             result = "1/2-1/2"
             winner_color = self.rules.get_winner(self.state)
             if winner_color == Color.WHITE:
                 result = "1-0"
             elif winner_color == Color.BLACK:
                 result = "0-1"
             self.move_history.append(result)

    def get_current_clocks(self) -> dict[Color, float] | None:
        """Returns the current remaining time for each player.

        Accounts for time passed since the last move.

        Returns:
            A dictionary mapping Color to remaining seconds, or None if no time control.
        """
        if not self.clocks or self.last_move_at is None:
            return self.clocks

        current_clocks = self.clocks.copy()
        # Deduct time passed from the player currently on move
        elapsed = time.time() - self.last_move_at
        current_clocks[self.state.turn] = max(0.0, current_clocks[self.state.turn] - elapsed)
        return current_clocks

    def undo_move(self) -> str:
        """Reverts the last move.

        Restores the previous game state.

        Returns:
            The FEN string of the restored state.

        Raises:
            ValueError: If there are no moves to undo.
        """
        if not self.history:
            raise ValueError("No moves to undo.")

        # Check if last element is a result string and remove it
        if self.move_history and self.move_history[-1] in ["1-0", "0-1", "1/2-1/2"]:
            self.move_history.pop()

        self.state = self.history.pop()
        if self.move_history:
            self.move_history.pop()
        if self.uci_history:
            self.uci_history.pop()

        if not self.uci_history:
            self.last_move_at = None

        # Reset overrides if any
        self.game_over_reason_override = None
        self.winner_override = None

        print(f"Undo move. Restored FEN: {self.state.fen}")
        return self.state.fen

    @property
    def repetitions_of_position(self) -> int:
        """Returns the number of times the current position has occurred."""
        return self.state.repetition_count

    @property
    def is_check(self) -> bool:
        """Checks if the current side to move is in check."""
        return self.rules.is_check(self.state)

    @property
    def is_checkmate(self) -> bool:
        """Checks if the current side to move is checkmated."""
        cls = getattr(self.rules, "GameOverReason", GameOverReason)
        reason = getattr(cls, "CHECKMATE", None)
        return reason is not None and self.game_over_reason == reason

    @property
    def is_stalemate(self) -> bool:
        """Whether the game is over by stalemate."""
        cls = getattr(self.rules, "GameOverReason", GameOverReason)
        reason = getattr(cls, "STALEMATE", None)
        return reason is not None and self.game_over_reason == reason

    @property
    def is_draw(self) -> bool:
        """Checks if the game is a draw."""
        cls = getattr(self.rules, "GameOverReason", GameOverReason)
        draw_reasons = []
        for attr in ("STALEMATE", "REPETITION", "FIFTY_MOVE_RULE", "MUTUAL_AGREEMENT", "INSUFFICIENT_MATERIAL"):
            reason = getattr(cls, attr, None)
            if reason is not None:
                draw_reasons.append(reason)

        return self.game_over_reason in draw_reasons

    @property
    def is_over(self) -> bool:
        """Checks if the game is over."""
        if self.is_over_by_timeout or self.game_over_reason_override is not None or self.winner_override is not None:
            return True
        return self.rules.is_game_over(self.state)

    @property
    def legal_moves(self) -> list[Move]:
        """Returns a list of all legal moves in the current position."""
        return [move for move in self.rules.get_theoretical_moves(self.state) if self.is_move_legal(move)]

    @property
    def has_legal_moves(self) -> bool:
        """Checks if there is at least one legal move."""
        return any(self.is_move_legal(move) for move in self.rules.get_theoretical_moves(self.state))

    @property
    def game_over_reason(self) -> GameOverReason:
        """Returns the reason for the game ending."""
        if self.game_over_reason_override:
            return self.game_over_reason_override
        if self.is_over_by_timeout:
             return GameOverReason.TIMEOUT
        return self.rules.get_game_over_reason(self.state)

    @property
    def winner(self) -> str | None:
        """Returns the winner's color (as string) or None if draw/ongoing."""
        if self.winner_override:
            return self.winner_override

        # Timeout handling
        if self.is_over_by_timeout:
             # If timeout, the winner is the one NOT on turn (simplification)
             return self.state.turn.opposite.value

        color = self.rules.get_winner(self.state)
        return color.value if color else None

    def is_move_legal(self, move: Move) -> bool:
        """Checks if a move is legal.

        Args:
            move: The move to check.

        Returns:
            True if the move is legal, False otherwise.
        """
        return self.rules.validate_move(self.state, move) == MoveLegalityReason.LEGAL