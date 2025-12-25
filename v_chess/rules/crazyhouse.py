from dataclasses import replace
from v_chess.enums import GameOverReason, MoveLegalityReason, BoardLegalityReason, Color
from v_chess.game_state import CrazyhouseGameState
from v_chess.move import Move
from v_chess.piece import Pawn, Piece
from v_chess.square import Square
from .standard import StandardRules


class CrazyhouseRules(StandardRules):
    MoveLegalityReason = MoveLegalityReason.load("Crazyhouse")
    BoardLegalityReason = BoardLegalityReason.load("Crazyhouse")
    GameOverReason = GameOverReason.load("Crazyhouse")

    @property
    def name(self) -> str:
        return "Crazyhouse"

    @property
    def fen_type(self) -> str:
        return "crazyhouse"

    def apply_move(self, move: Move) -> CrazyhouseGameState:
        if move.is_drop:
            return self._apply_drop(move)
        
        # Standard move (might capture)
        next_state_base = super().apply_move(move)
        
        # Recalculate capture based on current state (before move)
        moving_piece = self.state.board.get_piece(move.start)
        target_piece = self.state.board.get_piece(move.end)
        
        captured_piece_to_pocket = None
        if target_piece:
            captured_piece_to_pocket = target_piece
        elif isinstance(moving_piece, Pawn) and move.end == self.state.ep_square:
            # En Passant
            from v_chess.enums import Direction
            direction = Direction.DOWN if moving_piece.color == Color.WHITE else Direction.UP
            captured_sq = move.end.adjacent(direction)
            captured_piece_to_pocket = self.state.board.get_piece(captured_sq)

        # Get current pockets
        current_pockets = ((), ())
        if isinstance(self.state, CrazyhouseGameState):
            current_pockets = self.state.pockets
            
        new_pockets = [list(current_pockets[0]), list(current_pockets[1])]
        
        if captured_piece_to_pocket:
            pocket_color_idx = 0 if self.state.turn == Color.WHITE else 1
            captured_piece_type = type(captured_piece_to_pocket)
            
            # Create a piece of the same type but with the capturer's color
            new_piece = captured_piece_type(self.state.turn)
            new_pockets[pocket_color_idx].append(new_piece)
            new_pockets[pocket_color_idx].sort(key=lambda p: p.fen.upper())

        next_state = CrazyhouseGameState(
            board=next_state_base.board,
            turn=next_state_base.turn,
            castling_rights=next_state_base.castling_rights,
            ep_square=next_state_base.ep_square,
            halfmove_clock=next_state_base.halfmove_clock,
            fullmove_count=next_state_base.fullmove_count,
            rules=next_state_base.rules,
            repetition_count=next_state_base.repetition_count,
            pockets=(tuple(new_pockets[0]), tuple(new_pockets[1]))
        )
        next_state.rules.state = next_state
        return next_state

    def _apply_drop(self, move: Move) -> CrazyhouseGameState:
        if not move.is_drop:
            raise ValueError("Not a drop move")
            
        new_board = self.state.board.copy()
        new_board.set_piece(move.drop_piece, move.end)
        
        # Update pockets
        current_pockets = ((), ())
        if isinstance(self.state, CrazyhouseGameState):
            current_pockets = self.state.pockets
            
        pocket_idx = 0 if self.state.turn == Color.WHITE else 1
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
        
        new_halfmove_clock = 0
        new_fullmove_count = self.state.fullmove_count
        if self.state.turn == Color.BLACK:
            new_fullmove_count += 1
            
        new_rules = self.__class__()
        new_state = CrazyhouseGameState(
            board=new_board,
            turn=self.state.turn.opposite,
            castling_rights=self.state.castling_rights,
            ep_square=None,
            halfmove_clock=new_halfmove_clock,
            fullmove_count=new_fullmove_count,
            rules=new_rules,
            repetition_count=1,
            pockets=(tuple(new_pockets[0]), tuple(new_pockets[1]))
        )
        new_rules.state = new_state
        return new_state

    def get_theoretical_moves(self):
        yield from super().get_theoretical_moves()
        
        if not isinstance(self.state, CrazyhouseGameState):
            return
            
        pocket_idx = 0 if self.state.turn == Color.WHITE else 1
        pocket = self.state.pockets[pocket_idx]
        if not pocket:
            return
            
        unique_pieces = {type(p): p for p in pocket}.values()
        
        # Optimized: Iterate all 64 squares and check occupancy
        for r in range(8):
            for c in range(8):
                sq = Square(r, c)
                if self.state.board.get_piece(sq) is None:
                    for p in unique_pieces:
                        if isinstance(p, Pawn) and (r == 0 or r == 7):
                            continue
                        yield Move(Square(None), sq, None, p, player_to_move=self.state.turn)

    def move_pseudo_legality_reason(self, move: Move) -> MoveLegalityReason:
        if move.is_drop:
            if not isinstance(self.state, CrazyhouseGameState):
                return self.MoveLegalityReason.NO_PIECE
                
            pocket_idx = 0 if self.state.turn == Color.WHITE else 1
            pocket = self.state.pockets[pocket_idx]
            
            has_piece = any(type(p) == type(move.drop_piece) for p in pocket)
            if not has_piece:
                return self.MoveLegalityReason.NO_PIECE
            
            if self.state.board.get_piece(move.end) is not None:
                return self.MoveLegalityReason.PATH_BLOCKED
                
            if isinstance(move.drop_piece, Pawn) and (move.end.row == 0 or move.end.row == 7):
                return self.MoveLegalityReason.NOT_IN_MOVESET
                
            return self.MoveLegalityReason.LEGAL
            
        return super().move_pseudo_legality_reason(move)