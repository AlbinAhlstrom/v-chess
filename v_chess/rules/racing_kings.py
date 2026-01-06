from v_chess.enums import GameOverReason, MoveLegalityReason, BoardLegalityReason, Color
from v_chess.game_state import GameState
from v_chess.move import Move
from v_chess.piece import King
from .standard import StandardRules


class RacingKingsRules(StandardRules):
    MoveLegalityReason = MoveLegalityReason.load("RacingKings")
    BoardLegalityReason = BoardLegalityReason.load("RacingKings")
    GameOverReason = GameOverReason.load("RacingKings")

    @property
    def name(self) -> str:
        return "Racing Kings"

    @property
    def has_check(self) -> bool:
        return False

    @property
    def starting_fen(self) -> str:
        return "8/8/8/8/8/8/krbnNBRK/qrbnNBRQ w - - 0 1"

    def validate_move(self, state: GameState, move: Move) -> MoveLegalityReason:
        pseudo = self.move_pseudo_legality_reason(state, move)
        if pseudo != self.MoveLegalityReason.LEGAL:
            return pseudo

        next_state = self.apply_move(state, move)
        if self.is_check(next_state):
            return self.MoveLegalityReason.GIVES_CHECK

        if self.inactive_player_in_check(next_state):
             return self.MoveLegalityReason.KING_LEFT_IN_CHECK

        return self.MoveLegalityReason.LEGAL

    def is_check(self, state: GameState) -> bool:
        return self._is_color_in_check(state.board, state.turn)

    def get_game_over_reason(self, state: GameState) -> GameOverReason:
        wk_on_8 = any(isinstance(p, King) and p.color == Color.WHITE and sq.row == 0
                                                for sq, p in state.board.items())
        bk_on_8 = any(isinstance(p, King) and p.color == Color.BLACK and sq.row == 0
                                                for sq, p in state.board.items())

        if wk_on_8 and bk_on_8:
            return self.GameOverReason.STALEMATE

        if bk_on_8:
            return self.GameOverReason.KING_TO_EIGHTH_RANK

        if wk_on_8:
            # White is on 8th. If turn is Black, Black has one last turn.
            if state.turn == Color.BLACK:
                # If Black can also reach 8th, it's a draw
                pass
            else:
                # Turn is White, and White is on 8th. White wins!
                return self.GameOverReason.KING_TO_EIGHTH_RANK

        # Standard rules (repetition, 50-move, stalemate)
        res = super().get_game_over_reason(state)

        if str(res.value) == str(GameOverReason.ONGOING.value):
            return self.GameOverReason.ONGOING

        try:
            return self.GameOverReason(res.value)
        except ValueError:
            return self.GameOverReason.ONGOING

    def get_winner(self, state: GameState) -> Color | None:
        reason = self.get_game_over_reason(state)
        if reason == self.GameOverReason.KING_TO_EIGHTH_RANK:
            wk_on_8 = any(isinstance(p, King) and p.color == Color.WHITE and sq.row == 0
                                                    for sq, p in state.board.items())
            if wk_on_8: return Color.WHITE
            return Color.BLACK
        return super().get_winner(state)

    def validate_board_state(self, state: GameState) -> BoardLegalityReason:
        res = super().validate_board_state(state)
        if res != BoardLegalityReason.VALID:
            return res

        if self.is_check(state) or self.inactive_player_in_check(state):
            return self.BoardLegalityReason.KING_IN_CHECK

        return BoardLegalityReason.VALID