from abc import ABC, abstractmethod

from oop_chess.board import Board
from oop_chess.enums import MoveLegalityReason, StatusReason, Color, CastlingRight, Direction
from oop_chess.move import Move
from oop_chess.piece import King, Pawn, Piece, Rook
from oop_chess.square import Square
from oop_chess.game_state import GameState


class Rules(ABC):
    @abstractmethod
    def get_legal_moves(self, state: GameState) -> list[Move]: ...

    @abstractmethod
    def is_check(self, state: GameState) -> bool: ...

    @abstractmethod
    def is_game_over(self, state: GameState) -> bool: ...

    @abstractmethod
    def apply_move(self, state: GameState, move: Move) -> GameState: ...

    @abstractmethod
    def is_board_state_legal(self, state: GameState) -> bool: ...

    @abstractmethod
    def board_state_legality_reason(self, state: GameState) -> StatusReason: ...


class StandardRules(Rules):
    def get_legal_moves(self, state: GameState) -> list[Move]:
        return [move for move in self.get_theoretical_moves(state) if self.is_move_legal(state, move)]

    def is_check(self, state: GameState) -> bool:
        return state.board.is_check(state.turn)

    def is_game_over(self, state: GameState) -> bool:
        return not bool(self.get_legal_moves(state))

    def is_checkmate(self, state: GameState) -> bool:
        return self.is_check(state) and self.is_game_over(state)

    def is_draw(self, state: GameState) -> bool:
        return self.is_game_over(state) and not self.is_check(state)

    def is_move_legal(self, state: GameState, move: Move) -> bool:
        return self.move_legality_reason(state, move) == "Move is legal"

    def move_legality_reason(self, state: GameState, move: Move) -> str:
        pseudo_reason = self.move_pseudo_legality_reason(state, move)
        if pseudo_reason != MoveLegalityReason.LEGAL:
            return pseudo_reason.value

        if self.king_left_in_check(state, move):
            return "King left in check"

        return "Move is legal"

    def king_left_in_check(self, state: GameState, move: Move) -> bool:
        """Returns True if king is left in check after a move."""
        next_state = self.apply_move(state, move)
        return self.inactive_player_in_check(next_state)

    def apply_move(self, state: GameState, move: Move) -> GameState:
        """Returns a new GameState with the move applied."""
        new_board = state.board.copy()

        piece = new_board.get_piece(move.start)
        if piece is None:
            raise ValueError(f"No piece found at start coord: {move.start}.")

        target = new_board.get_piece(move.end)

        is_castling = isinstance(piece, King) and abs(move.start.col - move.end.col) == 2
        is_pawn_move = isinstance(piece, Pawn)
        is_en_passant = is_pawn_move and move.end == state.ep_square
        is_capture = target is not None or is_en_passant

        new_halfmove_clock = state.halfmove_clock + 1
        if is_pawn_move or is_capture:
            new_halfmove_clock = 0

        new_fullmove_count = state.fullmove_count
        if state.turn == Color.BLACK:
            new_fullmove_count += 1

        new_board.move_piece(piece, move.start, move.end)

        if is_en_passant:
            direction = Direction.DOWN if piece.color == Color.WHITE else Direction.UP
            captured_coordinate = move.end.adjacent(direction)
            new_board.remove_piece(captured_coordinate)

        if is_castling:
            rook_col = 0 if move.end.col == 2 else 7
            rook_coord = Square(move.end.row, rook_col)
            rook = new_board.get_piece(rook_coord)
            if rook:
                direction = Direction.RIGHT if move.end.col == 2 else Direction.LEFT
                end_coord = move.end.adjacent(direction)
                new_board.move_piece(rook, rook_coord, end_coord)

        if move.promotion_piece is not None:
            new_board.set_piece(move.promotion_piece, move.end)

        new_castling_rights = set(state.castling_rights)

        def revoke_rights(color: Color):
            to_remove = [r for r in new_castling_rights if r.color == color]
            for r in to_remove: new_castling_rights.discard(r)

        def revoke_rook_right(square: Square):
            to_remove = [r for r in new_castling_rights if r.expected_rook_square == square]
            for r in to_remove: new_castling_rights.discard(r)

        if isinstance(piece, King):
            revoke_rights(piece.color)

        if isinstance(piece, Rook):
            revoke_rook_right(move.start)

        if isinstance(target, Rook):
            revoke_rook_right(move.end)

        new_ep_square = None
        direction = Direction.DOWN if piece.color == Color.WHITE else Direction.UP
        if isinstance(piece, Pawn) and abs(move.start.row - move.end.row) > 1:
            new_ep_square = move.end.adjacent(direction)

        return GameState(
            board=new_board,
            turn=state.turn.opposite,
            castling_rights=tuple(sorted(new_castling_rights, key=lambda x: x.value)),
            ep_square=new_ep_square,
            halfmove_clock=new_halfmove_clock,
            fullmove_count=new_fullmove_count
        )

    def get_theoretical_moves(self, state: GameState) -> list[Move]:
        moves = []
        for sq, piece in state.board.board.items():
            if piece and piece.color == state.turn:
                for end in piece.theoretical_moves(sq):
                    moves.append(Move(sq, end))


                if isinstance(piece, Pawn):
                     is_start_rank = (sq.row == 6 if piece.color == Color.WHITE else sq.row == 1)
                     if is_start_rank:
                         direction = piece.direction
                         one_step = sq.get_step(direction)
                         two_step = one_step.get_step(direction) if one_step else None
                         if two_step:
                             moves.append(Move(sq, two_step))


                if isinstance(piece, King):
                     row = 7 if piece.color == Color.WHITE else 0
                     moves.append(Move(sq, Square(row, 6)))
                     moves.append(Move(sq, Square(row, 2)))

        return moves
    def is_move_pseudo_legal(self, state: GameState, move: Move) -> bool:
        return self.move_pseudo_legality_reason(state, move) == MoveLegalityReason.LEGAL

    def move_pseudo_legality_reason(self, state: GameState, move: Move) -> MoveLegalityReason:
        """Determine if a move is pseudolegal."""
        piece = state.board.get_piece(move.start)
        target = state.board.get_piece(move.end)

        is_pawn_double_push = False
        is_pawn_double_push_valid = False
        if isinstance(piece, Pawn):
            is_start_rank = (move.start.row == 6 if piece.color == Color.WHITE else move.start.row == 1)
            direction = piece.direction
            one_step = move.start.get_step(direction)
            two_step = one_step.get_step(direction) if one_step else None
            if is_start_rank and move.end == two_step:
                is_pawn_double_push = True
                if state.board.get_piece(one_step) is None and state.board.get_piece(two_step) is None:
                     is_pawn_double_push_valid = True

        if piece is None:
            return MoveLegalityReason.NO_PIECE
        if piece.color != state.turn:
            return MoveLegalityReason.WRONG_COLOR
        if isinstance(piece, King) and abs(move.start.col - move.end.col) == 2:
            return self.castling_legality_reason(state, move, piece)
        if not (move.end in piece.theoretical_moves(move.start) or is_pawn_double_push):
            return MoveLegalityReason.NOT_IN_MOVESET

        if target and target.color == state.turn:
            return MoveLegalityReason.OWN_PIECE_CAPTURE

        if isinstance(piece, Pawn):
            if move.is_vertical and target is not None:
                return MoveLegalityReason.FORWARD_PAWN_CAPTURE

            if (
                move.is_diagonal
                and target is None
                and move.end != state.ep_square
            ):
                return MoveLegalityReason.PAWN_DIAGONAL_NON_CAPTURE
            if move.end.row == piece.promotion_row and not move.promotion_piece is not None:
                return MoveLegalityReason.NON_PROMOTION

        if move.end not in state.board.unblocked_paths(piece, piece.theoretical_move_paths(move.start)):
             if not is_pawn_double_push_valid:
                 return MoveLegalityReason.PATH_BLOCKED

        if move.promotion_piece:
            if not move.end.is_promotion_row(state.turn):
                return MoveLegalityReason.EARLY_PROMOTION

            if isinstance(move.promotion_piece, King):
                return MoveLegalityReason.KING_PROMOTION

        return MoveLegalityReason.LEGAL

    def _is_castling_pseudo_legal(self, state: GameState, move: Move, piece: King) -> bool:
        return self.castling_legality_reason(state, move, piece) == MoveLegalityReason.LEGAL

    def castling_legality_reason(self, state: GameState, move: Move, piece: King) -> MoveLegalityReason:
        """Determine if a castling move is pseudolegal."""
        required_right = None
        squares_to_check = []
        rook_start_square = None

        if piece.color == Color.WHITE:
            if move.end == Square(7, 6):
                required_right = CastlingRight.WHITE_SHORT
                squares_to_check = [Square(7, 5), Square(7, 6)]
                rook_start_square = Square(7, 7)
            else:
                required_right = CastlingRight.WHITE_LONG
                squares_to_check = [Square(7, 3), Square(7, 2)]
                rook_start_square = Square(7, 0)
        else:
            if move.end == Square(0, 6):
                required_right = CastlingRight.BLACK_SHORT
                squares_to_check = [Square(0, 5), Square(0, 6)]
                rook_start_square = Square(0, 7)
            else:
                required_right = CastlingRight.BLACK_LONG
                squares_to_check = [Square(0, 3), Square(0, 2)]
                rook_start_square = Square(0, 0)

        if required_right is None:
            return MoveLegalityReason.NO_CASTLING_RIGHT

        if required_right not in state.castling_rights:
            return MoveLegalityReason.NO_CASTLING_RIGHT

        rook_piece = state.board.get_piece(rook_start_square)
        if not (rook_piece and isinstance(rook_piece, Rook) and rook_piece.color == piece.color):
            raise AttributeError("No rook found on expected square")

        if state.board.is_check(piece.color):
            return MoveLegalityReason.CASTLING_FROM_CHECK

        for sq in squares_to_check:
            if state.board.is_under_attack(sq, piece.color.opposite):
                return MoveLegalityReason.CASTLING_THROUGH_CHECK

        return MoveLegalityReason.LEGAL

    def is_attacking(self, piece: Piece, square: Square, board: Board, piece_square: Square) -> bool:
        return board.is_attacking(piece, square, piece_square)

    def is_under_attack(self, board: Board, square: Square, by_color: Color) -> bool:
        """Check if square is attacked by the given color."""
        return board.is_under_attack(square, by_color)

    def player_in_check(self, board: Board, color: Color) -> bool:
        return board.is_check(color)

    def is_board_state_legal(self, state: GameState) -> bool:
        return self.board_state_legality_reason(state) == StatusReason.VALID

    def board_state_legality_reason(self, state: GameState) -> StatusReason:
        """Return status of the state."""
        white_kings = state.board.get_pieces(King, Color.WHITE)
        black_kings = state.board.get_pieces(King, Color.BLACK)
        white_pawns = state.board.get_pieces(Pawn, Color.WHITE)
        black_pawns = state.board.get_pieces(Pawn, Color.BLACK)
        white_non_pawns = [piece for piece in state.board.get_pieces(color=Color.WHITE) if not isinstance(piece, Pawn)]
        black_non_pawns = [piece for piece in state.board.get_pieces(color=Color.BLACK) if not isinstance(piece, Pawn)]
        white_piece_max = 16 - len(white_pawns)
        black_piece_max = 16 - len(black_pawns)

        pawns_on_backrank = []
        for sq, piece in state.board.board.items():
             if isinstance(piece, Pawn) and (sq.row == 0 or sq.row == 7):
                 pawns_on_backrank.append(piece)

        is_ep_square_valid = state.ep_square is None or state.ep_square.row in (2, 5)

        if len(white_kings) < 1:
            return StatusReason.NO_WHITE_KING
        if len(black_kings) < 1:
            return StatusReason.NO_BLACK_KING
        if len(white_kings + black_kings) > 2:
            return StatusReason.TOO_MANY_KINGS

        if len(white_pawns) > 8:
            return StatusReason.TOO_MANY_WHITE_PAWNS
        if len(black_pawns) > 8:
            return StatusReason.TOO_MANY_BLACK_PAWNS
        if pawns_on_backrank:
            return StatusReason.PAWNS_ON_BACKRANK

        if len(white_non_pawns) > white_piece_max:
            return StatusReason.TOO_MANY_WHITE_PIECES
        if len(black_non_pawns) > black_piece_max:
            return StatusReason.TOO_MANY_BLACK_PIECES

        if self.invalid_castling_rights(state):
            return StatusReason.INVALID_CASTLING_RIGHTS

        if not is_ep_square_valid:
            return StatusReason.INVALID_EP_SQUARE

        if self.inactive_player_in_check(state):
            return StatusReason.OPPOSITE_CHECK

        return StatusReason.VALID

    def inactive_player_in_check(self, state: GameState) -> bool:
        return state.board.is_check(state.turn.opposite)

    def invalid_castling_rights(self, state: GameState) -> list[CastlingRight]:
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

class AntichessRules(StandardRules):
    def move_legality_reason(self, state: GameState, move: Move) -> str:
        pseudo_reason = self.move_pseudo_legality_reason(state, move)
        if pseudo_reason != MoveLegalityReason.LEGAL:
            return pseudo_reason.value

        if self._is_capture(state, move):
            return "Move is legal"

        # If move is not a capture, ensure no captures are available
        for opt_move in self.get_theoretical_moves(state):
            if self.move_pseudo_legality_reason(state, opt_move) == MoveLegalityReason.LEGAL:
                if self._is_capture(state, opt_move):
                    return "Mandatory capture available."
        return "Move is legal"

    def _is_capture(self, state: GameState, move: Move) -> bool:
        if state.board.get_piece(move.end):
            return True
        piece = state.board.get_piece(move.start)
        if isinstance(piece, Pawn) and move.end == state.ep_square:
            return True
        return False

    def is_check(self, state: GameState) -> bool:
        return False

    def inactive_player_in_check(self, state: GameState) -> bool:
        return False

    def is_game_over(self, state: GameState) -> bool:
        if not state.board.get_pieces(color=state.turn):
            return True
        if not self.get_legal_moves(state):
            return True
        return False

    def is_checkmate(self, state: GameState) -> bool:
        return False

    def is_draw(self, state: GameState) -> bool:
        return False

    def king_left_in_check(self, state: GameState, move: Move) -> bool:
        return False

    def castling_legality_reason(self, state: GameState, move: Move, piece: King) -> MoveLegalityReason:
        return MoveLegalityReason.NO_CASTLING_RIGHT

    def status(self, state: GameState) -> StatusReason:
        white_pawns = state.board.get_pieces(Pawn, Color.WHITE)
        black_pawns = state.board.get_pieces(Pawn, Color.BLACK)
        pawns_on_backrank = []
        for sq, piece in state.board.board.items():
             if isinstance(piece, Pawn) and (sq.row == 0 or sq.row == 7):
                 pawns_on_backrank.append(piece)

        is_ep_square_valid = state.ep_square is None or state.ep_square.row in (2, 5)

        if len(white_pawns) > 8:
            return StatusReason.TOO_MANY_WHITE_PAWNS
        if len(black_pawns) > 8:
            return StatusReason.TOO_MANY_BLACK_PAWNS
        if pawns_on_backrank:
            return StatusReason.PAWNS_ON_BACKRANK
        
        if not is_ep_square_valid:
            return StatusReason.INVALID_EP_SQUARE

        return StatusReason.VALID

