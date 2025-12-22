
from oop_chess.enums import Color, Direction
from oop_chess.piece import Piece, Pawn, Knight, Bishop, Rook, Queen, King
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oop_chess.board import Board
    from oop_chess.square import Square

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
        
    def is_attacked(self, square_idx: int, by_color: Color) -> bool:
        """Check if square is attacked by pieces of by_color."""
        # Pawn attacks (reverse pawn move from square to see if pawn is there)
        # White Pawn attacks sq from (r+1, c+/-1)
        # If by_color is WHITE, we look for white pawns at (r+1, c+/-1)
        # Basically, would a pawn of opposite color on sq attack those squares?
        
        # Super optimized approach:
        # Attackers to `square_idx` are pieces that `square_idx` attacks!
        # E.g. If a Knight on `square_idx` attacks X, then a Knight on X attacks `square_idx`.
        # This symmetry holds for all step pieces (N, K) and sliding pieces (B, R, Q).
        # For Pawns, it's directional.
        
        occ = self.occupied
        
        # 1. Knights
        if (KNIGHT_ATTACKS[square_idx] & self.pieces[by_color][Knight]):
            return True
            
        # 2. King
        if (KING_ATTACKS[square_idx] & self.pieces[by_color][King]):
            return True
            
        # 3. Rooks / Queens (Orthogonal)
        # Use Magic Bitboards or plain ray casting?
        # Using Direction rays for now.
        ortho_attackers = self.pieces[by_color][Rook] | self.pieces[by_color][Queen]
        if ortho_attackers:
            for d in Direction.straight():
                ray = d.get_ray_mask(square_index=square_idx)
                blockers = ray & occ
                if blockers:
                    # Find first blocker
                    if d in (Direction.UP, Direction.LEFT, Direction.UP_LEFT, Direction.UP_RIGHT):
                        # Increasing index?
                        # UP: -8. Decreasing.
                        # LEFT: -1. Decreasing.
                        # UP_LEFT: -9. Decreasing.
                        # Wait, UP is index -8?
                        # Row 0 is top.
                        pass 
                    
                    # Logic reuse:
                    # Just intersect ray with attackers.
                    # If any attacker is closer than first blocker (of ANY type)?
                    pass
        
        # Let's use `get_sliding_attacks` logic logic but inverted?
        # No, easier: Generate attacks FROM square as if it was a Rook/Bishop/Queen.
        # Intersect with enemy R/B/Q.
        
        # Rook-like attacks from `square_idx`
        rook_attacks = 0
        for d in Direction.straight():
            ray = d.get_ray_mask(square_idx)
            # Find closest blocker
            blockers = ray & occ
            if blockers:
                # Identify first blocker based on direction
                d_val = d.value[0] + d.value[1]*8 # col + row*8? No. 
                # UP: (0, -1) -> -8. Decreasing index.
                # MSB is first blocker for decreasing?
                # 0..63.
                # Decreasing means moving from high index to low? 
                # If sq=63. UP -> 55. 
                # So we look for HIGHEST index < 63 in blockers?
                # Yes. MSB of blockers.
                
                # Increasing (DOWN, RIGHT): LSB of blockers.
                
                idx_delta = d.value[1] * 8 + d.value[0]
                if idx_delta > 0: # Increasing
                    first_blocker = blockers & -blockers
                    # Mask is bits from square to blocker (exclusive of square, inclusive of blocker)
                    # Ray includes square to edge.
                    # Ray from blocker includes blocker to edge.
                    # XOR gives square to blocker (exclusive of blocker?).
                    # Actually `d.get_ray_mask` returns ray EXCLUDING start.
                    # So ray from sq: sq+1...edge.
                    # ray from blocker: blocker+1...edge.
                    # XOR: sq+1...blocker.
                    # Including blocker? No.
                    
                    # Simplified:
                    # Just calculate sliding attacks on fly using `Direction`
                    # `get_ray_mask` is simpler.
                    pass
            pass

        # Since I need this to be FAST, I shouldn't re-implement slow logic.
        # I'll implement a fast slider lookup here using the Ray masks I added to Direction.
        
        # Orthogonal
        if ortho_attackers:
            if self._check_slider(square_idx, ortho_attackers, Direction.straight(), occ):
                return True

        # Diagonal
        diag_attackers = self.pieces[by_color][Bishop] | self.pieces[by_color][Queen]
        if diag_attackers:
            if self._check_slider(square_idx, diag_attackers, Direction.diagonal(), occ):
                return True

        # Pawns
        # If by_color is WHITE (attacking UP), they must be at (r+1, c+/-1)
        # So we look at pawn capture squares from `square_idx` for BLACK pawns.
        # i.e. if we are a Black pawn at `square_idx`, where do we capture?
        # (r+1, c+/-1).
        
        r, c = divmod(square_idx, 8)
        
        if by_color == Color.WHITE:
            # Check for White pawns attacking 'square_idx'
            # White pawns come from high ranks (row 1..7) to low (row 0)?
            # No. Row 0 is Top (Black side). Row 7 is Bottom (White side).
            # White moves UP: Row decreases. 6 -> 5.
            # So White pawns are at Row + 1.
            start_row = r + 1
            if start_row < 8:
                if c > 0:
                    if (self.pieces[Color.WHITE][Pawn] & (1 << (start_row * 8 + c - 1))): return True
                if c < 7:
                    if (self.pieces[Color.WHITE][Pawn] & (1 << (start_row * 8 + c + 1))): return True
        else:
            # Black pawns come from Row - 1
            start_row = r - 1
            if start_row >= 0:
                if c > 0:
                    if (self.pieces[Color.BLACK][Pawn] & (1 << (start_row * 8 + c - 1))): return True
                if c < 7:
                    if (self.pieces[Color.BLACK][Pawn] & (1 << (start_row * 8 + c + 1))): return True
                    
        return False

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
