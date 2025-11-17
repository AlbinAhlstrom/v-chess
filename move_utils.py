from enum import Enum
from typing import Iterable

from chess.square import Square, Coordinate


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
