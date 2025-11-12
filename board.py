from enum import Enum


class Color(Enum):
    BLACK = 0
    WHITE = 1


class Coordinate:
    def __init__(self, row: int, col: int):
        if not 0 <= row < 8:
            raise ValueError(f"Invalid row {row}")
        if not 0 <= col < 8:
            raise ValueError(f"Invalid col {col}")

        self.row = row
        self.col = col

    def __eq__(self, other):
        return (
            isinstance(other, Coordinate)
            and self.row == other.row
            and self.col == other.col
        )

    def __repr__(self):
        return f"Coordinate({self.row}, {self.col})"

    def __hash__(self):
        return hash((self.row, self.col))

    def __str__(self):
        return f"{chr(self.col + ord('a'))}{8 - self.row}"


class BoardState:
    def __init__(
        self,
        board,
        history,
        player_to_move,
        castle_allowed,
        en_passant_square,
        halfmove_clock,
    ):
        self.board = board
        self.history = history
        self.player_to_move = player_to_move
        self.castle_allowed = castle_allowed
        self.en_passant_square = en_passant_square
        self.halfmove_clock = halfmove_clock

    @property
    def repetitions_of_position(self):
        return sum(1 for past in self.history if past == self.board)
