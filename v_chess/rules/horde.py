from v_chess.enums import GameOverReason, MoveLegalityReason, BoardLegalityReason, Color, Direction
from v_chess.game_state import GameState
from v_chess.move import Move
from v_chess.piece import Pawn, King
from v_chess.square import Square
from .standard import StandardRules


class HordeRules(StandardRules):
    """Rules for Horde chess variant."""
    MoveLegalityReason = MoveLegalityReason.load("Horde")
    BoardLegalityReason = BoardLegalityReason.load("Horde")
    GameOverReason = GameOverReason.load("Horde")

    @property
    def name(self) -> str:
        """The human-readable name of the variant."""
        return "Horde"

    @property
    def starting_fen(self) -> str:
        """The default starting FEN for Horde."""
        return "rnbqkbnr/pppppppp/8/1PP2PP1/PPPPPPPP/PPPPPPPP/PPPPPPPP/PPPPPPPP w kq - 0 1"

    def validate_board_state(self, state: GameState) -> BoardLegalityReason:
        """Validates the board state, allowing for the lack of a White King."""
        # Standard logic but without White King requirement
        black_kings = state.board.get_pieces(King, Color.BLACK)
        if len(black_kings) < 1:
            return BoardLegalityReason.NO_BLACK_KING

        # Standard pawn count limits don't apply to Horde White
        black_pawns = state.board.get_pieces(Pawn, Color.BLACK)
        if len(black_pawns) > 8:
            return BoardLegalityReason.TOO_MANY_BLACK_PAWNS

        if self.invalid_castling_rights(state):
            return BoardLegalityReason.INVALID_CASTLING_RIGHTS

        # Standard EP square check
        is_ep_square_valid = state.ep_square is None or state.ep_square.row in (2, 5)
        if not is_ep_square_valid:
            return BoardLegalityReason.INVALID_EP_SQUARE

        # Inactive player in check (only Black King can be in check)
        if state.turn == Color.BLACK:
            # White moved. Check if White king in check? No White king.
            pass
        else:
            # Black moved. Check if Black king in check.
            if self.is_check(state):
                 if self.inactive_player_in_check(state):
                      return BoardLegalityReason.OPPOSITE_CHECK

        return BoardLegalityReason.VALID

    def is_check(self, state: GameState) -> bool:
        """Checks if the current player is in check (always False for White)."""
        if state.turn == Color.WHITE:
            return False # White has no King
        return super().is_check(state)

    def get_game_over_reason(self, state: GameState) -> GameOverReason:
        """Determines the game over reason, including capture of all White pieces."""
        # White wins if Black checkmated
        if state.turn == Color.BLACK:
            if not self.has_legal_moves(state):
                if self.is_check(state):
                    return self.GameOverReason.CHECKMATE
                return self.GameOverReason.STALEMATE

        # Black wins if White has no pieces left
        white_pieces = state.board.get_pieces(color=Color.WHITE)
        if not white_pieces:
            return self.GameOverReason.ALL_PIECES_CAPTURED

        # Black wins if White checkmated? (No white king, so no)
        # But White can be stalemated
        if state.turn == Color.WHITE:
            if not self.has_legal_moves(state):
                return self.GameOverReason.STALEMATE

        res = super().get_game_over_reason(state)
        if str(res.value) == str(GameOverReason.ONGOING.value):
            return self.GameOverReason.ONGOING

        try:
            return self.GameOverReason(res.value)
        except ValueError:
            return self.GameOverReason.ONGOING

    def get_winner(self, state: GameState) -> Color | None:
        """Determines the winner of the game."""
        reason = self.get_game_over_reason(state)
        if reason == self.GameOverReason.CHECKMATE:
            return Color.WHITE
        if reason == self.GameOverReason.ALL_PIECES_CAPTURED:
            return Color.BLACK
        return super().get_winner(state)

    def get_theoretical_moves(self, state: GameState):
        """Generates all theoretical moves, including Horde-specific pawn pushes."""
        yield from super().get_theoretical_moves(state)

        # Horde specific: White pawns on rank 1 can also move 2 steps
        if state.turn == Color.WHITE:
            bb = state.board.bitboard
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

    def move_pseudo_legality_reason(self, state: GameState, move: Move) -> MoveLegalityReason:
        """Checks pseudo-legality, handling Horde-specific rank 1 pawn pushes."""
        piece = state.board.get_piece(move.start)
        if piece and isinstance(piece, Pawn) and piece.color == Color.WHITE:
            # White Rank 1: row 7. Double push is valid if path is clear.
            if move.start.row == 7:
                one_step = move.start.get_step(Direction.UP)
                two_step = one_step.get_step(Direction.UP) if one_step else None
                if move.end == two_step:
                    if state.board.get_piece(one_step) is None and state.board.get_piece(two_step) is None:
                        return self.MoveLegalityReason.LEGAL

        return super().move_pseudo_legality_reason(state, move)