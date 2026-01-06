from v_chess.enums import GameOverReason, MoveLegalityReason, BoardLegalityReason, Color
from v_chess.game_state import GameState, CrazyhouseGameState
from v_chess.move import Move
from v_chess.piece import Pawn
from v_chess.square import Square
from .standard import StandardRules


class CrazyhouseRules(StandardRules):
    """Rules for Crazyhouse chess variant."""
    MoveLegalityReason = MoveLegalityReason.load("Crazyhouse")
    BoardLegalityReason = BoardLegalityReason.load("Crazyhouse")
    GameOverReason = GameOverReason.load("Crazyhouse")

    @property
    def name(self) -> str:
        """The human-readable name of the variant."""
        return "Crazyhouse"

    def apply_move(self, state: GameState, move: Move) -> CrazyhouseGameState:
        """Applies a move, handling pocket updates for captures and drops."""
        if move.is_drop:
            return self._apply_drop(state, move)

        # Standard move (might capture)
        next_state_base = super().apply_move(state, move)

        # Recalculate capture based on current state (before move)
        moving_piece = state.board.get_piece(move.start)
        target_piece = state.board.get_piece(move.end)

        captured_piece_to_pocket = None
        if target_piece:
            captured_piece_to_pocket = target_piece
        elif isinstance(moving_piece, Pawn) and move.end == state.ep_square:
            # En Passant
            from v_chess.enums import Direction
            direction = Direction.DOWN if moving_piece.color == Color.WHITE else Direction.UP
            captured_sq = move.end.adjacent(direction)
            captured_piece_to_pocket = state.board.get_piece(captured_sq)

        # Get current pockets
        current_pockets = ((), ())
        if isinstance(state, CrazyhouseGameState):
            current_pockets = state.pockets

        new_pockets = [list(current_pockets[0]), list(current_pockets[1])]

        if captured_piece_to_pocket:
            pocket_color_idx = 0 if state.turn == Color.WHITE else 1
            captured_piece_type = type(captured_piece_to_pocket)

            # Create a piece of the same type but with the capturer's color
            new_piece = captured_piece_type(state.turn)
            new_pockets[pocket_color_idx].append(new_piece)
            new_pockets[pocket_color_idx].sort(key=lambda p: p.fen.upper())

        return CrazyhouseGameState(
            board=next_state_base.board,
            turn=next_state_base.turn,
            castling_rights=next_state_base.castling_rights,
            ep_square=next_state_base.ep_square,
            halfmove_clock=next_state_base.halfmove_clock,
            fullmove_count=next_state_base.fullmove_count,
            repetition_count=next_state_base.repetition_count,
            pockets=(tuple(new_pockets[0]), tuple(new_pockets[1]))
        )

    def _apply_drop(self, state: GameState, move: Move) -> CrazyhouseGameState:
        """Handles piece dropping logic."""
        if not move.is_drop:
            raise ValueError("Not a drop move")

        new_board = state.board.copy()
        new_board.set_piece(move.drop_piece, move.end)

        # Update pockets
        current_pockets = ((), ())
        if isinstance(state, CrazyhouseGameState):
            current_pockets = state.pockets

        pocket_idx = 0 if state.turn == Color.WHITE else 1
        my_pocket = list(current_pockets[pocket_idx])

        found = False
        for i, p in enumerate(my_pocket):
            if type(p) == type(move.drop_piece):
                my_pocket.pop(i)
                found = True
                break

        if not found:
            raise ValueError("Piece not in pocket")

        new_pockets = [list(current_pockets[0]), list(current_pockets[1])]
        new_pockets[pocket_idx] = my_pocket

        new_halfmove_clock = state.halfmove_clock + 1
        new_fullmove_count = state.fullmove_count + (1 if state.turn == Color.BLACK else 0)

        return CrazyhouseGameState(
            board=new_board,
            turn=state.turn.opposite,
            castling_rights=state.castling_rights,
            ep_square=None,
            halfmove_clock=new_halfmove_clock,
            fullmove_count=new_fullmove_count,
            repetition_count=1,
            pockets=(tuple(new_pockets[0]), tuple(new_pockets[1]))
        )

    def get_theoretical_moves(self, state: GameState):
        """Yields all legal moves including drops from pocket."""
        yield from super().get_theoretical_moves(state)

        if not isinstance(state, CrazyhouseGameState):
            return

        pocket_idx = 0 if state.turn == Color.WHITE else 1
        pocket = state.pockets[pocket_idx]
        if not pocket:
            return

        unique_pieces = {type(p): p for p in pocket}.values()

        # Optimized: Iterate all 64 squares and check occupancy
        for r in range(8):
            for c in range(8):
                sq = Square(r, c)
                if state.board.get_piece(sq) is None:
                    for p in unique_pieces:
                        if isinstance(p, Pawn) and (r == 0 or r == 7):
                            continue
                        yield Move(Square(None), sq, None, p, player_to_move=state.turn)

    def move_pseudo_legality_reason(self, state: GameState, move: Move) -> MoveLegalityReason:
        """Checks pseudo-legality, including drop moves."""
        if move.is_drop:
            if not isinstance(state, CrazyhouseGameState):
                return self.MoveLegalityReason.NO_PIECE

            pocket_idx = 0 if state.turn == Color.WHITE else 1
            pocket = state.pockets[pocket_idx]

            has_piece = any(type(p) == type(move.drop_piece) for p in pocket)
            if not has_piece:
                return self.MoveLegalityReason.NO_PIECE

            if state.board.get_piece(move.end) is not None:
                return self.MoveLegalityReason.PATH_BLOCKED

            if isinstance(move.drop_piece, Pawn) and (move.end.row == 0 or move.end.row == 7):
                return self.MoveLegalityReason.NOT_IN_MOVESET

            return self.MoveLegalityReason.LEGAL

        return super().move_pseudo_legality_reason(state, move)
