
from v_chess.enums import Color, Direction
from v_chess.piece import Piece, Pawn, Knight, Bishop, Rook, Queen, King
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from v_chess.board import Board
    from v_chess.square import Square

# Precompute Leaper Attacks
KNIGHT_ATTACKS = [0] * 64
KING_ATTACKS = [0] * 64

def _init_tables():
    for sq in range(64):
        # Knight
        r, c = divmod(sq, 8)
        k_moves = [
            (r-2, c-1), (r-2, c+1), (r-1, c-2), (r-1, c+2),
            (r+1, c-2), (r+1, c+2), (r+2, c-1), (r+2, c+1)
        ]
        mask = 0
        for nr, nc in k_moves:
            if 0 <= nr < 8 and 0 <= nc < 8:
                mask |= (1 << (nr * 8 + nc))
        KNIGHT_ATTACKS[sq] = mask
        
        # King
        ki_moves = [
            (r-1, c-1), (r-1, c), (r-1, c+1),
            (r, c-1),             (r, c+1),
            (r+1, c-1), (r+1, c), (r+1, c+1)
        ]
        mask = 0
        for nr, nc in ki_moves:
            if 0 <= nr < 8 and 0 <= nc < 8:
                mask |= (1 << (nr * 8 + nc))
        KING_ATTACKS[sq] = mask

_init_tables()

class BitboardState:
    def __init__(self):
        self.pieces = {
            Color.WHITE: {Pawn: 0, Knight: 0, Bishop: 0, Rook: 0, Queen: 0, King: 0},
            Color.BLACK: {Pawn: 0, Knight: 0, Bishop: 0, Rook: 0, Queen: 0, King: 0}
        }
        self.occupied_co = {Color.WHITE: 0, Color.BLACK: 0}
        self.occupied = 0

    def copy(self) -> 'BitboardState':
        new_bb = BitboardState()
        for color in Color:
            for p_type, mask in self.pieces[color].items():
                new_bb.pieces[color][p_type] = mask
        new_bb.occupied_co = self.occupied_co.copy()
        new_bb.occupied = self.occupied
        return new_bb

    def update_occupancy(self):
        self.occupied_co[Color.WHITE] = (
            self.pieces[Color.WHITE][Pawn] | self.pieces[Color.WHITE][Knight] |
            self.pieces[Color.WHITE][Bishop] | self.pieces[Color.WHITE][Rook] |
            self.pieces[Color.WHITE][Queen] | self.pieces[Color.WHITE][King]
        )
        self.occupied_co[Color.BLACK] = (
            self.pieces[Color.BLACK][Pawn] | self.pieces[Color.BLACK][Knight] |
            self.pieces[Color.BLACK][Bishop] | self.pieces[Color.BLACK][Rook] |
            self.pieces[Color.BLACK][Queen] | self.pieces[Color.BLACK][King]
        )
        self.occupied = self.occupied_co[Color.WHITE] | self.occupied_co[Color.BLACK]

    def set_piece(self, square_idx: int, piece: Piece):
        self.pieces[piece.color][type(piece)] |= (1 << square_idx)
        self.update_occupancy()

    def remove_piece(self, square_idx: int, piece: Piece):
        self.pieces[piece.color][type(piece)] &= ~(1 << square_idx)
        self.update_occupancy()
        
    def get_piece_mask(self, piece_type: type, color: Color) -> int:
        return self.pieces[color].get(piece_type, 0)
        
    def is_attacked(self, square_idx: int, by_color: Color, occupancy_override: int | None = None) -> bool:
        """Check if square is attacked by pieces of by_color."""
        occ = occupancy_override if occupancy_override is not None else self.occupied
        
        # 1. Knights
        if (KNIGHT_ATTACKS[square_idx] & self.pieces[by_color][Knight]):
            return True
            
        # 2. King
        if (KING_ATTACKS[square_idx] & self.pieces[by_color][King]):
            return True
            
        # 3. Sliders
        ortho_attackers = self.pieces[by_color][Rook] | self.pieces[by_color][Queen]
        if ortho_attackers and self._check_slider(square_idx, ortho_attackers, Direction.straight(), occ):
            return True

        diag_attackers = self.pieces[by_color][Bishop] | self.pieces[by_color][Queen]
        if diag_attackers and self._check_slider(square_idx, diag_attackers, Direction.diagonal(), occ):
            return True

        # 4. Pawns
        r, c = divmod(square_idx, 8)
        if by_color == Color.WHITE:
            start_row = r + 1
            if start_row < 8:
                if c > 0:
                    if (self.pieces[Color.WHITE][Pawn] & (1 << (start_row * 8 + c - 1))): return True
                if c < 7:
                    if (self.pieces[Color.WHITE][Pawn] & (1 << (start_row * 8 + c + 1))): return True
        else:
            start_row = r - 1
            if start_row >= 0:
                if c > 0:
                    if (self.pieces[Color.BLACK][Pawn] & (1 << (start_row * 8 + c - 1))): return True
                if c < 7:
                    if (self.pieces[Color.BLACK][Pawn] & (1 << (start_row * 8 + c + 1))): return True
                    
        return False

    def is_king_attacked_after_move(self, move: 'Move', color: Color, board: 'Board', ep_square: 'Square | None' = None) -> bool:
        """
        Efficiently check if the king of the given color is attacked after a move.
        Avoids full Board.copy() by locally manipulating bitboards.
        """
        start_idx = move.start.index
        end_idx = move.end.index
        
        moving_piece = board.get_piece(move.start)
        if not moving_piece: return False
        
        target_piece = board.get_piece(move.end)
        is_ep = isinstance(moving_piece, Pawn) and move.end == ep_square
        
        # Save current state
        orig_pieces_white = {k: v for k, v in self.pieces[Color.WHITE].items()}
        orig_pieces_black = {k: v for k, v in self.pieces[Color.BLACK].items()}
        
        # Apply move
        self.pieces[moving_piece.color][type(moving_piece)] &= ~(1 << start_idx)
        self.pieces[moving_piece.color][type(moving_piece)] |= (1 << end_idx)
        
        if target_piece:
            self.pieces[target_piece.color][type(target_piece)] &= ~(1 << end_idx)
            
        if is_ep:
            direction = Direction.DOWN if moving_piece.color == Color.WHITE else Direction.UP
            captured_sq = move.end.adjacent(direction)
            if not captured_sq.is_none_square:
                self.pieces[moving_piece.color.opposite][Pawn] &= ~(1 << captured_sq.index)

        self.update_occupancy()
        
        # Find king
        king_mask = self.pieces[color][King]
        if not king_mask:
             king_idx = -1
        else:
             king_idx = (king_mask & -king_mask).bit_length() - 1
        
        is_attacked = False
        if king_idx != -1:
            is_attacked = self.is_attacked(king_idx, color.opposite)
        
        # Restore state
        self.pieces[Color.WHITE] = orig_pieces_white
        self.pieces[Color.BLACK] = orig_pieces_black
        self.update_occupancy()
        
        return is_attacked

    def _check_slider(self, square_idx, attackers, directions, occupied):
        for d in directions:
            ray = d.get_ray_mask(square_idx)
            if not (ray & attackers): 
                continue # No attackers in this direction line at all
            
            blockers = ray & occupied
            if not blockers:
                # No blockers, but there ARE attackers in the ray (checked above)
                return True
                
            # There are blockers. Check if the FIRST blocker is an attacker.
            idx_delta = d.value[1] * 8 + d.value[0]
            
            if idx_delta > 0: # Increasing index (DOWN, RIGHT, etc)
                # First blocker is LSB (smallest index)
                first_blocker_mask = blockers & -blockers
            else: # Decreasing index (UP, LEFT)
                # First blocker is MSB (largest index)
                # MSB: 1 << (blockers.bit_length() - 1)
                first_blocker_mask = 1 << (blockers.bit_length() - 1)
                
            if first_blocker_mask & attackers:
                return True
                
        return False
