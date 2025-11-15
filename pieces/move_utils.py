from typing import Iterable

from chess.square import Square
from pieces import Piece


def straight_moves(piece: Piece):
    pos = piece.position

    horizontal_moves = [Square(pos.row, col) for col in range(0, 8)]
    vertical_moves = [Square(row, pos.col) for row in range(0, 8)]

    return (horizontal_moves | vertical_moves) - {Square(pos.row, pos.col)}


def diagonal_moves(piece: Piece):
    pos = piece.position

    diagonal = {
        Square(pos.row + offset, pos.col + offset)
        for offset in range(-7, 8)
        if 0 <= pos.row + offset < 8 and 0 <= pos.col + offset < 8
    }
    inverted_diagonal = {
        Square(pos.row + offset, pos.col - offset)
        for offset in range(-7, 8)
        if 0 <= pos.row + offset < 8 and 0 <= pos.col - offset < 8
    }
    return (diagonal | inverted_diagonal) - {Square(pos.row, pos.col)}


def limit_distance(piece: Piece, moves: Iterable[Square], limit: int) -> set[Square]:
    return {
        move
        for move in moves
        if abs(piece.position.row - move.row) <= limit
        and abs(piece.position.col - move.col) <= limit
    }
