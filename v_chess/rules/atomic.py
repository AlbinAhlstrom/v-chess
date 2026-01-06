from v_chess.enums import GameOverReason, MoveLegalityReason, BoardLegalityReason, Color, Direction
from v_chess.game_state import GameState
from v_chess.move import Move
from v_chess.piece import Pawn, King
from .standard import StandardRules


class AtomicRules(StandardRules):
    MoveLegalityReason = MoveLegalityReason.load("Atomic")
    BoardLegalityReason = BoardLegalityReason.load("Atomic")
    GameOverReason = GameOverReason.load("Atomic")

    @property
    def name(self) -> str:
        return "Atomic"

    def apply_move(self, state: GameState, move: Move) -> GameState:
        # Standard move logic might need to be bypassed if it's a capture
        # because the board changes drastically.

        # Check if it's a capture in current state
        moving_piece = state.board.get_piece(move.start)
        target_piece = state.board.get_piece(move.end)
        is_en_passant = isinstance(moving_piece, Pawn) and move.end == state.ep_square

        if not (target_piece or is_en_passant):
            return super().apply_move(state, move)

        # Capture logic: Explosion
        new_board = state.board.copy()

        # 1. Remove capturing piece
        new_board.remove_piece(move.start)

        # 2. Remove captured piece (target square or EP square)
        if is_en_passant:
            direction = Direction.DOWN if moving_piece.color == Color.WHITE else Direction.UP
            captured_sq = move.end.adjacent(direction)
            new_board.remove_piece(captured_sq)
        else:
            new_board.remove_piece(move.end)

        # 3. Explode neighbors
        # Surrounding 8 squares of move.end
        neighbors = [
            move.end.adjacent(d) for d in Direction.straight_and_diagonal()
        ]

        for sq in neighbors:
            if not sq.is_none_square:
                p = new_board.get_piece(sq)
                if p and not isinstance(p, Pawn):
                    new_board.remove_piece(sq)

        # Update state (turn, clocks, etc.)
        # Explosion resets halfmove? Captures do.
        new_halfmove_clock = 0
        new_fullmove_count = state.fullmove_count
        if state.turn == Color.BLACK:
            new_fullmove_count += 1

        return GameState(
            board=new_board,
            turn=state.turn.opposite,
            castling_rights=self._update_castling_rights_after_explosion(state, new_board),
            ep_square=None, # EP is consumed/lost
            halfmove_clock=new_halfmove_clock,
            fullmove_count=new_fullmove_count,
            repetition_count=1,
            explosion_square=move.end
        )

    def _update_castling_rights_after_explosion(self, state: GameState, board) -> tuple:
        # Castling rights are lost if King or Rook are exploded
        from v_chess.enums import CastlingRight
        new_rights = []
        for right in state.castling_rights:
            if right == CastlingRight.NONE: continue
            king = board.get_piece(right.expected_king_square)
            rook = board.get_piece(right.expected_rook_square)
            if isinstance(king, King) and king.color == right.color and \
               board.get_piece(right.expected_rook_square) and \
               board.get_piece(right.expected_rook_square).color == right.color:
                new_rights.append(right)
        return tuple(new_rights)

    def validate_move(self, state: GameState, move: Move) -> MoveLegalityReason:
        # 1. Standard pseudo-legality
        pseudo = self.move_pseudo_legality_reason(state, move)
        if pseudo != MoveLegalityReason.LEGAL:
            return pseudo

        # 2. Kings cannot capture
        piece = state.board.get_piece(move.start)
        if isinstance(piece, King):
            if state.board.get_piece(move.end) or move.end == state.ep_square:
                return self.MoveLegalityReason.OWN_PIECE_CAPTURE

        # 3. Check for king explosion (own king)
        next_state = self.apply_move(state, move)
        own_king_exists = any(isinstance(p, King) and p.color == state.turn 
                              for p in next_state.board.values())

        if not own_king_exists:
            return self.MoveLegalityReason.KING_EXPLODED

        # 4. Standard check rules? 
        # In Atomic, if you explode the opponent's king, check rules don't matter.
        # But if the move DOESN'T explode the opponent's king, you MUST NOT be in check.

        opp_king_exists = any(isinstance(p, King) and p.color == state.turn.opposite 
                               for p in next_state.board.values())

        if not opp_king_exists:
            return self.MoveLegalityReason.LEGAL # Win move!

        # Standard check validation
        if self.inactive_player_in_check(next_state):
            return self.MoveLegalityReason.KING_LEFT_IN_CHECK

        # 5. Kings cannot be adjacent
        if self._kings_adjacent(next_state.board):
            return self.MoveLegalityReason.KING_EXPLODED

        return self.MoveLegalityReason.LEGAL

    def _kings_adjacent(self, board) -> bool:
        wk = [sq for sq, p in board.items() if isinstance(p, King) and p.color == Color.WHITE]
        bk = [sq for sq, p in board.items() if isinstance(p, King) and p.color == Color.BLACK]
        if not wk or not bk: return False
        return wk[0].is_adjacent_to(bk[0])

    def validate_board_state(self, state: GameState) -> BoardLegalityReason:
        res = super().validate_board_state(state)

        # Check adjacent kings if the board is otherwise valid or just has an opposite check
        # (since adjacent kings imply opposite check, we want to report the specific reason)
        if res == BoardLegalityReason.VALID or res == BoardLegalityReason.OPPOSITE_CHECK:
            if self._kings_adjacent(state.board):
                return self.BoardLegalityReason.KINGS_ADJACENT

        return res

    def get_game_over_reason(self, state: GameState) -> GameOverReason:
        # Check if a king is missing
        wk = any(isinstance(p, King) and p.color == Color.WHITE for p in state.board.values())
        bk = any(isinstance(p, King) and p.color == Color.BLACK for p in state.board.values())

        if not wk or not bk:
            return self.GameOverReason.KING_EXPLODED

        res = super().get_game_over_reason(state)
        if res == GameOverReason.ONGOING:
            return self.GameOverReason.ONGOING

        try:
            return self.GameOverReason(res.value)
        except ValueError:
            return self.GameOverReason.ONGOING

    def get_winner(self, state: GameState) -> Color | None:
        reason = self.get_game_over_reason(state)
        if reason == self.GameOverReason.KING_EXPLODED:
            wk = any(isinstance(p, King) and p.color == Color.WHITE for p in state.board.values())
            if not wk: return Color.BLACK
            return Color.WHITE
        return super().get_winner(state)