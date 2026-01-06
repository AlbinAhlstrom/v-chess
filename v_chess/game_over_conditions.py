from typing import TYPE_CHECKING, Optional
from v_chess.enums import GameOverReason, Color
from v_chess.piece import King

if TYPE_CHECKING:
    from v_chess.game_state import GameState
    from v_chess.rules import Rules

def evaluate_repetition(state: "GameState", rules: "Rules") -> Optional[GameOverReason]:
    """Draw by threefold repetition."""
    if state.repetition_count >= 3:
        cls = getattr(rules, "GameOverReason", GameOverReason)
        return getattr(cls, "REPETITION", GameOverReason.REPETITION)
    return None

def evaluate_fifty_move_rule(state: "GameState", rules: "Rules") -> Optional[GameOverReason]:
    """Draw by 50-move rule."""
    if state.halfmove_clock >= 100:
        cls = getattr(rules, "GameOverReason", GameOverReason)
        return getattr(cls, "FIFTY_MOVE_RULE", GameOverReason.FIFTY_MOVE_RULE)
    return None

def evaluate_checkmate(state: "GameState", rules: "Rules") -> Optional[GameOverReason]:
    """Win by Checkmate."""
    if rules.is_check(state):
        if not rules.has_legal_moves(state):
            cls = getattr(rules, "GameOverReason", GameOverReason)
            return getattr(cls, "CHECKMATE", GameOverReason.CHECKMATE)
    return None

def evaluate_stalemate(state: "GameState", rules: "Rules") -> Optional[GameOverReason]:
    """Draw by Stalemate."""
    if not rules.is_check(state):
        if not rules.has_legal_moves(state):
            cls = getattr(rules, "GameOverReason", GameOverReason)
            return getattr(cls, "STALEMATE", GameOverReason.STALEMATE)
    return None

def evaluate_king_center_win(state: "GameState", rules: "Rules") -> Optional[GameOverReason]:
    """Win by moving King to the center (KOTH)."""
    center_squares = {(3, 3), (3, 4), (4, 3), (4, 4)}
    for sq, piece in state.board.items():
        if isinstance(piece, King):
            if (sq.row, sq.col) in center_squares:
                cls = getattr(rules, "GameOverReason", GameOverReason)
                return getattr(cls, "KING_ON_HILL", GameOverReason.KING_ON_HILL)
    return None

def evaluate_three_check_win(state: "GameState", rules: "Rules") -> Optional[GameOverReason]:
    """Win by giving check 3 times."""
    from v_chess.game_state import ThreeCheckGameState
    if isinstance(state, ThreeCheckGameState):
        if state.checks[0] >= 3 or state.checks[1] >= 3:
            cls = getattr(rules, "GameOverReason", GameOverReason)
            return getattr(cls, "THREE_CHECKS", GameOverReason.THREE_CHECKS)
    return None

def evaluate_atomic_king_exploded(state: "GameState", rules: "Rules") -> Optional[GameOverReason]:
    """Game over if a king explodes."""
    wk = any(isinstance(p, King) and p.color == Color.WHITE for p in state.board.values())
    bk = any(isinstance(p, King) and p.color == Color.BLACK for p in state.board.values())
    if not wk or not bk:
        cls = getattr(rules, "GameOverReason", GameOverReason)
        return getattr(cls, "KING_EXPLODED", GameOverReason.KING_EXPLODED)
    return None

def evaluate_antichess_win(state: "GameState", rules: "Rules") -> Optional[GameOverReason]:
    """Win by losing all pieces or stalemate."""
    white_pieces = any(p.color == Color.WHITE for p in state.board.values())
    black_pieces = any(p.color == Color.BLACK for p in state.board.values())
    if not white_pieces or not black_pieces:
         cls = getattr(rules, "GameOverReason", GameOverReason)
         return getattr(cls, "ALL_PIECES_CAPTURED", GameOverReason.ALL_PIECES_CAPTURED)
    if not rules.has_legal_moves(state):
         cls = getattr(rules, "GameOverReason", GameOverReason)
         return getattr(cls, "STALEMATE", GameOverReason.STALEMATE)
    return None

def evaluate_horde_win(state: "GameState", rules: "Rules") -> Optional[GameOverReason]:
    """Horde specific win conditions."""
    black_pieces = any(p.color == Color.BLACK for p in state.board.values())
    if not black_pieces:
         cls = getattr(rules, "GameOverReason", GameOverReason)
         return getattr(cls, "ALL_PIECES_CAPTURED", GameOverReason.ALL_PIECES_CAPTURED)
    white_pieces = any(p.color == Color.WHITE for p in state.board.values())
    if not white_pieces:
         cls = getattr(rules, "GameOverReason", GameOverReason)
         return getattr(cls, "ALL_PIECES_CAPTURED", GameOverReason.ALL_PIECES_CAPTURED)
    return None

def evaluate_racing_kings_win(state: "GameState", rules: "Rules") -> Optional[GameOverReason]:
    """Win by reaching the 8th rank."""
    wk_on_8 = False
    bk_on_8 = False
    for sq, piece in state.board.items():
        if isinstance(piece, King) and sq.row == 0:
            if piece.color == Color.WHITE:
                wk_on_8 = True
            else:
                bk_on_8 = True
    cls = getattr(rules, "GameOverReason", GameOverReason)
    if wk_on_8 and bk_on_8:
        return getattr(cls, "STALEMATE", GameOverReason.STALEMATE)
    if bk_on_8:
        return getattr(cls, "KING_TO_EIGHTH_RANK", GameOverReason.KING_TO_EIGHTH_RANK)
    if wk_on_8:
        if state.turn == Color.BLACK:
            return None
        return getattr(cls, "KING_TO_EIGHTH_RANK", GameOverReason.KING_TO_EIGHTH_RANK)
    return None