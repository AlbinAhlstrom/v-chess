from chess import Coordinate
from pieces import Piece


def straight_moves(piece: Piece):
    p = piece.position

    horizontal_moves = {Coordinate(p.row, col) for col in range(0, 8)}
    vertical_moves = {Coordinate(row, p.col) for row in range(0, 8)}

    return (horizontal_moves | vertical_moves) - {Coordinate(p.row, p.col)}


def diagonal_moves(piece: Piece):
    p = piece.position

    cols = [p.col + i for i in range(-7, 8) if 0 <= p.col + i < 8]
    rows = [p.row + i for i in range(-7, 8) if 0 <= p.row + i < 8]
    inv_rows = [p.row - i for i in range(-7, 8) if 0 <= p.row - i < 8]

    diag = {Coordinate(row, col) for row, col in zip(rows, cols)}
    inv_diag = {Coordinate(row, col) for row, col in zip(inv_rows, cols)}

    return (diag | inv_diag) - {Coordinate(p.row, p.col)}
