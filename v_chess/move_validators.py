from typing import TYPE_CHECKING, Optional
from v_chess.enums import MoveLegalityReason, Color

if TYPE_CHECKING:
    from v_chess.game_state import GameState
    from v_chess.move import Move
    from v_chess.rules import Rules

def validate_piece_presence(state: "GameState", move: "Move", rules: "Rules") -> Optional[MoveLegalityReason]:
    """Ensures a piece exists at the starting square (unless it's a drop)."""
    if move.is_drop:
        return None
    piece = state.board.get_piece(move.start)
    if piece is None:
        cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
        return getattr(cls, "NO_PIECE", MoveLegalityReason.NO_PIECE)
    return None

def validate_turn(state: "GameState", move: "Move", rules: "Rules") -> Optional[MoveLegalityReason]:
    """Ensures the piece being moved belongs to the active player."""
    if move.is_drop:
        if move.player_to_move and move.player_to_move != state.turn:
             cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
             return getattr(cls, "WRONG_COLOR", MoveLegalityReason.WRONG_COLOR)
        return None
        
    piece = state.board.get_piece(move.start)
    if piece and piece.color != state.turn:
        cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
        return getattr(cls, "WRONG_COLOR", MoveLegalityReason.WRONG_COLOR)
    return None

def validate_friendly_capture(state: "GameState", move: "Move", rules: "Rules") -> Optional[MoveLegalityReason]:
    """Ensures the move does not capture a piece of the same color (except castling in 960)."""
    target = state.board.get_piece(move.end)
    if target and target.color == state.turn:
        from v_chess.piece import King, Rook
        piece = state.board.get_piece(move.start)
        if isinstance(piece, King) and isinstance(target, Rook):
             if rules.name == "Chess960":
                  return None
        
        cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
        return getattr(cls, "OWN_PIECE_CAPTURE", MoveLegalityReason.OWN_PIECE_CAPTURE)
    return None

def validate_moveset(state: "GameState", move: "Move", rules: "Rules") -> Optional[MoveLegalityReason]:
    """Checks if the move is physically possible for the piece type (geometry)."""
    if move.is_drop:
        return None
        
    piece = state.board.get_piece(move.start)
    if not piece: return None
    
    from v_chess.piece import Pawn, King
    
    in_moveset = move.end in piece.theoretical_moves(move.start)
    
    is_pawn_double_push = False
    if isinstance(piece, Pawn):
        is_start_rank = (move.start.row == 6 if piece.color == Color.WHITE else move.start.row == 1)
        if rules.name == "Horde" and piece.color == Color.WHITE and move.start.row == 7:
            is_start_rank = True
            
        direction = piece.direction
        one_step = move.start.get_step(direction)
        two_step = one_step.get_step(direction) if one_step and not one_step.is_none_square else None
        if is_start_rank and move.end == two_step:
            is_pawn_double_push = True
    
    is_castling_attempt = False
    if isinstance(piece, King):
        if abs(move.start.col - move.end.col) == 2:
            is_castling_attempt = True
        elif rules.name == "Chess960":
            target = state.board.get_piece(move.end)
            from v_chess.piece import Rook
            if isinstance(target, Rook) and target.color == piece.color:
                is_castling_attempt = True
    
    if not (in_moveset or is_pawn_double_push or is_castling_attempt):
        cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
        return getattr(cls, "NOT_IN_MOVESET", MoveLegalityReason.NOT_IN_MOVESET)
    return None

def validate_path(state: "GameState", move: "Move", rules: "Rules") -> Optional[MoveLegalityReason]:
    """Ensures the path between start and end is not blocked."""
    if move.is_drop:
        return None
        
    piece = state.board.get_piece(move.start)
    if not piece: return None
    
    from v_chess.piece import Pawn, King, Rook
    if isinstance(piece, King):
         if abs(move.start.col - move.end.col) < 2:
              if rules.name == "Chess960":
                   target = state.board.get_piece(move.end)
                   if isinstance(target, Rook) and target.color == piece.color:
                        return None
              return None
         elif abs(move.start.col - move.end.col) == 2:
              return None

    from v_chess.piece import Knight
    if isinstance(piece, Knight):
        return None

    if isinstance(piece, Pawn):
        direction = piece.direction
        one_step = move.start.get_step(direction)
        two_step = one_step.get_step(direction) if one_step and not one_step.is_none_square else None
        if move.end == two_step:
            if state.board.get_piece(one_step) is not None or state.board.get_piece(two_step) is not None:
                cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
                return getattr(cls, "PATH_BLOCKED", MoveLegalityReason.PATH_BLOCKED)
            return None

    unblocked = rules.unblocked_paths(state.board, piece, piece.theoretical_move_paths(move.start))
    if move.end not in unblocked:
        cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
        return getattr(cls, "PATH_BLOCKED", MoveLegalityReason.PATH_BLOCKED)
        
    return None

def validate_pawn_capture(state: "GameState", move: "Move", rules: "Rules") -> Optional[MoveLegalityReason]:
    """Enforces pawn capture/non-capture rules (Vertical vs Diagonal)."""
    piece = state.board.get_piece(move.start)
    from v_chess.piece import Pawn
    if not isinstance(piece, Pawn):
        return None
        
    target = state.board.get_piece(move.end)
    is_capture = target is not None or move.end == state.ep_square
    
    if move.is_vertical and is_capture:
        cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
        return getattr(cls, "FORWARD_PAWN_CAPTURE", MoveLegalityReason.FORWARD_PAWN_CAPTURE)

    if move.is_diagonal and not is_capture:
        cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
        return getattr(cls, "PAWN_DIAGONAL_NON_CAPTURE", MoveLegalityReason.PAWN_DIAGONAL_NON_CAPTURE)
        
    return None

def validate_promotion(state: "GameState", move: "Move", rules: "Rules") -> Optional[MoveLegalityReason]:
    """Ensures pawns promote when and only when they reach the last rank."""
    piece = state.board.get_piece(move.start)
    from v_chess.piece import Pawn, King
    
    is_pawn = isinstance(piece, Pawn)
    is_promo_rank = move.end.is_promotion_row(state.turn)
    
    if is_pawn and is_promo_rank and move.promotion_piece is None:
        cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
        return getattr(cls, "NON_PROMOTION", MoveLegalityReason.NON_PROMOTION)
        
    if move.promotion_piece:
        if not is_pawn or not is_promo_rank:
            cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
            return getattr(cls, "EARLY_PROMOTION", MoveLegalityReason.EARLY_PROMOTION)
        if isinstance(move.promotion_piece, King):
            cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
            return getattr(cls, "KING_PROMOTION", MoveLegalityReason.KING_PROMOTION)
            
    return None

def validate_standard_castling(state: "GameState", move: "Move", rules: "Rules") -> Optional[MoveLegalityReason]:
    """Validates standard castling (O-O, O-O-O)."""
    piece = state.board.get_piece(move.start)
    from v_chess.piece import King
    if not (isinstance(piece, King) and abs(move.start.col - move.end.col) == 2):
        return None
        
    reason = rules.castling_legality_reason(state, move, piece)
    cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
    return reason if reason != cls.LEGAL else None

def validate_king_safety(state: "GameState", move: "Move", rules: "Rules") -> Optional[MoveLegalityReason]:
    """Ensures the move does not leave the player's own King in check."""
    from v_chess.piece import King
    if rules.has_check:
        has_king = any(isinstance(p, King) and p.color == state.turn for p in state.board.values())
        if has_king and rules.king_left_in_check(state, move):
            cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
            return getattr(cls, "KING_LEFT_IN_CHECK", MoveLegalityReason.KING_LEFT_IN_CHECK)
    return None

def validate_mandatory_capture(state: "GameState", move: "Move", rules: "Rules") -> Optional[MoveLegalityReason]:
    """Enforces mandatory captures (e.g., in Antichess)."""
    from v_chess.piece import Pawn
    is_capture = state.board.get_piece(move.end) is not None
    if not is_capture:
        piece = state.board.get_piece(move.start)
        if piece and isinstance(piece, Pawn) and move.end == state.ep_square:
            is_capture = True
    
    if is_capture:
        return None
        
    for opt_move in rules.get_theoretical_moves(state):
        if rules.move_pseudo_legality_reason(state, opt_move) == MoveLegalityReason.LEGAL:
            opt_is_cap = state.board.get_piece(opt_move.end) is not None
            if not opt_is_cap:
                opt_piece = state.board.get_piece(opt_move.start)
                if opt_piece and isinstance(opt_piece, Pawn) and opt_move.end == state.ep_square:
                    opt_is_cap = True
            
            if opt_is_cap:
                cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
                return getattr(cls, "MANDATORY_CAPTURE", MoveLegalityReason.MANDATORY_CAPTURE)
    
    return None

def validate_horde_pawn(state: "GameState", move: "Move", rules: "Rules") -> Optional[MoveLegalityReason]:
    """Handles Horde-specific pawn rules (rank 1 double push)."""
    from v_chess.piece import Pawn
    from v_chess.enums import Direction
    piece = state.board.get_piece(move.start)
    if piece and isinstance(piece, Pawn) and piece.color == Color.WHITE:
        if move.start.row == 7:
            one_step = move.start.get_step(Direction.UP)
            two_step = one_step.get_step(Direction.UP) if one_step else None
            if move.end == two_step:
                if state.board.get_piece(one_step) is None and state.board.get_piece(two_step) is None:
                    return None # This validator approves it
    return None

def validate_antichess_castling(state: "GameState", move: "Move", rules: "Rules") -> Optional[MoveLegalityReason]:
    """Explicitly blocks castling in Antichess."""
    piece = state.board.get_piece(move.start)
    from v_chess.piece import King
    if isinstance(piece, King) and abs(move.start.col - move.end.col) > 1:
        cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
        return getattr(cls, "CASTLING_DISABLED", MoveLegalityReason.CASTLING_DISABLED)
    return None

def validate_crazyhouse_drop(state: "GameState", move: "Move", rules: "Rules") -> Optional[MoveLegalityReason]:
    """Validates piece drops in Crazyhouse."""
    if not move.is_drop:
        return None
        
    from v_chess.game_state import CrazyhouseGameState
    from v_chess.piece import Pawn
    
    if not isinstance(state, CrazyhouseGameState):
        cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
        return getattr(cls, "NO_PIECE", MoveLegalityReason.NO_PIECE)

    pocket_idx = 0 if state.turn == Color.WHITE else 1
    pocket = state.pockets[pocket_idx]

    has_piece = any(type(p) == type(move.drop_piece) for p in pocket)
    if not has_piece:
        cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
        return getattr(cls, "NO_PIECE", MoveLegalityReason.NO_PIECE)

    if state.board.get_piece(move.end) is not None:
        cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
        return getattr(cls, "PATH_BLOCKED", MoveLegalityReason.PATH_BLOCKED)

    if isinstance(move.drop_piece, Pawn) and (move.end.row == 0 or move.end.row == 7):
        cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
        return getattr(cls, "NOT_IN_MOVESET", MoveLegalityReason.NOT_IN_MOVESET)

    return None

def validate_atomic_move(state: "GameState", move: "Move", rules: "Rules") -> Optional[MoveLegalityReason]:
    """Enforces Atomic-specific move constraints."""
    from v_chess.piece import King, Pawn
    from v_chess.enums import Direction
    from dataclasses import replace
    
    piece = state.board.get_piece(move.start)
    if isinstance(piece, King):
        if state.board.get_piece(move.end) or move.end == state.ep_square:
            cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
            return getattr(cls, "OWN_PIECE_CAPTURE", MoveLegalityReason.OWN_PIECE_CAPTURE)

    sim_board = state.board.copy()
    sim_board.move_piece(piece, move.start, move.end)
    
    is_ep = isinstance(piece, Pawn) and move.end == state.ep_square
    if is_ep:
        d = Direction.DOWN if piece.color == Color.WHITE else Direction.UP
        sim_board.remove_piece(move.end.adjacent(d))
        
    dummy_next = replace(state, board=sim_board, turn=state.turn.opposite)
    final_state = rules.post_move_actions(state, move, dummy_next)
    
    own_king_exists = any(isinstance(p, King) and p.color == state.turn 
                          for p in final_state.board.values())

    cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
    if not own_king_exists:
        return getattr(cls, "KING_EXPLODED", MoveLegalityReason.KING_EXPLODED)

    opp_king_exists = any(isinstance(p, King) and p.color == state.turn.opposite 
                           for p in final_state.board.values())

    if not opp_king_exists:
        return None

    if rules.inactive_player_in_check(final_state):
         return getattr(cls, "KING_LEFT_IN_CHECK", MoveLegalityReason.KING_LEFT_IN_CHECK)

    wk = [sq for sq, p in final_state.board.items() if isinstance(p, King) and p.color == Color.WHITE]
    bk = [sq for sq, p in final_state.board.items() if isinstance(p, King) and p.color == Color.BLACK]
    if wk and bk and wk[0].is_adjacent_to(bk[0]):
        return getattr(cls, "KING_EXPLODED", MoveLegalityReason.KING_EXPLODED)

    return None

def validate_racing_kings_move(state: "GameState", move: "Move", rules: "Rules") -> Optional[MoveLegalityReason]:
    """Enforces Racing Kings constraints."""
    next_state = rules.apply_move(state, move)
    cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
    
    if rules.is_check(next_state):
        return getattr(cls, "GIVES_CHECK", MoveLegalityReason.GIVES_CHECK)

    if rules.inactive_player_in_check(next_state):
         return getattr(cls, "KING_LEFT_IN_CHECK", MoveLegalityReason.KING_LEFT_IN_CHECK)
         
    return None

def validate_chess960_castling(state: "GameState", move: "Move", rules: "Rules") -> Optional[MoveLegalityReason]:
    """Validates 960-specific castling."""
    piece = state.board.get_piece(move.start)
    from v_chess.piece import King, Rook
    if not isinstance(piece, King):
        return None
        
    is_castling = abs(move.start.col - move.end.col) > 1
    target = state.board.get_piece(move.end)
    if isinstance(target, Rook) and target.color == piece.color:
        is_castling = True
        
    if not is_castling:
        return None
        
    reason = rules.castling_legality_reason(state, move, piece)
    cls = getattr(rules, "MoveLegalityReason", MoveLegalityReason)
    return reason if reason != cls.LEGAL else None