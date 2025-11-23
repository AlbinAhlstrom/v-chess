from copy import deepcopy
from typing import Optional

from chess.board import Board
from chess.move import Move
from chess.piece.color import Color
from chess.square import Coordinate
from chess.piece.sliding_piece import SlidingPiece
from chess.piece.pawn import Pawn


class Game:
    """Represents a chess game.

    Responsible for turn management.
    The majority of the game logic is handled in the Board class.
    """

    def __init__(self, board: Optional[Board] = None):
        self.board = board or Board.starting_setup()
        self.current_player = Color.WHITE

        self.is_over = False
        self.winner = None
        self.history = []

    def switch_current_player(self):
        """Switch current player to the opponent."""
        self.current_player = self.current_player.opposite
        self.board.player_to_move = self.current_player

    def add_to_history(self):
        self.history.append(deepcopy(self.board))

    def move_is_legal(self, move, verbose=False):
        """Determine if a move is legal.
        - Has to move a piece of the current players color
        - Movement has to correspond to the pieces capabilities
        - Capturing own pieces is not allowed
        - Path has to be clear (Doesn't apply for knights)
        - Pawn can only move diagonal if capturing or en passant
        - Pawns can only make non-capturing moves forward
        - Can't move into check
        - Must unckeck oneself if in check
        TODO: - Castling is allowed
        """
        start = move.start
        end = move.end
        piece = move.start.piece
        target = move.end.piece

        if piece is None:
            if verbose:
                print("No piece")
            return False

        if piece.color != self.current_player:
            if verbose:
                print("Wrong piece color")
            return False

        if end.coordinate not in piece.moves:
            if verbose:
                print("Move not in piece moveset")
            return False

        if target and target.color == self.current_player:
            if verbose:
                print("Can't capture own piece")
            return False

        if (
            isinstance(piece, Pawn)
            and end.col != start.col
            and target is None
            and end != self.board.en_passant_square
        ):
            if verbose:
                print("Can only move pawn diagonal to capture")
            return False

        if isinstance(piece, Pawn) and move.is_capture and start.col == end.col:
            if verbose:
                print("Pawns can't capture forwards.")
            return False

        if not self.board.path_is_clear(move.start, move.end):
            if verbose:
                print("Path is blocked.")
            return False

        if self.king_left_in_check(move):
            if verbose:
                print("King left in check.")
            return False

        return True

    def get_all_legal_moves(self) -> list[Move]:
        legal_moves = []

        for piece in self.board.current_players_pieces:
            start_square = piece.square

            for end_coord in piece.moves:
                end_square = self.board.get_square(end_coord)

                candidate_move = self.board.get_move(start_square, end_square)

                if self.move_is_legal(candidate_move):
                    legal_moves.append(candidate_move)

        return legal_moves

    @property
    def is_checkmate(self) -> bool:
        if not self.board.current_player_in_check:
            return False

        return len(self.get_all_legal_moves()) == 0

    @property
    def is_draw(self) -> bool:
        if self.board.current_player_in_check:
            return False

        return len(self.get_all_legal_moves()) == 0

    def render(self):
        """Print the board."""
        for row in range(8):
            pieces = [self.board.get_square((row, col)).piece or 0 for col in range(8)]
            print(pieces)

    def king_left_in_check(self, move: Move) -> bool:
        self.add_to_history()
        self.execute_piece_movement(move)
        check = self.board.current_player_in_check
        self.undo_last_move()
        self.switch_current_player()
        return check

    def make_move(self, move: Move):
        """Make a move.

        Refetching board squares is necessary due to making a move
        and reverting another board object. Since move references the old
        board object new squares need to be fetched.
        """
        start_square = self.board.get_square(move.start.coordinate)
        end_square = self.board.get_square(move.end.coordinate)

        move = self.board.get_move(start_square, end_square)

        self.add_to_history()
        self.execute_piece_movement(move)
        self.switch_current_player()

    def execute_piece_movement(self, move: Move):
        if move.target_piece:
            move.target_piece.square.piece = None

        move.start.piece = None
        move.end.piece = move.piece
        move.piece.has_moved = True

        if move.is_double_pawn_push:
            en_passant_sq = self.board.get_square(move.piece.en_passant_square)
            self.board.en_passant_square = en_passant_sq

    def undo_last_move(self):
        """Revert to the previous board state."""
        if not self.history:
            raise ValueError("No moves to undo.")

        self.board = self.history.pop()
        self.switch_current_player()

    @property
    def repetitions_of_position(self) -> int:
        return sum(1 for past in self.history if past.board == self.board)
