from typing import Optional

from chess.board import Board
from chess.move import Move
from chess.piece.color import Color


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

    def is_move_legal(self, move):
        """Determine if a move is legal.
        X- Checking if piece belongs to current player
        - Valid movement patterns
        - Checks for check
        - Castling/en passant rules
        """
        if move.start.piece.color != self.current_player:
            return False
        return True

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
        if not self.is_move_legal(move):
            raise Exception("Not a legal move")
        self.board.make_move(move)
        self.switch_turn()

    def debug_move(self):
        start_square = self.board.get_square(input("Enter a square: "))

        for square in start_square.piece.moves:
            print(str(square))
        self.switch_turn()
