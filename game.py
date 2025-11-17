from typing import Optional

from chess.board import Board


class Game:
    """Represents a chess game.

    Responsible for turn management.
    The majority of the game logic is handled in the Board class.
    """

    def __init__(
        self, board: Optional[Board] = None, player_white=None, player_black=None
    ):
        self.board = board or Board.starting_setup()

        self.player_white = player_white
        self.player_black = player_black

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
        - Checking if piece belongs to current player
        - Valid movement patterns
        - Checks for check
        - Castling/en passant rules
        """
        pass

    def render(self):
        """Print the board."""
        for row in range(8):
            pieces = [self.board.get_square((row, col)).piece or 0 for col in range(8)]
            print(pieces)
