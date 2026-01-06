from typing import TYPE_CHECKING, Optional
from v_chess.enums import BoardLegalityReason, Color
from v_chess.piece import King, Pawn


if TYPE_CHECKING:
    from v_chess.game_state import GameState
    from v_chess.rules import Rules


def standard_king_count(state: "GameState", rules: "Rules") -> Optional[BoardLegalityReason]:
    """Ensures exactly one king exists for each player."""
    white_kings = state.board.get_pieces(King, Color.WHITE)
    black_kings = state.board.get_pieces(King, Color.BLACK)
    if len(white_kings) < 1: return BoardLegalityReason.NO_WHITE_KING
    if len(black_kings) < 1: return BoardLegalityReason.NO_BLACK_KING
    if len(white_kings + black_kings) > 2: return BoardLegalityReason.TOO_MANY_KINGS
    return None

def black_king_count_horde(state: "GameState", rules: "Rules") -> Optional[BoardLegalityReason]:
    """Ensures at least one black king exists (used in Horde)."""
    black_kings = state.board.get_pieces(King, Color.BLACK)
    if len(black_kings) < 1: return BoardLegalityReason.NO_BLACK_KING
    return None

def pawn_on_backrank(state: "GameState", rules: "Rules") -> Optional[BoardLegalityReason]:
    """Ensures no pawns are on the first or last ranks."""
    for sq, piece in state.board.items():
         if isinstance(piece, Pawn) and (sq.row == 0 or sq.row == 7):
             return BoardLegalityReason.PAWNS_ON_BACKRANK
    return None

def pawn_count_standard(state: "GameState", rules: "Rules") -> Optional[BoardLegalityReason]:
    """Ensures neither side has more than 8 pawns."""
    white_pawns = state.board.get_pieces(Pawn, Color.WHITE)
    black_pawns = state.board.get_pieces(Pawn, Color.BLACK)
    if len(white_pawns) > 8: return BoardLegalityReason.TOO_MANY_WHITE_PAWNS
    if len(black_pawns) > 8: return BoardLegalityReason.TOO_MANY_BLACK_PAWNS
    return None

def black_pawn_count_horde(state: "GameState", rules: "Rules") -> Optional[BoardLegalityReason]:
    """Ensures black doesn't have more than 8 pawns (used in Horde)."""
    black_pawns = state.board.get_pieces(Pawn, Color.BLACK)
    if len(black_pawns) > 8: return BoardLegalityReason.TOO_MANY_BLACK_PAWNS
    return None

def piece_count_promotion_consistency(state: "GameState", rules: "Rules") -> Optional[BoardLegalityReason]:
    """Ensures total piece count is consistent with pawn promotions."""
    white_pawns = state.board.get_pieces(Pawn, Color.WHITE)
    black_pawns = state.board.get_pieces(Pawn, Color.BLACK)
    white_non_pawns = [p for p in state.board.get_pieces(color=Color.WHITE) if not isinstance(p, Pawn)]
    black_non_pawns = [p for p in state.board.get_pieces(color=Color.BLACK) if not isinstance(p, Pawn)]

    if len(white_non_pawns) > (16 - len(white_pawns)): return BoardLegalityReason.TOO_MANY_WHITE_PIECES
    if len(black_non_pawns) > (16 - len(black_pawns)): return BoardLegalityReason.TOO_MANY_BLACK_PIECES
    return None

def castling_rights_consistency(state: "GameState", rules: "Rules") -> Optional[BoardLegalityReason]:
    """Ensures castling rights match current piece positions."""
    if rules.invalid_castling_rights(state):
        return BoardLegalityReason.INVALID_CASTLING_RIGHTS
    return None

def en_passant_target_validity(state: "GameState", rules: "Rules") -> Optional[BoardLegalityReason]:
    """Ensures en passant target square is valid."""
    if state.ep_square is not None and state.ep_square.row not in (2, 5):
        return BoardLegalityReason.INVALID_EP_SQUARE
    return None

def inactive_player_check_safety(state: "GameState", rules: "Rules") -> Optional[BoardLegalityReason]:
    """Ensures the player who just moved didn't leave themselves in check."""
    if rules.inactive_player_in_check(state):
        return BoardLegalityReason.OPPOSITE_CHECK
    return None

def atomic_kings_proximity(state: "GameState", rules: "Rules") -> Optional[BoardLegalityReason]:
    """Ensures kings are not adjacent in Atomic chess."""
    if rules._kings_adjacent(state.board):
        return BoardLegalityReason.KINGS_ADJACENT
    return None

def racing_kings_check_illegality(state: "GameState", rules: "Rules") -> Optional[BoardLegalityReason]:
    """Ensures neither player is in check (used in Racing Kings)."""
    if rules.is_check(state) or rules.inactive_player_in_check(state):
         cls = getattr(rules, "BoardLegalityReason", BoardLegalityReason)
         return getattr(cls, "KING_IN_CHECK", BoardLegalityReason.KING_IN_CHECK)
    return None
