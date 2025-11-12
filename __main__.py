from pieces import Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook, Pawn
from chess import Color, Coordinate, BoardState


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
