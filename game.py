from typing import Optional

from chess.board import Board
from chess.move import Move
from chess.piece.color import Color
from chess.piece.sliding_piece import SlidingPiece
from chess.piece.pawn import Pawn
from chess.move_utils import get_move_from_input


class Game:
    """Represents a chess game.

    Responsible for turn management.
    The majority of the game logic is handled in the Board class.
    """

    def __init__(self, board: Optional[Board] = None):
        self.board = board or Board.starting_setup()

        self.player_white = Color.WHITE
        self.player_black = Color.BLACK

        self.current_player = self.player_white

        self.is_over = False
        self.winner = None
        self.move_history = []

    def switch_turn(self):
        """Switch current player to the opponent."""
        self.current_player = (
            self.player_black
            if self.current_player == self.player_white
            else self.player_white
        )

    def move_is_legal(self, move):
        """Determine if a move is legal.
        - Has to move a piece of the current players color
        - Movement has to correspond to the pieces capabilities
        - Capturing own pieces is not allowed
        - Path has to be clear (Doesn't apply for knights)
        TODO: - Pawn can only move diagonal if capturing or en passant
        TODO: - Can't move into check
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

        print(f"{end=}")
        print(f"{self.board.en_passant_square=}")
        if (
            isinstance(piece, Pawn)
            and end.col != start.col
            and target is None
            and end != self.board.en_passant_square
        ):
            print("Can only move pawn diagonal to capture")
            return False

        return self.board.path_is_clear(move.start, move.end)

    def render(self):
        """Print the board."""
        for row in range(8):
            pieces = [self.board.get_square((row, col)).piece or 0 for col in range(8)]
            print(pieces)

    def take_turn(self):
        self.board.history.append(self.board.copy())
        move = get_move_from_input(board)
        if self.move_is_legal(move):
            self.board.make_move(move)
            print(f"{move.is_double_pawn_push=}")
            if move.is_double_pawn_push:
                self.board.en_passant_square = move.end.piece.en_passant_square
            self.switch_turn()
        else:
            print("Not a legal move")
