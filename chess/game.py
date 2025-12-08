from copy import deepcopy

from chess.board import Board
from chess.move import Move
from chess.piece.king import King
from chess.piece.pawn import Pawn
from chess.enums import Color


class IllegalMoveException(Exception): ...


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
        piece = self.board.get_piece(move.start)
        target = self.board.get_piece(move.end)

        if piece is None:
            return False, "No piece moved."

        if piece.color != self.board.player_to_move:
            return False, "Wrong piece color."

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
        piece = self.board.get_piece(move.start)
        if isinstance(piece, Pawn) and move.is_diagonal and self.board.get_piece(move.end) is None and move.end == self.board.en_passant_square:
            move = Move(move.start, move.end, is_en_passant=True)

        is_legal, reason = self.is_move_legal(move)
        if not is_legal:
            raise IllegalMoveException(reason)

        self.add_to_history()
        self.board.make_move(move)
        self.increment_turn_counters(move)

    def increment_turn_counters(self, move: Move):
        if self.board.is_pawn_move(move) or self.board.is_capture(move):
            self.board.halfmove_clock = 0
        else:
            self.board.halfmove_clock += 1

        if self.board.player_to_move == Color.WHITE:
            self.board.fullmove_count += 1

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

