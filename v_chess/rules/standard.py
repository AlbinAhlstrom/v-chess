from typing import List, Callable, Optional
from itertools import chain

from v_chess.board import Board
from v_chess.enums import Color, CastlingRight, Direction, MoveLegalityReason, BoardLegalityReason, GameOverReason
from v_chess.move import Move
from v_chess.piece import King, Pawn, Piece, Rook, Queen, Bishop, Knight
from v_chess.square import Square
from v_chess.game_state import GameState
from v_chess.game_over_conditions import (
    evaluate_repetition, evaluate_fifty_move_rule, 
    evaluate_checkmate, evaluate_stalemate
)
from v_chess.move_validators import (
    validate_piece_presence, validate_turn, 
    validate_moveset, validate_friendly_capture, validate_pawn_capture, 
    validate_path, validate_promotion, validate_standard_castling, 
    validate_king_safety
)
from v_chess.state_validators import (
    standard_king_count, pawn_on_backrank,
    pawn_count_standard, piece_count_promotion_consistency, castling_rights_consistency,
    en_passant_target_validity, inactive_player_check_safety
)
from .core import Rules


class StandardRules(Rules):
    @property
    def starting_fen(self) -> str:
        from v_chess.game_state import GameState
        return GameState.STARTING_FEN

    @property
    def game_over_conditions(self) -> List[Callable[[GameState, Rules], Optional[GameOverReason]]]:
        """Returns a list of conditions that can end the game."""
        return [
            evaluate_repetition,
            evaluate_fifty_move_rule,
            evaluate_checkmate,
            evaluate_stalemate
        ]

    @property
    def move_validators(self) -> List[Callable[[GameState, Move, Rules], Optional[MoveLegalityReason]]]:
        """Returns a list of move validators."""
        return [
            validate_piece_presence,
            validate_turn,
            validate_moveset,
            validate_friendly_capture,
            validate_pawn_capture,
            validate_path,
            validate_promotion,
            validate_standard_castling,
            validate_king_safety
        ]

    @property
    def state_validators(self) -> List[Callable[[GameState, Rules], Optional[BoardLegalityReason]]]:
        """Returns a list of board state validators."""
        return [
            standard_king_count,
            pawn_on_backrank,
            pawn_count_standard,
            piece_count_promotion_consistency,
            castling_rights_consistency,
            en_passant_target_validity,
            inactive_player_check_safety
        ]

    def get_winner(self, state: GameState) -> Color | None:
        """Determines the winner of the game."""
        reason = self.get_game_over_reason(state)
        if reason == GameOverReason.CHECKMATE:
            return state.turn.opposite
        return None

    def is_check(self, state: GameState) -> bool:
        """Checks if the current player is in check."""
        return self._is_color_in_check(state.board, state.turn)

    def king_left_in_check(self, state: GameState, move: Move) -> bool:
        """Checks if the king is left in check after a move."""
        return state.board.bitboard.is_king_attacked_after_move(move, state.turn, state.board, state.ep_square)

    def castling_legality_reason(self, state: GameState, move: Move, piece: King) -> MoveLegalityReason:
        """Determines if a castling move is pseudo-legal."""
        required_right = None
        squares_to_check_attack = []
        squares_to_check_occupancy = []
        rook_start_square = None

        if piece.color == Color.WHITE:
            if move.end == Square(7, 6):
                required_right = CastlingRight.WHITE_SHORT
                squares_to_check_attack = [Square(7, 5), Square(7, 6)]
                squares_to_check_occupancy = [Square(7, 5), Square(7, 6)]
                rook_start_square = Square(7, 7)
            else:
                required_right = CastlingRight.WHITE_LONG
                squares_to_check_attack = [Square(7, 3), Square(7, 2)]
                squares_to_check_occupancy = [Square(7, 3), Square(7, 2), Square(7, 1)]
                rook_start_square = Square(7, 0)
        else:
            if move.end == Square(0, 6):
                required_right = CastlingRight.BLACK_SHORT
                squares_to_check_attack = [Square(0, 5), Square(0, 6)]
                squares_to_check_occupancy = [Square(0, 5), Square(0, 6)]
                rook_start_square = Square(0, 7)
            else:
                required_right = CastlingRight.BLACK_LONG
                squares_to_check_attack = [Square(0, 3), Square(0, 2)]
                squares_to_check_occupancy = [Square(0, 3), Square(0, 2), Square(0, 1)]
                rook_start_square = Square(0, 0)

        if required_right is None:
            return MoveLegalityReason.NO_CASTLING_RIGHT

        if required_right not in state.castling_rights:
            return MoveLegalityReason.NO_CASTLING_RIGHT

        rook_piece = state.board.get_piece(rook_start_square)
        if not (rook_piece and isinstance(rook_piece, Rook) and rook_piece.color == piece.color):
            return MoveLegalityReason.NO_CASTLING_RIGHT

        for sq in squares_to_check_occupancy:
            if state.board.get_piece(sq) is not None:
                return MoveLegalityReason.PATH_BLOCKED

        if self._is_color_in_check(state.board, piece.color):
            return MoveLegalityReason.CASTLING_FROM_CHECK

        for sq in squares_to_check_attack:
            if self.is_under_attack(state.board, sq, piece.color.opposite):
                return MoveLegalityReason.CASTLING_THROUGH_CHECK

        return MoveLegalityReason.LEGAL

    def get_theoretical_moves(self, state: GameState):
        """Generates all moves possible on an empty board for the current turn."""
        bb = state.board.bitboard
        turn = state.turn

        for p_type, mask in bb.pieces[turn].items():
            temp_mask = mask
            while temp_mask:
                sq_idx = (temp_mask & -temp_mask).bit_length() - 1
                sq = Square(divmod(sq_idx, 8))
                piece = state.board.get_piece(sq)

                if piece:
                    # Basic moves and promotions
                    for end in piece.theoretical_moves(sq):
                        if isinstance(piece, Pawn) and end.is_promotion_row(turn):
                            for promo_piece_type in [Queen, Rook, Bishop, Knight]:
                                yield Move(sq, end, promo_piece_type(turn))
                        else:
                            yield Move(sq, end)

                    if isinstance(piece, Pawn):
                        # Double push
                        is_start_rank = (sq.row == 6 if turn == Color.WHITE else sq.row == 1)
                        if is_start_rank:
                            direction = piece.direction
                            one_step = sq.get_step(direction)
                            two_step = one_step.get_step(direction) if one_step and not one_step.is_none_square else None
                            if two_step and not two_step.is_none_square:
                                yield Move(sq, two_step)

                    if isinstance(piece, King):
                        row = 7 if turn == Color.WHITE else 0
                        if sq == Square(row, 4):
                            yield Move(sq, Square(row, 6))
                            yield Move(sq, Square(row, 2))

                temp_mask &= temp_mask - 1
        
        # Add variant-specific moves (e.g. drops)
        yield from self.get_extra_theoretical_moves(state)

    def get_extra_theoretical_moves(self, state: GameState) -> list[Move]:
        return []

    def is_attacking(self, board: Board, piece: Piece, square: Square, piece_square: Square) -> bool:
        """Checks if a piece at a specific square is attacking another square."""
        if isinstance(piece, (Knight)):
            return square in piece.capture_squares(piece_square)
        else:
            return square in self.unblocked_paths(board, piece, piece.capture_paths(piece_square))

    def is_under_attack(self, board: Board, square: Square, by_color: Color) -> bool:
        """Checks if a square is attacked by pieces of the given color."""
        return board.bitboard.is_attacked(square.index, by_color)

    def inactive_player_in_check(self, state: GameState) -> bool:
        """Checks if the player who just moved is in check."""
        return self._is_color_in_check(state.board, state.turn.opposite)

    def invalid_castling_rights(self, state: GameState) -> list[CastlingRight]:
        """Returns a list of castling rights that are no longer valid due to piece positions."""
        invalid = []
        for right in state.castling_rights:
            king = state.board.get_piece(right.expected_king_square)
            rook = state.board.get_piece(right.expected_rook_square)
            if not (isinstance(king, King) and king.color == right.color):
                invalid.append(right)
                continue
            if not (isinstance(rook, Rook) and rook.color == right.color):
                invalid.append(right)
                continue
        return invalid

    def unblocked_path(self, board: Board, piece: Piece, path: list[Square]) -> list[Square]:
        """Returns the squares in a path that are not blocked by other pieces."""
        try:
            stop_index = next(
                i for i, coord in enumerate(path) if board.get_piece(coord) is not None
            )
        except StopIteration:
            return path

        target_piece = board.get_piece(path[stop_index])

        if target_piece and target_piece.color != piece.color:
            return path[: stop_index + 1]
        else:
            return path[:stop_index]

    def unblocked_paths(self, board: Board, piece: Piece, paths: list[list[Square]]) -> list[Square]:
        """Returns all reachable squares across multiple paths."""
        return list(chain.from_iterable([self.unblocked_path(board, piece, path) for path in paths]))

    def _is_color_in_check(self, board: Board, color: Color) -> bool:
        """Checks if the king of the given color is under attack."""
        king_mask = board.bitboard.pieces[color][King]
        while king_mask:
            sq_idx = (king_mask & -king_mask).bit_length() - 1
            if board.bitboard.is_attacked(sq_idx, color.opposite):
                return True
            king_mask &= king_mask - 1
        return False

    def get_legal_castling_moves(self, state: GameState) -> list[Move]:
        """Returns all legal castling moves."""
        moves = []
        for sq, piece in state.board.items():
            if isinstance(piece, King) and piece.color == state.turn:
                 # Check short
                 m_short = Move(sq, Square(sq.row, 6))
                 if self.validate_move(state, m_short) == MoveLegalityReason.LEGAL:
                     moves.append(m_short)
                 # Check long
                 m_long = Move(sq, Square(sq.row, 2))
                 if self.validate_move(state, m_long) == MoveLegalityReason.LEGAL:
                     moves.append(m_long)
        return moves

    def get_legal_en_passant_moves(self, state: GameState) -> list[Move]:
        """Returns all legal en passant moves."""
        if state.ep_square is None:
            return []
        moves = []
        for sq, piece in state.board.items():
             if isinstance(piece, Pawn) and piece.color == state.turn:
                 direction = piece.direction
                 if (
                     (sq.col == state.ep_square.col - 1 or sq.col == state.ep_square.col + 1)
                     and sq.row == state.ep_square.row - direction.value[1]
                 ):
                     move = Move(sq, state.ep_square)
                     if self.validate_move(state, move) == MoveLegalityReason.LEGAL:
                         moves.append(move)
        return moves

    def get_legal_promotion_moves(self, state: GameState) -> list[Move]:
        """Returns all legal pawn promotion moves."""
        moves = []
        for sq, piece in state.board.items():
            if isinstance(piece, Pawn) and piece.color == state.turn:
                 direction = piece.direction
                 next_sq = sq.get_step(direction)
                 if next_sq and next_sq.is_promotion_row(piece.color):
                     for promo_type in [Queen, Rook, Bishop, Knight]:
                         move = Move(sq, next_sq, promo_type(piece.color))
                         if self.validate_move(state, move) == MoveLegalityReason.LEGAL:
                             moves.append(move)

                 for capture_dir in [Direction.UP_LEFT, Direction.UP_RIGHT] if piece.color == Color.WHITE else [Direction.DOWN_LEFT, Direction.DOWN_RIGHT]:
                     cap_sq = sq.get_step(capture_dir)
                     if cap_sq and cap_sq.is_promotion_row(piece.color):
                         target = state.board.get_piece(cap_sq)
                         if target and target.color != piece.color:
                             for promo_type in [Queen, Rook, Bishop, Knight]:
                                 move = Move(sq, cap_sq, promo_type(piece.color))
                                 if self.validate_move(state, move) == MoveLegalityReason.LEGAL:
                                     moves.append(move)
        return moves

    def apply_move(self, state: GameState, move: Move) -> GameState:
        """Executes a move and returns the new GameState."""
        
        if move.is_drop:
             new_board = state.board.copy()
             new_board.set_piece(move.drop_piece, move.end)
             
             new_halfmove_clock = state.halfmove_clock + 1
             new_fullmove_count = state.fullmove_count + (1 if state.turn == Color.BLACK else 0)
             
             new_state = GameState(
                board=new_board,
                turn=state.turn.opposite,
                castling_rights=state.castling_rights,
                ep_square=None,
                halfmove_clock=new_halfmove_clock,
                fullmove_count=new_fullmove_count,
                repetition_count=1
             )
             
             return self.post_move_actions(state, move, new_state)

        new_board = state.board.copy()
        piece = new_board.get_piece(move.start)
        target = new_board.get_piece(move.end)

        # Castling Detection (Generalized for 960)
        is_castling = False
        rook_sq = None
        if isinstance(piece, King):
            # Standard/960 Target: King moves > 1 square OR to C/G file
            if abs(move.start.col - move.end.col) > 1:
                is_castling = True
            # 960 KxR Capture: Target is own Rook
            elif isinstance(target, Rook) and target.color == piece.color:
                is_castling = True
                rook_sq = move.end

        is_pawn_move = isinstance(piece, Pawn)
        is_en_passant = is_pawn_move and move.end == state.ep_square
        is_capture = target is not None or is_en_passant

        new_halfmove_clock = state.halfmove_clock + 1
        if is_pawn_move or is_capture:
            new_halfmove_clock = 0

        new_fullmove_count = state.fullmove_count
        if state.turn == Color.BLACK:
            new_fullmove_count += 1

        if is_castling:
            # Determine Castling Right involved
            if rook_sq: # Known from KxR
                # Find right matching this rook
                right = next((r for r in state.castling_rights if r.expected_rook_square == rook_sq and r.color == piece.color), None)
            else:
                # Infer from direction
                is_kingside = move.end.col > move.start.col
                # For 960, we might need more robust matching if multiple rooks on same side (rare)
                # Standard assumption: King moves towards the rook.
                # In 960 standard notation (target c/g), g is kingside, c is queenside.
                if move.end.col == 6: # g-file (Kingside)
                     right = next((r for r in state.castling_rights if r.color == piece.color and r.expected_rook_square.col > move.start.col), None)
                elif move.end.col == 2: # c-file (Queenside)
                     right = next((r for r in state.castling_rights if r.color == piece.color and r.expected_rook_square.col < move.start.col), None)
                else:
                     # Non-standard target (manual 960 move?), fall back to direction
                     if is_kingside:
                         right = next((r for r in state.castling_rights if r.color == piece.color and r.expected_rook_square.col > move.start.col), None)
                     else:
                         right = next((r for r in state.castling_rights if r.color == piece.color and r.expected_rook_square.col < move.start.col), None)

            if right:
                rook_sq = right.expected_rook_square
                rook = new_board.get_piece(rook_sq)
                
                # Destination Squares (Fixed for Chess)
                rank = move.start.row
                king_dest = Square(rank, 6) # g-file
                rook_dest = Square(rank, 5) # f-file
                if right.expected_rook_square.col < move.start.col: # Queenside
                    king_dest = Square(rank, 2) # c-file
                    rook_dest = Square(rank, 3) # d-file
                
                # Execute Castling
                # Remove both first to avoid self-collision in 960
                new_board.remove_piece(move.start)
                new_board.remove_piece(rook_sq)
                new_board.set_piece(piece, king_dest)
                new_board.set_piece(rook, rook_dest)
            else:
                # Fallback (shouldn't happen if validated)
                new_board.move_piece(piece, move.start, move.end)

        else:
            new_board.move_piece(piece, move.start, move.end)

        if is_en_passant:
            direction = Direction.DOWN if piece.color == Color.WHITE else Direction.UP
            captured_coordinate = move.end.adjacent(direction)
            new_board.remove_piece(captured_coordinate)

        if move.promotion_piece is not None:
            new_board.set_piece(move.promotion_piece, move.end)

        new_castling_rights = set(state.castling_rights)

        def revoke_rights(color: Color):
            to_remove = [r for r in new_castling_rights if r != CastlingRight.NONE and r.color == color]
            for r in to_remove: new_castling_rights.discard(r)

        def revoke_rook_right(square: Square):
            to_remove = [r for r in new_castling_rights if r != CastlingRight.NONE and r.expected_rook_square == square]
            for r in to_remove: new_castling_rights.discard(r)

        if isinstance(piece, King):
            revoke_rights(piece.color)

        if isinstance(piece, Rook):
            revoke_rook_right(move.start)

        # If rook was captured (or involved in castling? No, castling rights revoked by King move)
        # But if we capture a rook, we must revoke *that* rook's right.
        # In castling KxR, target IS rook.
        if isinstance(target, Rook):
            revoke_rook_right(move.end)
        
        # Explicit check for 960 KxR castling target revocation if not caught above
        if is_castling and rook_sq:
             revoke_rook_right(rook_sq)

        new_ep_square = None
        direction = Direction.DOWN if piece.color == Color.WHITE else Direction.UP
        if isinstance(piece, Pawn) and abs(move.start.row - move.end.row) > 1:
            new_ep_square = move.end.adjacent(direction)

        # Basic state transition
        new_state = GameState(
            board=new_board,
            turn=state.turn.opposite,
            castling_rights=tuple(sorted(new_castling_rights, key=lambda x: x.value)),
            ep_square=new_ep_square,
            halfmove_clock=new_halfmove_clock,
            fullmove_count=new_fullmove_count,
            repetition_count=1
        )
        
        # Apply variant hooks
        return self.post_move_actions(state, move, new_state)