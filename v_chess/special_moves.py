from typing import TYPE_CHECKING, Iterable, Callable, Optional, List
from v_chess.move import Move
from v_chess.enums import Color, Direction
from v_chess.square import Square

if TYPE_CHECKING:
    from v_chess.game_state import GameState
    from v_chess.piece import Piece

# Type Aliases for Modular Rules
# PieceMoveRule: Generates moves for a specific piece at a specific square.
PieceMoveRule = Callable[["GameState", "Square", "Piece"], Iterable[Move]]
# GlobalMoveRule: Generates moves that don't originate from a specific piece on board (e.g. Drops).
GlobalMoveRule = Callable[["GameState"], Iterable[Move]]

def basic_moves(state: "GameState", sq: "Square", piece: "Piece") -> Iterable[Move]:
    """Generates basic moves for a piece, excluding pawn promotions."""
    from v_chess.piece import Pawn
    for end in piece.theoretical_moves(sq):
        if isinstance(piece, Pawn) and end.is_promotion_row(state.turn):
            continue
        yield Move(sq, end, player_to_move=state.turn)

def pawn_promotions(state: "GameState", sq: "Square", piece: "Piece") -> Iterable[Move]:
    """Generates promotion moves for pawns reaching the last rank."""
    from v_chess.piece import Pawn, Queen, Rook, Bishop, Knight, King
    if isinstance(piece, Pawn):
        for end in piece.theoretical_moves(sq):
            if end.is_promotion_row(state.turn):
                for promo_piece_type in [Queen, Rook, Bishop, Knight, King]:
                    yield Move(sq, end, promo_piece_type(state.turn), player_to_move=state.turn)

def pawn_double_push(state: "GameState", sq: "Square", piece: "Piece") -> Iterable[Move]:
    """Generates double push moves for pawns on their starting rank."""
    from v_chess.piece import Pawn
    if isinstance(piece, Pawn):
        is_start_rank = (sq.row == 6 if state.turn == Color.WHITE else sq.row == 1)
        if is_start_rank:
            direction = piece.direction
            one_step = sq.get_step(direction)
            two_step = one_step.get_step(direction) if one_step and not one_step.is_none_square else None
            if two_step and not two_step.is_none_square:
                yield Move(sq, two_step, player_to_move=state.turn)

def standard_castling(state: "GameState", sq: "Square", piece: "Piece") -> Iterable[Move]:
    """Generates standard castling moves (O-O, O-O-O)."""
    from v_chess.piece import King
    if isinstance(piece, King):
        # Potential castling from start square to c/g files
        rank = 7 if state.turn == Color.WHITE else 0
        if sq == Square(rank, 4):
             yield Move(sq, Square(rank, 6), player_to_move=state.turn)
             yield Move(sq, Square(rank, 2), player_to_move=state.turn)

def chess960_castling(state: "GameState", sq: "Square", piece: "Piece") -> Iterable[Move]:
    """Generates 960 castling moves (King-to-Target or King-to-Rook)."""
    from v_chess.piece import King, Rook
    if isinstance(piece, King):
        rank = 7 if state.turn == Color.WHITE else 0
        if sq.row != rank:
            return

        # 1. King-to-Target Notation (c/g files)
        for col in [6, 2]:
             yield Move(sq, Square(rank, col), player_to_move=state.turn)
        
        # 2. King-to-Rook Notation (capturing own rook)
        for col in range(8):
             target_sq = Square(rank, col)
             target_piece = state.board.get_piece(target_sq)
             if isinstance(target_piece, Rook) and target_piece.color == piece.color:
                  yield Move(sq, target_sq, player_to_move=state.turn)

def horde_pawn_double_push(state: "GameState", sq: "Square", piece: "Piece") -> Iterable[Move]:
    """Generates rank 1 double pushes for White pawns in Horde."""
    from v_chess.piece import Pawn
    if state.turn == Color.WHITE and isinstance(piece, Pawn) and sq.row == 7:
        one_step = sq.get_step(Direction.UP)
        two_step = one_step.get_step(Direction.UP) if one_step and not one_step.is_none_square else None
        if two_step and not two_step.is_none_square:
            yield Move(sq, two_step, player_to_move=state.turn)

def crazyhouse_drops(state: "GameState") -> Iterable[Move]:
    """Generates all legal drops from the pocket in Crazyhouse."""
    from v_chess.game_state import CrazyhouseGameState
    from v_chess.piece import Pawn
    
    if not isinstance(state, CrazyhouseGameState):
        return

    pocket_idx = 0 if state.turn == Color.WHITE else 1
    pocket = state.pockets[pocket_idx]
    if not pocket:
        return

    unique_pieces = {type(p): p for p in pocket}.values()

    for r in range(8):
        for c in range(8):
            target_sq = Square(r, c)
            if state.board.get_piece(target_sq) is None:
                for p in unique_pieces:
                    if isinstance(p, Pawn) and (r == 0 or r == 7):
                        continue
                    yield Move(Square(None), target_sq, None, p, player_to_move=state.turn)

crazyhouse_drops.is_global = True