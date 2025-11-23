from enum import Enum
from typing import Iterable

from chess.square import Square, Coordinate
from chess.board import Board


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP_LEFT = (-1, -1)
    UP_RIGHT = (1, -1)
    DOWN_LEFT = (-1, 1)
    DOWN_RIGHT = (1, 1)


class Moveset(Enum):
    STRAIGHT = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
    DIAGONAL = [
        Direction.UP_LEFT,
        Direction.UP_RIGHT,
        Direction.DOWN_LEFT,
        Direction.DOWN_RIGHT,
    ]
    STRAIGHT_AND_DIAGONAL = STRAIGHT + DIAGONAL


def get_line_from(square: Coordinate, direction: Direction):
    row_increment, col_increment = direction
    row = square.row + row_increment
    col = square.col + col_increment
    line = []

    while 0 <= row < 8 and 0 <= col < 8:
        line.append(Coordinate(row, col))
        row += row_increment
        col += col_increment

    return line


def get_move_from_input(board):
    from chess.move import Move

    while True:
        move_str = input("Enter a move (e.g. e2e4) or square to debug: ")
        try:
            start_square = board.get_square(move_str[:2])
            end_square = board.get_square(move_str[2:])
            break
        except ValueError:
            print("Invalid move")
    return Move(start_square, end_square)


def debug_square(square):
    print(f"{square=}")
    if square.piece is not None:
        print(f"{[str(square) for square in square.piece.moves]}")
        if isinstance(square.piece, Pawn):
            print(f"{square.piece.en_passant_square}")
