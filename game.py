from typing import Optional

from chess.board import Board
from chess.move import Move
from chess.piece.color import Color
from chess.piece.sliding_piece import SlidingPiece


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

    def switch_turn(self):
        """Switch current player to the opponent."""
        self.current_player = (
            self.player_black
            if self.current_player == self.player_white
            else self.player_white
        )

    def move_is_legal(self, move):
        """Determine if a move is legal.
        - Checking if piece belongs to current player
        - Valid movement patterns
        TODO: Checks for check
        TODO: Castling/en passant rules
        """
        if not move.start.is_occupied:
            print("No piece")
            return False

        if move.start.piece.color != self.current_player:
            print("Wrong piece color")
            return False

        if move.end.piece and move.end.piece.color == self.current_player:
            print("Can't capture own piece")
            return False

        return self.board.path_is_clear(move.start, move.end)

    def render(self):
        """Print the board."""
        for row in range(8):
            pieces = [self.board.get_square((row, col)).piece or 0 for col in range(8)]
            print(pieces)

    def take_turn(self):
        move_str = input("Enter a move: ")
        start_square = self.board.get_square(move_str[:2])
        end_square = self.board.get_square(move_str[2:])
        move = Move(start_square, end_square)
        if self.move_is_legal(move):
            self.board.make_move(move)
            self.switch_turn()
        else:
            print("Not a legal move")

    def debug_move(self):
        start_square = self.board.get_square(input("Enter a square: "))

        for square in start_square.piece.moves:
            print(str(square))
        self.switch_turn()
