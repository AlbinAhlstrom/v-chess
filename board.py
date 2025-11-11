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
        halfmove_clock
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


def main():
    def setup_starting_board():
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        board = [[None for _ in range(8)] for _ in range(8)]

        board[1] = [Pawn(Color.BLACK, Coordinate(1, col)) for col in range(8)]
        board[6] = [Pawn(Color.WHITE, Coordinate(6, col)) for col in range(8)]

        board[0] = [
            piece(Color.BLACK, Coordinate(0, col))
            for col, piece in enumerate(piece_order)
        ]
        board[7] = [
            piece(Color.WHITE, Coordinate(7, col))
            for col, piece in enumerate(piece_order)
        ]

        return board

    board = setup_starting_board()
    history = [board]
    player_to_move = Color.WHITE
    castle_allowed = [Color.WHITE, Color.BLACK]
    en_passant_square = None
    halfmove_clock = 0

    state = BoardState(
        board,
        history,
        player_to_move,
        castle_allowed,
        en_passant_square,
        halfmove_clock,
    )
    for row in state.board:
        row = [char or 0 for char in row]
        print(row)


if __name__ == "__main__":
    main()
