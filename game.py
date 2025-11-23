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
        self.last_move: Move = None

    def switch_current_player(self):
        """Switch current player to the opponent."""
        self.current_player = self.current_player.opposite

    def add_to_history(self):
        self.history.append(self.board)

    def move_is_legal(self, move):
        """Determine if a move is legal.
        - Has to move a piece of the current players color
        - Movement has to correspond to the pieces capabilities
        - Capturing own pieces is not allowed
        - Path has to be clear (Doesn't apply for knights)
        - Pawn can only move diagonal if capturing or en passant
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

        return self.board.path_is_clear(move.start, move.end)

    def move_is_into_check(move: Move) -> bool:
        return False

    def render(self):
        """Print the board."""
        for row in range(8):
            pieces = [self.board.get_square((row, col)).piece or 0 for col in range(8)]
            print(pieces)

    def take_turn(self):
        move = self.get_move_from_input()
        if self.move_is_legal(move):
            self.make_move(move)
            self.last_move = move
            self.switch_current_player()
        else:
            print("Not a legal move")

    def make_move(self, move: Move):
        if move.is_double_pawn_push:
            square = Coordinate(move.start.row + move.piece.direction, move.start.col)
            self.board.en_passant_square = self.board.get_square(square)
        if move.target_piece or move.is_en_passant:
            move.target_piece.square.piece = None
        move.start.piece = None
        move.end.piece = move.piece
        move.piece.has_moved = True

    def undo_move(self, move: Move):
        if move.is_en_passant:
            move.end.piece = None
            original_location = Coordinate(move.start.row, move.end.col)
            capture_square = self.board.get_square(original_location)
            capture_square.piece = move.target_piece
        else:
            move.end.piece = move.target_piece
        move.start.piece = move.piece

        self.board = self.history.pop(-1)
        self.switch_current_player()

    @property
    def repetitions_of_position(self) -> int:
        return sum(1 for past in self.history if past.board == self.board)

    def get_move_from_string(self, move: str) -> Move:
        try:
            start_square = self.board.get_square(move[:2])
            end_square = self.board.get_square(move[2:])
        except ValueError:
            print("Move must consist of two valid squares without separation")

        piece = start_square.piece
        target_piece = end_square.piece
        move = Move(start_square, end_square, piece, target_piece)

        if move.is_en_passant:
            capture_square = Coordinate(start_square.row, end_square.col)
            target_piece = self.board.get_square(capture_square).piece
            move = Move(start_square, end_square, piece, target_piece)
        return move

    def get_move_from_input(self):
        while True:
            move_str = input("Enter a move (e.g. e2e4) or square to debug: ")
            return self.get_move_from_string(move_str)
