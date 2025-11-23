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

    def add_to_history(self):
        self.history.append(deepcopy(self.board))

    def move_is_legal(self, move):
        """Determine if a move is legal.
        - Has to move a piece of the current players color
        - Movement has to correspond to the pieces capabilities
        - Capturing own pieces is not allowed
        - Path has to be clear (Doesn't apply for knights)
        - Pawn can only move diagonal if capturing or en passant
        - Pawn can only move two squares on first move
        TODO: *Current* - Can't move into check
        TODO: - Must unckeck oneself if in check
        TODO: - Castling is allowed
        """
        start = move.start
        end = move.end
        piece = move.start.piece
        target = move.end.piece

        if piece is None:
            print("No piece")
            return False

        if piece.color != self.current_player:
            print("Wrong piece color")
            return False

        if end.coordinate not in piece.moves:
            print("Move not in piece moveset")
            return False

        if target and target.color == self.current_player:
            print("Can't capture own piece")
            return False

        if (
            isinstance(piece, Pawn)
            and end.col != start.col
            and target is None
            and end != self.board.en_passant_square
        ):
            print("Can only move pawn diagonal to capture")
            return False
        if isinstance(piece, Pawn) and abs(end.col - start.col) > 1 and piece.has_moved:
            print("Pawns can only move two squares of first move")

        return self.board.path_is_clear(move.start, move.end)

    def move_is_into_check(move: Move) -> bool:
        return False

    def render(self):
        """Print the board."""
        for row in range(8):
            pieces = [self.board.get_square((row, col)).piece or 0 for col in range(8)]
            print(pieces)

    def make_move(self, move: Move):
        self.execute_piece_movement(move)
        self.switch_current_player()

    def execute_piece_movement(self, move: Move):
        if move.target_piece or move.is_en_passant:
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
