from v_chess.enums import GameOverReason, MoveLegalityReason, BoardLegalityReason, Color, CastlingRight
from v_chess.move import Move
from v_chess.piece import King, Rook
from v_chess.square import Square
from v_chess.game_state import GameState
from .standard import StandardRules
from dataclasses import replace


class Chess960Rules(StandardRules):
    MoveLegalityReason = MoveLegalityReason.load("Chess960")
    BoardLegalityReason = BoardLegalityReason.load("Chess960")
    GameOverReason = GameOverReason.load("Chess960")

    @property
    def name(self) -> str:
        return "Chess960"

    @property
    def starting_fen(self) -> str:
        import random
        # 1. Place Bishops on opposite colors
        # Light squares: 1, 3, 5, 7. Dark: 0, 2, 4, 6.
        b1 = random.choice([1, 3, 5, 7])
        b2 = random.choice([0, 2, 4, 6])

        # 2. Place remaining pieces in empty squares
        remaining_indices = [i for i in range(8) if i not in (b1, b2)]

        # 3. Place Queen
        q_idx = random.choice(remaining_indices)
        remaining_indices.remove(q_idx)

        # 4. Place Knights
        n1_idx = random.choice(remaining_indices)
        remaining_indices.remove(n1_idx)
        n2_idx = random.choice(remaining_indices)
        remaining_indices.remove(n2_idx)

        # 5. Place Rooks and King (King must be between Rooks)
        # remaining_indices has 3 elements left.
        # Sort them: [r1, k, r2]
        remaining_indices.sort()
        r1_idx, k_idx, r2_idx = remaining_indices

        # 6. Build the backrank string
        backrank = [''] * 8
        backrank[b1] = 'B'; backrank[b2] = 'B'
        backrank[q_idx] = 'Q'
        backrank[n1_idx] = 'N'; backrank[n2_idx] = 'N'
        backrank[r1_idx] = 'R'; backrank[r2_idx] = 'R'
        backrank[k_idx] = 'K'

        row_str = "".join(backrank)

        # 7. Build full FEN
        # white backrank row_str.lower() for black
        # Castling rights in 960 use the column letters of the rooks
        # e.g. HAha if rooks are on h and a.
        w_rook_cols = f"{chr(ord('A') + r2_idx)}{chr(ord('A') + r1_idx)}"
        b_rook_cols = f"{chr(ord('a') + r2_idx)}{chr(ord('a') + r1_idx)}"

        fen = f"{row_str.lower()}/pppppppp/8/8/8/8/PPPPPPPP/{row_str} w {w_rook_cols}{b_rook_cols} - 0 1"
        return fen

    def post_move_actions(self, old_state: GameState, move: Move, new_state: GameState) -> GameState:
        # Standard castling rights cleanup in Game handles implicit rook loss.
        # But 960 KxR castling might need explicit rights removal if Game didn't catch it.
        # Game handles KxR castling logic explicitly now.
        
        # We just need to ensure correct rights cleanup if the Game missed something specific to 960 notation
        # But Game looks up rights by piece/rook square.
        
        # Is there anything else?
        # Maybe remove rights if a rook moves/is captured? StandardRules logic handles this via Game.
        
        return new_state

    def invalid_castling_rights(self, state: GameState) -> list[CastlingRight]:
        invalid = []
        for right in state.castling_rights:
            if right == CastlingRight.NONE: continue
            row = 7 if right.color == Color.WHITE else 0
            kings = [p for sq, p in state.board.items()
                     if isinstance(p, King) and p.color == right.color and sq.row == row]
            rook_sq = right.expected_rook_square
            rook = state.board.get_piece(rook_sq)
            if not kings or not (isinstance(rook, Rook) and rook.color == right.color):
                invalid.append(right)
        return invalid

    def move_pseudo_legality_reason(self, state: GameState, move: Move) -> MoveLegalityReason:
        piece = state.board.get_piece(move.start)
        if isinstance(piece, King):
             for legal_castling in self.get_legal_castling_moves(state):
                 if legal_castling.start == move.start and legal_castling.end == move.end:
                      return self.castling_legality_reason(state, move, piece)
             # Also allow King-to-Rook for pseudo-legality (will be validated in apply_move/validate_move)
             target = state.board.get_piece(move.end)
             if isinstance(target, Rook) and target.color == piece.color:
                  # Map King-to-Rook to standard target for validation
                  is_kingside = move.end.col > move.start.col
                  target_col = 6 if is_kingside else 2
                  m_equiv = Move(move.start, Square(move.start.row, target_col))
                  return self.castling_legality_reason(state, m_equiv, piece)

        return super().move_pseudo_legality_reason(state, move)

    def castling_legality_reason(self, state: GameState, move: Move, piece: King) -> MoveLegalityReason:
        target_king_sq = move.end
        row = 7 if piece.color == Color.WHITE else 0
        
        # Check if target is Rook (KxR notation)
        target_piece = state.board.get_piece(target_king_sq)
        if isinstance(target_piece, Rook) and target_piece.color == piece.color:
             # Map to standard target based on direction
             if target_king_sq.col > move.start.col:
                 target_king_sq = Square(row, 6) # Kingside
             else:
                 target_king_sq = Square(row, 2) # Queenside

        is_kingside = target_king_sq.col > move.start.col

        right = None
        if target_king_sq == Square(row, 6): # Kingside
             for r in state.castling_rights:
                 if r.color == piece.color and r.expected_rook_square.col > move.start.col:
                     right = r; break
        elif target_king_sq == Square(row, 2): # Queenside
             for r in state.castling_rights:
                 if r.color == piece.color and r.expected_rook_square.col < move.start.col:
                     right = r; break

        if not right: return MoveLegalityReason.NO_CASTLING_RIGHT

        rook_sq = right.expected_rook_square
        target_king = Square(row, 6) if is_kingside else Square(row, 2)
        target_rook = Square(row, 5) if is_kingside else Square(row, 3)

        k_min, k_max = min(move.start.col, target_king.col), max(move.start.col, target_king.col)
        for c in range(k_min, k_max + 1):
            sq = Square(row, c)
            if sq == move.start: continue
            p = state.board.get_piece(sq)
            if p and sq != rook_sq: return MoveLegalityReason.PATH_BLOCKED

        r_min, r_max = min(rook_sq.col, target_rook.col), max(rook_sq.col, target_rook.col)
        for c in range(r_min, r_max + 1):
            sq = Square(row, c)
            if sq == rook_sq: continue
            p = state.board.get_piece(sq)
            if p and sq != move.start: return MoveLegalityReason.PATH_BLOCKED

        if self.is_check(state): return MoveLegalityReason.CASTLING_FROM_CHECK

        step = 1 if target_king.col > move.start.col else -1
        curr_col = move.start.col + step
        while True:
            sq = Square(row, curr_col)
            if self.is_under_attack(state.board, sq, piece.color.opposite):
                return MoveLegalityReason.CASTLING_THROUGH_CHECK
            if curr_col == target_king.col: break
            curr_col += step

        return MoveLegalityReason.LEGAL

    def get_legal_castling_moves(self, state: GameState) -> list[Move]:
        moves = []
        for sq, piece in state.board.items():
            if isinstance(piece, King) and piece.color == state.turn:
                 for target_col in [6, 2]:
                     m = Move(sq, Square(sq.row, target_col))
                     if self.castling_legality_reason(state, m, piece) == MoveLegalityReason.LEGAL:
                         moves.append(m)
                 # Also add King-to-Rook moves for 960 notation
                 for r_sq, r_piece in state.board.items():
                      if isinstance(r_piece, Rook) and r_piece.color == piece.color:
                           is_kingside = r_sq.col > sq.col
                           target_col = 6 if is_kingside else 2
                           m_equiv = Move(sq, Square(sq.row, target_col))
                           if self.castling_legality_reason(state, m_equiv, piece) == MoveLegalityReason.LEGAL:
                                moves.append(Move(sq, r_sq))
        return moves
