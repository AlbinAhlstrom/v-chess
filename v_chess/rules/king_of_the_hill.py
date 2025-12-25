from v_chess.enums import GameOverReason, Color
from v_chess.square import Square
from v_chess.piece import King
from .standard import StandardRules

class KingOfTheHillRules(StandardRules):
    
    GameOverReason = GameOverReason.load("KingOfTheHill")

    @property
    def name(self) -> str:
        return "King of the Hill"

    def get_game_over_reason(self) -> GameOverReason:
        # Check standard game over reasons first (Checkmate, Stalemate, etc.)
        standard_reason = super().get_game_over_reason()
        if standard_reason != self.GameOverReason.ONGOING:
            return standard_reason

        # Check King of the Hill condition: King on center squares
        center_squares = {Square("d4"), Square("d5"), Square("e4"), Square("e5")}
        
        for sq, piece in self.state.board.board.items():
            if isinstance(piece, King) and sq in center_squares:
                return self.GameOverReason.KING_ON_HILL
        
        return self.GameOverReason.ONGOING

    def get_winner(self) -> Color | None:
        reason = self.get_game_over_reason()
        if reason == self.GameOverReason.CHECKMATE:
            return self.state.turn.opposite
        if reason == self.GameOverReason.KING_ON_HILL:
            # The player whose turn it is currently is NOT the one who moved into the center.
            # The move was just applied. The turn has switched.
            # So if King is on center, the player who JUST moved (opposite of current turn) won.
            # Wait, `take_turn` applies move, then switches turn, then checks game over.
            # `apply_move` switches turn.
            return self.state.turn.opposite
        return None