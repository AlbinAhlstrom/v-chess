from v_chess.enums import GameOverReason, Color
from v_chess.square import Square
from v_chess.piece import King
from v_chess.game_state import GameState
from .standard import StandardRules

class KingOfTheHillRules(StandardRules):

    GameOverReason = GameOverReason.load("KingOfTheHill")

    @property
    def name(self) -> str:
        return "King of the Hill"

    def get_game_over_reason(self, state: GameState) -> GameOverReason:
        # Check standard game over reasons first (Checkmate, Stalemate, etc.)
        standard_reason = super().get_game_over_reason(state)
        if standard_reason != self.GameOverReason.ONGOING:
            return standard_reason

        # Check King of the Hill condition: King on center squares
        center_squares = {Square("d4"), Square("d5"), Square("e4"), Square("e5")}

        for sq, piece in state.board.items():
            if isinstance(piece, King) and sq in center_squares:
                return self.GameOverReason.KING_ON_HILL

        return self.GameOverReason.ONGOING

    def get_winner(self, state: GameState) -> Color | None:
        reason = self.get_game_over_reason(state)
        if reason == self.GameOverReason.CHECKMATE:
            return state.turn.opposite
        if reason == self.GameOverReason.KING_ON_HILL:
            # The player who just moved won.
            return state.turn.opposite
        return None
