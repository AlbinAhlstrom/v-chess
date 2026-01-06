from typing import TYPE_CHECKING

from v_chess.enums import Color, Direction
from v_chess.piece import Pawn, Knight, Bishop, Rook, Queen, King, Piece
from v_chess.move import Move
from v_chess.square import Square

if TYPE_CHECKING:
    from v_chess.board import Board


class AttackTables:
    """Singleton provider for precomputed attack masks."""

    _KNIGHT_ATTACKS = [0] * 64
    _KING_ATTACKS = [0] * 64
    _INITIALIZED = False

    @classmethod
    def _initialize(cls):
        if cls._INITIALIZED:
            return

        for sq in range(64):
            r, c = divmod(sq, 8)

            k_moves = [
                (r - 2, c - 1), (r - 2, c + 1), (r - 1, c - 2), (r - 1, c + 2),
                (r + 1, c - 2), (r + 1, c + 2), (r + 2, c - 1), (r + 2, c + 1)
            ]
            mask = 0
            for nr, nc in k_moves:
                if 0 <= nr < 8 and 0 <= nc < 8:
                    mask |= (1 << (nr * 8 + nc))
            cls._KNIGHT_ATTACKS[sq] = mask

            ki_moves = [
                (r - 1, c - 1), (r - 1, c), (r - 1, c + 1),
                (r, c - 1),             (r, c + 1),
                (r + 1, c - 1), (r + 1, c), (r + 1, c + 1)
            ]
            mask = 0
            for nr, nc in ki_moves:
                if 0 <= nr < 8 and 0 <= nc < 8:
                    mask |= (1 << (nr * 8 + nc))
            cls._KING_ATTACKS[sq] = mask

        cls._INITIALIZED = True

    @classmethod
    def knight_attacks(cls, sq_idx: int) -> int:
        if not cls._INITIALIZED:
            cls._initialize()
        return cls._KNIGHT_ATTACKS[sq_idx]

    @classmethod
    def king_attacks(cls, sq_idx: int) -> int:
        if not cls._INITIALIZED:
            cls._initialize()
        return cls._KING_ATTACKS[sq_idx]


class Bitboard:
    """Manages the bitwise state of the chess board.

    Attributes:
        pieces: Nested dictionary mapping Color -> PieceType -> Bitmask.
        occupied_co: Dictionary mapping Color -> Bitmask of all their pieces.
        occupied: Bitmask of all pieces on the board.
    """

    def __init__(self):
        """Initializes an empty Bitboard."""
        self.pieces = {
            Color.WHITE: {Pawn: 0, Knight: 0, Bishop: 0, Rook: 0, Queen: 0, King: 0},
            Color.BLACK: {Pawn: 0, Knight: 0, Bishop: 0, Rook: 0, Queen: 0, King: 0}
        }
        self.occupied_co = {Color.WHITE: 0, Color.BLACK: 0}
        self.occupied = 0

    def copy(self) -> Bitboard:
        """Creates a deep copy of the Bitboard."""
        new_bb = Bitboard()
        for color in Color:
            for p_type, mask in self.pieces[color].items():
                new_bb.pieces[color][p_type] = mask
        new_bb.occupied_co = self.occupied_co.copy()
        new_bb.occupied = self.occupied
        return new_bb

    def update_occupancy(self):
        """Recalculates occupancy bitmasks based on piece positions."""
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
        """Sets a piece at the given square index."""
        self.pieces[piece.color][type(piece)] |= (1 << square_idx)
        self.update_occupancy()

    def remove_piece(self, square_idx: int, piece: Piece):
        """Removes a piece from the given square index."""
        self.pieces[piece.color][type(piece)] &= ~(1 << square_idx)
        self.update_occupancy()

    def get_piece_mask(self, piece_type: type, color: Color) -> int:
        """Returns the bitmask for a specific piece type and color."""
        return self.pieces[color].get(piece_type, 0)

    def piece_at(self, square_index: int) -> tuple[type[Piece] | None, Color | None]:
        """Returns the piece type and color at the given square index."""
        if square_index < 0:
            return None, None

        mask = 1 << square_index
        if not (self.occupied & mask):
            return None, None

        if self.occupied_co[Color.WHITE] & mask:
            for p_type, p_mask in self.pieces[Color.WHITE].items():
                if p_mask & mask:
                    return p_type, Color.WHITE
        else:
            for p_type, p_mask in self.pieces[Color.BLACK].items():
                if p_mask & mask:
                    return p_type, Color.BLACK

        return None, None

    def is_attacked(self, square_idx: int, by_color: Color, occupancy_override: int | None = None) -> bool:
        """Checks if a square is attacked by pieces of a specific color."""
        occ = occupancy_override if occupancy_override is not None else self.occupied

        if (AttackTables.knight_attacks(square_idx) & self.pieces[by_color][Knight]):
            return True

        if (AttackTables.king_attacks(square_idx) & self.pieces[by_color][King]):
            return True

        ortho_attackers = self.pieces[by_color][Rook] | self.pieces[by_color][Queen]
        if ortho_attackers and self._check_slider(square_idx, ortho_attackers, Direction.straight(), occ):
            return True

        diag_attackers = self.pieces[by_color][Bishop] | self.pieces[by_color][Queen]
        if diag_attackers and self._check_slider(square_idx, diag_attackers, Direction.diagonal(), occ):
            return True

        r, c = divmod(square_idx, 8)
        if by_color == Color.WHITE:
            start_row = r + 1
            if start_row < 8:
                if c > 0 and (self.pieces[Color.WHITE][Pawn] & (1 << (start_row * 8 + c - 1))):
                    return True
                if c < 7 and (self.pieces[Color.WHITE][Pawn] & (1 << (start_row * 8 + c + 1))):
                    return True
        else:
            start_row = r - 1
            if start_row >= 0:
                if c > 0 and (self.pieces[Color.BLACK][Pawn] & (1 << (start_row * 8 + c - 1))):
                    return True
                if c < 7 and (self.pieces[Color.BLACK][Pawn] & (1 << (start_row * 8 + c + 1))):
                    return True

        return False

    def is_king_attacked_after_move(self, move: Move, color: Color, board: "Board", ep_square: Square | None = None) -> bool:
        """Checks if the king is under attack after a hypothetical move."""
        start_idx = move.start.index
        end_idx = move.end.index

        if move.is_drop:
            moving_piece = move.drop_piece
        else:
            moving_piece = board.get_piece(move.start)

        if not moving_piece:
            return False

        target_piece = board.get_piece(move.end)
        is_ep = not move.is_drop and isinstance(moving_piece, Pawn) and move.end == ep_square

        orig_pieces_white = {k: v for k, v in self.pieces[Color.WHITE].items()}
        orig_pieces_black = {k: v for k, v in self.pieces[Color.BLACK].items()}

        if not move.is_drop:
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

        king_mask = self.pieces[color][King]
        if not king_mask:
             king_idx = -1
        else:
             king_idx = (king_mask & -king_mask).bit_length() - 1

        is_attacked = False
        if king_idx != -1:
            is_attacked = self.is_attacked(king_idx, color.opposite)

        self.pieces[Color.WHITE] = orig_pieces_white
        self.pieces[Color.BLACK] = orig_pieces_black
        self.update_occupancy()

        return is_attacked

    def _check_slider(self, square_idx: int, attackers: int, directions: list[Direction], occupied: int) -> bool:
        """Helper to check sliding piece attacks."""
        for d in directions:
            ray = d.get_ray_mask(square_idx)
            if not (ray & attackers):
                continue

            blockers = ray & occupied
            if not blockers:
                return True

            idx_delta = d.value[1] * 8 + d.value[0]

            if idx_delta > 0:
                first_blocker_mask = blockers & -blockers
            else:
                first_blocker_mask = 1 << (blockers.bit_length() - 1)

            if first_blocker_mask & attackers:
                return True

        return False


