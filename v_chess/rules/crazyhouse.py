from v_chess.enums import GameOverReason, MoveLegalityReason, BoardLegalityReason, Color
from v_chess.game_state import GameState, CrazyhouseGameState
from v_chess.move import Move
from v_chess.piece import Pawn, Piece
from v_chess.square import Square
from .standard import StandardRules
from dataclasses import replace


class CrazyhouseRules(StandardRules):
    """Rules for Crazyhouse chess variant."""
    MoveLegalityReason = MoveLegalityReason.load("Crazyhouse")
    BoardLegalityReason = BoardLegalityReason.load("Crazyhouse")
    GameOverReason = GameOverReason.load("Crazyhouse")

    @property
    def name(self) -> str:
        """The human-readable name of the variant."""
        return "Crazyhouse"

    @property
    def fen_type(self) -> str:
        """The FEN notation type used."""
        return "crazyhouse"

    def get_extra_theoretical_moves(self, state: GameState) -> list[Move]:
        """Yields all legal moves including drops from pocket."""
        moves = []
        if not isinstance(state, CrazyhouseGameState):
            return moves

        pocket_idx = 0 if state.turn == Color.WHITE else 1
        pocket = state.pockets[pocket_idx]
        if not pocket:
            return moves

        unique_pieces = {type(p): p for p in pocket}.values()

        # Optimized: Iterate all 64 squares and check occupancy
        for r in range(8):
            for c in range(8):
                sq = Square(r, c)
                if state.board.get_piece(sq) is None:
                    for p in unique_pieces:
                        if isinstance(p, Pawn) and (r == 0 or r == 7):
                            continue
                        moves.append(Move(Square(None), sq, None, p, player_to_move=state.turn))
        return moves

    def post_move_actions(self, old_state: GameState, move: Move, new_state: GameState) -> GameState:
        """Updates pockets after a move (capture or drop)."""
        # Ensure we are working with a CrazyhouseGameState
        current_pockets = ((), ())
        if isinstance(old_state, CrazyhouseGameState):
            current_pockets = old_state.pockets
            
        new_pockets = [list(current_pockets[0]), list(current_pockets[1])]
        
        if move.is_drop:
            # Remove dropped piece from pocket
            pocket_idx = 0 if old_state.turn == Color.WHITE else 1
            my_pocket = new_pockets[pocket_idx]
            
            found = False
            for i, p in enumerate(my_pocket):
                if type(p) == type(move.drop_piece):
                    my_pocket.pop(i)
                    found = True
                    break
            
            if not found:
                # Should have been caught by validate_move/pseudo check
                pass
                
        else:
            # Check capture
            moving_piece = old_state.board.get_piece(move.start)
            target_piece = old_state.board.get_piece(move.end)
            
            captured_piece = None
            if target_piece:
                captured_piece = target_piece
            elif isinstance(moving_piece, Pawn) and move.end == old_state.ep_square:
                # En Passant
                from v_chess.enums import Direction
                direction = Direction.DOWN if moving_piece.color == Color.WHITE else Direction.UP
                captured_sq = move.end.adjacent(direction)
                captured_piece = old_state.board.get_piece(captured_sq)
                
            if captured_piece:
                pocket_color_idx = 0 if old_state.turn == Color.WHITE else 1
                captured_piece_type = type(captured_piece)
                new_piece = captured_piece_type(old_state.turn)
                new_pockets[pocket_color_idx].append(new_piece)
                new_pockets[pocket_color_idx].sort(key=lambda p: p.fen.upper())

        return CrazyhouseGameState(
            board=new_state.board,
            turn=new_state.turn,
            castling_rights=new_state.castling_rights,
            ep_square=new_state.ep_square,
            halfmove_clock=new_state.halfmove_clock,
            fullmove_count=new_state.fullmove_count,
            repetition_count=new_state.repetition_count,
            pockets=(tuple(new_pockets[0]), tuple(new_pockets[1]))
        )

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