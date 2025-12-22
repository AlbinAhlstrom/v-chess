from oop_chess.enums import Color, MoveLegalityReason, BoardLegalityReason, GameOverReason
from oop_chess.move import Move
from oop_chess.piece import King, Pawn
from oop_chess.game_state import GameState
from .standard import StandardRules


class AntichessRules(StandardRules):
    @property
    def name(self) -> str:
        return "Antichess"

    @property
    def has_check(self) -> bool:
        return False

    def validate_move(self, move: Move) -> MoveLegalityReason:
        pseudo_reason = self.move_pseudo_legality_reason(move)
        if pseudo_reason != MoveLegalityReason.LEGAL:
            return pseudo_reason

        if self._is_capture(move):
            return MoveLegalityReason.LEGAL

        for opt_move in self.get_theoretical_moves():
            if self.move_pseudo_legality_reason(opt_move) == MoveLegalityReason.LEGAL:
                if self._is_capture(opt_move):
                    return MoveLegalityReason.MANDATORY_CAPTURE
        return MoveLegalityReason.LEGAL

    def _is_capture(self, move: Move) -> bool:
        if self.state.board.get_piece(move.end):
            return True
        piece = self.state.board.get_piece(move.start)
        if isinstance(piece, Pawn) and move.end == self.state.ep_square:
            return True
        return False

    def is_check(self) -> bool:
        return False

    def inactive_player_in_check(self) -> bool:
        return False

    def get_game_over_reason(self) -> GameOverReason:
        if self.state.repetition_count >= 3:
             return GameOverReason.REPETITION
        if self.is_fifty_moves:
             return GameOverReason.FIFTY_MOVE_RULE
        if not self.state.board.get_pieces(color=self.state.turn):
            return GameOverReason.ALL_PIECES_CAPTURED
        if not self.get_legal_moves():
             return GameOverReason.STALEMATE
        return GameOverReason.ONGOING

    def validate_board_state(self) -> BoardLegalityReason:
        white_pawns = self.state.board.get_pieces(Pawn, Color.WHITE)
        black_pawns = self.state.board.get_pieces(Pawn, Color.BLACK)
        pawns_on_backrank = []
        for sq, piece in self.state.board.board.items():
             if isinstance(piece, Pawn) and (sq.row == 0 or sq.row == 7):
                 pawns_on_backrank.append(piece)

        is_ep_square_valid = self.state.ep_square is None or self.state.ep_square.row in (2, 5)

        if len(white_pawns) > 8:
            return BoardLegalityReason.TOO_MANY_WHITE_PAWNS
        if len(black_pawns) > 8:
            return BoardLegalityReason.TOO_MANY_BLACK_PAWNS
        if pawns_on_backrank:
            return BoardLegalityReason.PAWNS_ON_BACKRANK

        if not is_ep_square_valid:
            return BoardLegalityReason.INVALID_EP_SQUARE

        return BoardLegalityReason.VALID

    def get_winner(self) -> Color | None:
        reason = self.get_game_over_reason()
        if reason in (GameOverReason.ALL_PIECES_CAPTURED, GameOverReason.STALEMATE):
             return self.state.turn
        return None

    def castling_legality_reason(self, move: Move, piece: King) -> MoveLegalityReason:
        return MoveLegalityReason.CASTLING_DISABLED

    def get_legal_castling_moves(self) -> list[Move]:
        return []
