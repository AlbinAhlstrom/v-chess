from v_chess.enums import Color, MoveLegalityReason, BoardLegalityReason, GameOverReason
from v_chess.move import Move
from v_chess.piece import King, Pawn
from v_chess.game_state import GameState
from .standard import StandardRules


class AntichessRules(StandardRules):
    MoveLegalityReason = MoveLegalityReason.load("Antichess")
    BoardLegalityReason = BoardLegalityReason.load("Antichess")
    GameOverReason = GameOverReason.load("Antichess")

    @property
    def name(self) -> str:
        return "Antichess"

    @property
    def has_check(self) -> bool:
        return False

    def validate_move(self, state: GameState, move: Move) -> MoveLegalityReason:
        pseudo_reason = self.move_pseudo_legality_reason(state, move)
        if pseudo_reason != self.MoveLegalityReason.LEGAL:
            return pseudo_reason

        if self._is_capture(state, move):
            return self.MoveLegalityReason.LEGAL

        for opt_move in self.get_theoretical_moves(state):
            if self.move_pseudo_legality_reason(state, opt_move) == self.MoveLegalityReason.LEGAL:
                if self._is_capture(state, opt_move):
                    return self.MoveLegalityReason.MANDATORY_CAPTURE
        return self.MoveLegalityReason.LEGAL

    def _is_capture(self, state: GameState, move: Move) -> bool:
        if state.board.get_piece(move.end):
            return True
        piece = state.board.get_piece(move.start)
        if isinstance(piece, Pawn) and move.end == state.ep_square:
            return True
        return False

    def is_check(self, state: GameState) -> bool:
        return False

    def inactive_player_in_check(self, state: GameState) -> bool:
        return False

    def get_game_over_reason(self, state: GameState) -> GameOverReason:
        if state.repetition_count >= 3:
             return self.GameOverReason.REPETITION
        if self.is_fifty_moves(state):
             return self.GameOverReason.FIFTY_MOVE_RULE
        if not state.board.get_pieces(color=state.turn):
            return self.GameOverReason.ALL_PIECES_CAPTURED
        if not self.has_legal_moves(state):
             return self.GameOverReason.STALEMATE
        return self.GameOverReason.ONGOING

    def validate_board_state(self, state: GameState) -> BoardLegalityReason:
        white_pawns = state.board.get_pieces(Pawn, Color.WHITE)
        black_pawns = state.board.get_pieces(Pawn, Color.BLACK)
        pawns_on_backrank = []
        for sq, piece in state.board.items():
             if isinstance(piece, Pawn) and (sq.row == 0 or sq.row == 7):
                 pawns_on_backrank.append(piece)

        is_ep_square_valid = state.ep_square is None or state.ep_square.row in (2, 5)

        if len(white_pawns) > 8:
            return self.BoardLegalityReason.TOO_MANY_WHITE_PAWNS
        if len(black_pawns) > 8:
            return self.BoardLegalityReason.TOO_MANY_BLACK_PAWNS
        if pawns_on_backrank:
            return self.BoardLegalityReason.PAWNS_ON_BACKRANK

        if not is_ep_square_valid:
            return self.BoardLegalityReason.INVALID_EP_SQUARE

        return self.BoardLegalityReason.VALID

    def get_winner(self, state: GameState) -> Color | None:
        reason = self.get_game_over_reason(state)
        if reason in (self.GameOverReason.ALL_PIECES_CAPTURED, self.GameOverReason.STALEMATE):
             return state.turn
        return None

    def castling_legality_reason(self, state: GameState, move: Move, piece: King) -> MoveLegalityReason:
        return self.MoveLegalityReason.CASTLING_DISABLED

    def get_legal_castling_moves(self, state: GameState) -> list[Move]:
        return []
