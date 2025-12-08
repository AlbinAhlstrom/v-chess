from copy import deepcopy

from chess.board import Board
from chess.move import Move
from chess.piece.king import King
from chess.piece.pawn import Pawn
from chess.enums import Color, CastlingRight
from chess.square import Square
from chess.exceptions import IllegalMoveException
from chess.piece.rook import Rook # Import Rook class


class Game:
    """Represents a chess game.

    Responsible for turn management.
    The majority of the game logic is handled in the Board class.
    """

    def __init__(self, board: Board):
        self.board = board
        self.history = []

    @property
    def is_over(self):
        return not bool(self.legal_moves)

    @property
    def is_checkmate(self):
        return self.is_over and self.board.current_player_in_check

    @property
    def is_draw(self):
         return self.is_over and not self.board.current_player_in_check

    def add_to_history(self):
        self.history.append(deepcopy(self.board))

    def is_move_pseudo_legal(self, move: Move) -> tuple[bool, str]:
        """Determine if a move is pseudolegal."""
        print(f"Game.is_move_pseudo_legal: Checking move {move}")
        piece = self.board.get_piece(move.start)
        target = self.board.get_piece(move.end)

        if piece is None:
            return False, "No piece moved."

        if piece.color != self.board.player_to_move:
            return False, "Wrong piece color."

        if isinstance(piece, King) and abs(move.start.col - move.end.col) == 2:
            print(f"Game.is_move_pseudo_legal: Potential castling move: {move}")
            return self._is_castling_pseudo_legal(move, piece)

        if move.end not in piece.theoretical_moves:
            return False, "Move not in piece moveset."

        if target and target.color == self.board.player_to_move:
            return False, "Can't capture own piece."

        if isinstance(piece, Pawn):
            if move.is_vertical and target is not None:
                return False, "Cant capture forwards with pawn."

            if (
                move.is_diagonal
                and target is None
                and move.end != self.board.en_passant_square
            ):
                return False, "Diagonal pawn move requires a capture."
            if move.end.row == piece.promotion_row and not move.is_promotion:
                return False, "Pawns must promote when reaching last row."

        if not self.board.unblocked_paths(piece):
            return False, "Path is blocked."

        if move.is_promotion:
            if not move.end.is_promotion_row(self.board.player_to_move):
                return False, "Can only promote on the last row."

            if isinstance(move.promotion_piece, King):
                return False, "Can't promote to king."

        return True, "Move is pseudo legal."

    def _is_castling_pseudo_legal(self, move: Move, piece: King) -> tuple[bool, str]:
        """Determine if a castling move is pseudolegal."""
        print(f"Game._is_castling_pseudo_legal: Checking castling for move {move}, piece {piece}")
        required_right = None
        squares_to_check = []
        rook_start_square = None # New variable to store rook's starting square

        if piece.color == Color.WHITE:
            if move.end == Square(0, 6):  # White Kingside (g1)
                required_right = CastlingRight.WHITE_SHORT
                squares_to_check = [Square(0, 5), Square(0, 6)]  # f1, g1
                rook_start_square = Square(0, 7) # h1
            elif move.end == Square(0, 2):  # White Queenside (c1)
                required_right = CastlingRight.WHITE_LONG
                squares_to_check = [Square(0, 3), Square(0, 2)]  # d1, c1
                rook_start_square = Square(0, 0) # a1
        else:  # Black King
            if move.end == Square(7, 6):  # Black Kingside (g8)
                required_right = CastlingRight.BLACK_SHORT
                squares_to_check = [Square(7, 5), Square(7, 6)]  # f8, g8
                rook_start_square = Square(7, 7) # h8
            elif move.end == Square(7, 2):  # Black Queenside (c8)
                required_right = CastlingRight.BLACK_LONG
                squares_to_check = [Square(7, 3), Square(7, 2)]  # d8, c8
                rook_start_square = Square(7, 0) # a8

        if required_right is None:
            return False, "Invalid castling move."

        if required_right not in self.board.castling_rights:
            return False, f"Castling right {required_right.value} not available."

        # Check for rook presence and type
        rook_piece = self.board.get_piece(rook_start_square)
        if not (rook_piece and isinstance(rook_piece, Rook) and rook_piece.color == piece.color):
            return False, f"Rook not present at {rook_start_square} or is not a {piece.color.name} Rook for castling."

        if self.board.player_in_check(piece.color):
            return False, "Cannot castle while in check."

        for sq in squares_to_check:
            if self.board.is_under_attack(sq, piece.color.opposite):
                return False, f"Cannot castle through or into attacked square {sq}."
        
        return True, ""

    @property
    def theoretical_moves(self):
        pieces = self.board.current_players_pieces
        if any([piece.square is None for piece in pieces]):
            raise AttributeError(f"Found piece without square")
        return [Move(piece.square, end) for piece in pieces for end in piece.theoretical_moves]


    @property
    def pseudo_legal_moves(self) -> list[Move]:
        return [move for move in self.theoretical_moves if self.is_move_pseudo_legal(move)[0]]

    @property
    def legal_moves(self) -> list[Move]:
        self.board.update_castling_rights()
        return [move for move in self.theoretical_moves if self.is_move_legal(move)[0]]

    def is_move_legal(self, move: Move) -> tuple[bool, str]:
        is_pseudo_legal, reason = self.is_move_pseudo_legal(move)
        if not is_pseudo_legal:
            return False, reason

        if self.king_left_in_check(move):
            return False, "King left in check"

        return True, "Move is legal"

    def render(self):
        """Print the board."""
        for row in range(8):
            pieces = [self.board.get_piece((row, col)) or 0 for col in range(8)]
            print(pieces)

    def king_left_in_check(self, move: Move) -> bool:
        """Returns True if king is left in check after a move."""
        initial_fen = self.board.fen
        real_board = self.board

        self.board = Board.from_fen(self.board.fen)
        self.board.make_move(move)

        # Turn has switched after making move
        is_check = self.board.inactive_player_in_check

        self.board = real_board
        assert self.board.fen == initial_fen
        return is_check

    def take_turn(self, move: Move):
        """Make a move.

        Refetching board squares is necessary due to making a move
        and reverting another board object. Since move references the old
        board object new squares need to be fetched.
        """
        print(f"Game.take_turn: Received move from frontend: {move}")
        piece = self.board.get_piece(move.start)
        if isinstance(piece, Pawn) and move.is_diagonal and self.board.get_piece(move.end) is None and move.end == self.board.en_passant_square:
            move = Move(move.start, move.end, is_en_passant=True)

        is_legal, reason = self.is_move_legal(move)
        print(f"Game.take_turn: is_move_legal for {move}: {is_legal}, Reason: {reason}")
        if not is_legal:
            raise IllegalMoveException(reason)

        self.add_to_history()
        self.board.make_move(move)
        self.board.update_castling_rights()
        self.board.increment_turn_counters(move)

    def undo_last_move(self) -> str:
        """Revert to the previous board state."""
        if not self.history:
            raise ValueError("No moves to undo.")

        self.board = self.history.pop()
        self.board.switch_active_player()
        return self.board.fen

    @property
    def repetitions_of_position(self) -> int:
        return sum(1 for past in self.history if past.board == self.board)
