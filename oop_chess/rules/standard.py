from itertools import chain

from oop_chess.board import Board
from oop_chess.enums import Color, CastlingRight, Direction, MoveLegalityReason, BoardLegalityReason, GameOverReason
from oop_chess.move import Move
from oop_chess.piece import King, Pawn, Piece, Rook, Queen, Bishop, Knight
from oop_chess.square import Square
from oop_chess.game_state import GameState
from .core import Rules


class StandardRules(Rules):
    @property
    def name(self) -> str:
        return "Standard Chess"

    @property
    def fen_type(self) -> str:
        return "standard"

    @property
    def has_check(self) -> bool:
        return True

    def get_legal_moves(self) -> list[Move]:
        return [move for move in self.get_theoretical_moves() if self.validate_move(move) == MoveLegalityReason.LEGAL]

    def get_winner(self) -> Color | None:
        reason = self.get_game_over_reason()
        if reason == GameOverReason.CHECKMATE:
            return self.state.turn.opposite
        return None

    def is_check(self) -> bool:
        return self._is_color_in_check(self.state.board, self.state.turn)

    def get_game_over_reason(self) -> GameOverReason:
        # Use variant-specific GameOverReason class if available
        cls = getattr(self, "GameOverReason", GameOverReason)
        
        if self.state.repetition_count >= 3:
            return cls.REPETITION
        if self.is_fifty_moves:
            return cls.FIFTY_MOVE_RULE
        if not self.get_legal_moves():
            if self.is_check():
                return cls.CHECKMATE
            return cls.STALEMATE
        return cls.ONGOING

    def validate_move(self, move: Move) -> MoveLegalityReason:
        pseudo_reason = self.move_pseudo_legality_reason(move)
        if pseudo_reason != MoveLegalityReason.LEGAL:
            return pseudo_reason

        if self.king_left_in_check(move):
            return MoveLegalityReason.KING_LEFT_IN_CHECK

        return MoveLegalityReason.LEGAL

    def validate_board_state(self) -> BoardLegalityReason:
        white_kings = self.state.board.get_pieces(King, Color.WHITE)
        black_kings = self.state.board.get_pieces(King, Color.BLACK)
        white_pawns = self.state.board.get_pieces(Pawn, Color.WHITE)
        black_pawns = self.state.board.get_pieces(Pawn, Color.BLACK)
        white_non_pawns = [piece for piece in self.state.board.get_pieces(color=Color.WHITE) if not isinstance(piece, Pawn)]
        black_non_pawns = [piece for piece in self.state.board.get_pieces(color=Color.BLACK) if not isinstance(piece, Pawn)]
        white_piece_max = 16 - len(white_pawns)
        black_piece_max = 16 - len(black_pawns)

        pawns_on_backrank = []
        for sq, piece in self.state.board.board.items():
             if isinstance(piece, Pawn) and (sq.row == 0 or sq.row == 7):
                 pawns_on_backrank.append(piece)

        is_ep_square_valid = self.state.ep_square is None or self.state.ep_square.row in (2, 5)

        if len(white_kings) < 1:
            return BoardLegalityReason.NO_WHITE_KING
        if len(black_kings) < 1:
            return BoardLegalityReason.NO_BLACK_KING
        if len(white_kings + black_kings) > 2:
            return BoardLegalityReason.TOO_MANY_KINGS

        if len(white_pawns) > 8:
            return BoardLegalityReason.TOO_MANY_WHITE_PAWNS
        if len(black_pawns) > 8:
            return BoardLegalityReason.TOO_MANY_BLACK_PAWNS
        if pawns_on_backrank:
            return BoardLegalityReason.PAWNS_ON_BACKRANK

        if len(white_non_pawns) > white_piece_max:
            return BoardLegalityReason.TOO_MANY_WHITE_PIECES
        if len(black_non_pawns) > black_piece_max:
            return BoardLegalityReason.TOO_MANY_BLACK_PIECES

        if self.invalid_castling_rights():
            return BoardLegalityReason.INVALID_CASTLING_RIGHTS

        if not is_ep_square_valid:
            return BoardLegalityReason.INVALID_EP_SQUARE

        if self.inactive_player_in_check():
            return BoardLegalityReason.OPPOSITE_CHECK

        return BoardLegalityReason.VALID

    def king_left_in_check(self, move: Move) -> bool:
        """Returns True if king is left in check after a move."""
        next_state = self.apply_move(move)
        return next_state.rules.inactive_player_in_check()

    def apply_move(self, move: Move) -> GameState:
        """Returns a new GameState with the move applied."""
        new_board = self.state.board.copy()

        piece = new_board.get_piece(move.start)
        if piece is None:
            raise ValueError(f"No piece found at start coord: {move.start}.")

        target = new_board.get_piece(move.end)

        is_castling = isinstance(piece, King) and abs(move.start.col - move.end.col) == 2
        is_pawn_move = isinstance(piece, Pawn)
        is_en_passant = is_pawn_move and move.end == self.state.ep_square
        is_capture = target is not None or is_en_passant

        new_halfmove_clock = self.state.halfmove_clock + 1
        if is_pawn_move or is_capture:
            new_halfmove_clock = 0

        new_fullmove_count = self.state.fullmove_count
        if self.state.turn == Color.BLACK:
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

        new_castling_rights = set(self.state.castling_rights)

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

        if isinstance(target, Rook):
            revoke_rook_right(move.end)

        new_ep_square = None
        direction = Direction.DOWN if piece.color == Color.WHITE else Direction.UP
        if isinstance(piece, Pawn) and abs(move.start.row - move.end.row) > 1:
            new_ep_square = move.end.adjacent(direction)

        new_rules = self.__class__()
        new_state = GameState(
            board=new_board,
            turn=self.state.turn.opposite,
            castling_rights=tuple(sorted(new_castling_rights, key=lambda x: x.value)),
            ep_square=new_ep_square,
            halfmove_clock=new_halfmove_clock,
            fullmove_count=new_fullmove_count,
            rules=new_rules,
            repetition_count=1
        )
        new_rules.state = new_state
        return new_state

    def get_theoretical_moves(self) -> list[Move]:
        moves = []
        for sq, piece in self.state.board.board.items():
            if piece and piece.color == self.state.turn:
                # Basic moves from piece moveset
                for end in piece.theoretical_moves(sq):
                    moves.append(Move(sq, end))

                if isinstance(piece, Pawn):
                    # Double push
                    is_start_rank = (sq.row == 6 if piece.color == Color.WHITE else sq.row == 1)
                    if is_start_rank:
                        direction = piece.direction
                        one_step = sq.get_step(direction)
                        two_step = one_step.get_step(direction) if one_step else None
                        if two_step:
                            moves.append(Move(sq, two_step))

                    # Promotions
                    target_squares = []
                    if piece.color == Color.WHITE and sq.row == 1:
                        target_squares.append(sq.get_step(Direction.UP))
                        target_squares.extend([sq.get_step(Direction.UP_LEFT), sq.get_step(Direction.UP_RIGHT)])
                    elif piece.color == Color.BLACK and sq.row == 6:
                        target_squares.append(sq.get_step(Direction.DOWN))
                        target_squares.extend([sq.get_step(Direction.DOWN_LEFT), sq.get_step(Direction.DOWN_RIGHT)])

                    for target_sq in target_squares:
                        if target_sq and target_sq.is_promotion_row(piece.color):
                            for promo_piece_type in [Queen, Rook, Bishop, Knight]:
                                moves.append(Move(sq, target_sq, promo_piece_type(piece.color)))

                if isinstance(piece, King):
                    row = 7 if piece.color == Color.WHITE else 0
                    moves.append(Move(sq, Square(row, 6)))
                    moves.append(Move(sq, Square(row, 2)))
        return moves

    def move_pseudo_legality_reason(self, move: Move) -> MoveLegalityReason:
        """Determine if a move is pseudolegal."""
        piece = self.state.board.get_piece(move.start)
        target = self.state.board.get_piece(move.end)

        is_pawn_double_push = False
        is_pawn_double_push_valid = False
        if isinstance(piece, Pawn):
            is_start_rank = (move.start.row == 6 if piece.color == Color.WHITE else move.start.row == 1)
            direction = piece.direction
            one_step = move.start.get_step(direction)
            two_step = one_step.get_step(direction) if one_step else None
            if is_start_rank and move.end == two_step:
                is_pawn_double_push = True
                if self.state.board.get_piece(one_step) is None and self.state.board.get_piece(two_step) is None:
                     is_pawn_double_push_valid = True

        if piece is None:
            return MoveLegalityReason.NO_PIECE
        if piece.color != self.state.turn:
            return MoveLegalityReason.WRONG_COLOR
        if isinstance(piece, King) and abs(move.start.col - move.end.col) == 2:
            return self.castling_legality_reason(move, piece)
        if not (move.end in piece.theoretical_moves(move.start) or is_pawn_double_push):
            return MoveLegalityReason.NOT_IN_MOVESET

        if target and target.color == self.state.turn:
            return MoveLegalityReason.OWN_PIECE_CAPTURE

        if isinstance(piece, Pawn):
            if move.is_vertical and target is not None:
                return MoveLegalityReason.FORWARD_PAWN_CAPTURE

            if (
                move.is_diagonal
                and target is None
                and move.end != self.state.ep_square
            ):
                return MoveLegalityReason.PAWN_DIAGONAL_NON_CAPTURE
            if move.end.row == piece.promotion_row and not move.promotion_piece is not None:
                return MoveLegalityReason.NON_PROMOTION

        if move.end not in self.unblocked_paths(self.state.board, piece, piece.theoretical_move_paths(move.start)):
             if not is_pawn_double_push_valid:
                 return MoveLegalityReason.PATH_BLOCKED

        if move.promotion_piece:
            if not move.end.is_promotion_row(self.state.turn):
                return MoveLegalityReason.EARLY_PROMOTION

            if isinstance(move.promotion_piece, King):
                return MoveLegalityReason.KING_PROMOTION

        return MoveLegalityReason.LEGAL

    def castling_legality_reason(self, move: Move, piece: King) -> MoveLegalityReason:
        """Determine if a castling move is pseudolegal."""
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

        if required_right not in self.state.castling_rights:
            return MoveLegalityReason.NO_CASTLING_RIGHT

        rook_piece = self.state.board.get_piece(rook_start_square)
        if not (rook_piece and isinstance(rook_piece, Rook) and rook_piece.color == piece.color):
            raise AttributeError("No rook found on expected square")

        for sq in squares_to_check_occupancy:
            if self.state.board.get_piece(sq) is not None:
                return MoveLegalityReason.PATH_BLOCKED

        if self._is_color_in_check(self.state.board, piece.color):
            return MoveLegalityReason.CASTLING_FROM_CHECK

        for sq in squares_to_check_attack:
            if self.is_under_attack(self.state.board, sq, piece.color.opposite):
                return MoveLegalityReason.CASTLING_THROUGH_CHECK

        return MoveLegalityReason.LEGAL

    def is_attacking(self, board: Board, piece: Piece, square: Square, piece_square: Square) -> bool:
        if isinstance(piece, (Knight)):
            return square in piece.capture_squares(piece_square)
        else:
            return square in self.unblocked_paths(board, piece, piece.capture_paths(piece_square))

    def is_under_attack(self, board: Board, square: Square, by_color: Color) -> bool:
        """Check if square is attacked by the given color."""
        return board.bitboard.is_attacked(square.index, by_color)

    def inactive_player_in_check(self) -> bool:
        return self._is_color_in_check(self.state.board, self.state.turn.opposite)

    def invalid_castling_rights(self) -> list[CastlingRight]:
        invalid = []
        for right in self.state.castling_rights:
            king = self.state.board.get_piece(right.expected_king_square)
            rook = self.state.board.get_piece(right.expected_rook_square)
            if not (isinstance(king, King) and king.color == right.color):
                invalid.append(right)
                continue
            if not (isinstance(rook, Rook) and rook.color == right.color):
                invalid.append(right)
                continue
        return invalid

    def unblocked_path(self, board: Board, piece: Piece, path: list[Square]) -> list[Square]:
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
        """Return all unblocked squares in a piece's moveset"""
        return list(chain.from_iterable([self.unblocked_path(board, piece, path) for path in paths]))

    def _is_color_in_check(self, board: Board, color: Color) -> bool:
        """Check if the King of the given color is under attack."""
        king_sq = None
        for sq, piece in board.board.items():
            if isinstance(piece, King) and piece.color == color:
                king_sq = sq
                break

        if king_sq is None:
            return False

        return self.is_under_attack(board, king_sq, color.opposite)

    def get_legal_castling_moves(self) -> list[Move]:
        # Implementation of castling logic reuse
        moves = []
        for sq, piece in self.state.board.board.items():
            if isinstance(piece, King) and piece.color == self.state.turn:
                 # Check short
                 m_short = Move(sq, Square(sq.row, 6))
                 if self.castling_legality_reason(m_short, piece) == MoveLegalityReason.LEGAL:
                     moves.append(m_short)
                 # Check long
                 m_long = Move(sq, Square(sq.row, 2))
                 if self.castling_legality_reason(m_long, piece) == MoveLegalityReason.LEGAL:
                     moves.append(m_long)
        return moves

    def get_legal_en_passant_moves(self) -> list[Move]:
        if self.state.ep_square is None:
            return []
        moves = []
        for sq, piece in self.state.board.board.items():
             if isinstance(piece, Pawn) and piece.color == self.state.turn:
                 direction = piece.direction
                 if (
                     (sq.col == self.state.ep_square.col - 1 or sq.col == self.state.ep_square.col + 1)
                     and sq.row == self.state.ep_square.row - direction.value[1]
                 ):
                     move = Move(sq, self.state.ep_square)
                     if self.validate_move(move) == MoveLegalityReason.LEGAL:
                         moves.append(move)
        return moves

    def get_legal_promotion_moves(self) -> list[Move]:
        moves = []
        for sq, piece in self.state.board.board.items():
            if isinstance(piece, Pawn) and piece.color == self.state.turn:
                 direction = piece.direction
                 next_sq = sq.get_step(direction)
                 if next_sq and next_sq.is_promotion_row(piece.color):
                     for promo_type in [Queen, Rook, Bishop, Knight]:
                         move = Move(sq, next_sq, promo_type(piece.color))
                         if self.validate_move(move) == MoveLegalityReason.LEGAL:
                             moves.append(move)

                 for capture_dir in [Direction.UP_LEFT, Direction.UP_RIGHT] if piece.color == Color.WHITE else [Direction.DOWN_LEFT, Direction.DOWN_RIGHT]:
                     cap_sq = sq.get_step(capture_dir)
                     if cap_sq and cap_sq.is_promotion_row(piece.color):
                         target = self.state.board.get_piece(cap_sq)
                         if target and target.color != piece.color:
                             for promo_type in [Queen, Rook, Bishop, Knight]:
                                 move = Move(sq, cap_sq, promo_type(piece.color))
                                 if self.validate_move(move) == MoveLegalityReason.LEGAL:
                                     moves.append(move)
        return moves
