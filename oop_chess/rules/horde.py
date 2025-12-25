from dataclasses import replace
from oop_chess.enums import GameOverReason, MoveLegalityReason, BoardLegalityReason, Color, Direction
from oop_chess.game_state import GameState
from oop_chess.move import Move
from oop_chess.piece import Pawn, King
from oop_chess.square import Square
from .standard import StandardRules


class HordeRules(StandardRules):
    MoveLegalityReason = MoveLegalityReason.load("Horde")
    BoardLegalityReason = BoardLegalityReason.load("Horde")
    GameOverReason = GameOverReason.load("Horde")

    @property
    def name(self) -> str:
        return "Horde"

    @property
    def starting_fen(self) -> str:
        return "rnbqkbnr/pppppppp/8/1PP2PP1/PPPPPPPP/PPPPPPPP/PPPPPPPP/PPPPPPPP w kq - 0 1"

    def validate_board_state(self) -> BoardLegalityReason:
        # Standard logic but without White King requirement
        black_kings = self.state.board.get_pieces(King, Color.BLACK)
        if len(black_kings) < 1:
            return BoardLegalityReason.NO_BLACK_KING

        # Standard pawn count limits don't apply to Horde White
        black_pawns = self.state.board.get_pieces(Pawn, Color.BLACK)
        if len(black_pawns) > 8:
            return BoardLegalityReason.TOO_MANY_BLACK_PAWNS

        if self.invalid_castling_rights():
            return BoardLegalityReason.INVALID_CASTLING_RIGHTS

        # Standard EP square check
        is_ep_square_valid = self.state.ep_square is None or self.state.ep_square.row in (2, 5)
        if not is_ep_square_valid:
            return BoardLegalityReason.INVALID_EP_SQUARE

        # Inactive player in check (only Black King can be in check)
        if self.state.turn == Color.BLACK:
            # White moved. Check if White king in check? No White king.
            pass
        else:
            # Black moved. Check if Black king in check.
            if self.is_check(): # is_check uses self.state.turn
                 # Wait, is_check checks if active color is in check.
                 # If Black just moved, it's White's turn.
                 # inactive_player_in_check checks turn.opposite.
                 if self.inactive_player_in_check():
                      return BoardLegalityReason.OPPOSITE_CHECK

        return BoardLegalityReason.VALID

    def is_check(self) -> bool:
        if self.state.turn == Color.WHITE:
            return False # White has no King
        return super().is_check()

    def get_game_over_reason(self) -> GameOverReason:
        # White wins if Black checkmated
        if self.state.turn == Color.BLACK:
            if not self.has_legal_moves():
                if self.is_check():
                    return self.GameOverReason.CHECKMATE
                return self.GameOverReason.STALEMATE

        # Black wins if White has no pieces left
        white_pieces = self.state.board.get_pieces(color=Color.WHITE)
        if not white_pieces:
            return self.GameOverReason.ALL_PIECES_CAPTURED

        # Black wins if White checkmated? (No white king, so no)
        # But White can be stalemated
        if self.state.turn == Color.WHITE:
            if not self.has_legal_moves():
                return self.GameOverReason.STALEMATE

        res = super().get_game_over_reason()
        if str(res.value) == str(GameOverReason.ONGOING.value):
            return self.GameOverReason.ONGOING
            
        try:
            return self.GameOverReason(res.value)
        except ValueError:
            return self.GameOverReason.ONGOING

    def get_winner(self) -> Color | None:
        reason = self.get_game_over_reason()
        if reason == self.GameOverReason.CHECKMATE:
            return Color.WHITE
        if reason == self.GameOverReason.ALL_PIECES_CAPTURED:
            return Color.BLACK
        return super().get_winner()

    def get_theoretical_moves(self):
        yield from super().get_theoretical_moves()

        # Horde specific: White pawns on rank 1 can also move 2 steps
        if self.state.turn == Color.WHITE:
            bb = self.state.board.bitboard
            mask = bb.pieces[Color.WHITE][Pawn] & 0xFF00000000000000 # Row 7 (Rank 1)
            while mask:
                sq_idx = (mask & -mask).bit_length() - 1
                sq = Square(divmod(sq_idx, 8))
                
                # Manual double push for Rank 1
                one_step = sq.get_step(Direction.UP)
                two_step = one_step.get_step(Direction.UP) if one_step and not one_step.is_none_square else None
                if two_step and not two_step.is_none_square:
                    yield Move(sq, two_step)
                
                mask &= mask - 1

    def move_pseudo_legality_reason(self, move: Move) -> MoveLegalityReason:
        piece = self.state.board.get_piece(move.start)
        if piece and isinstance(piece, Pawn) and piece.color == Color.WHITE:
            # White Rank 1: row 7. Double push is valid if path is clear.
            if move.start.row == 7:
                one_step = move.start.get_step(Direction.UP)
                two_step = one_step.get_step(Direction.UP) if one_step else None
                if move.end == two_step:
                    if self.state.board.get_piece(one_step) is None and self.state.board.get_piece(two_step) is None:
                        return self.MoveLegalityReason.LEGAL

        return super().move_pseudo_legality_reason(move)
