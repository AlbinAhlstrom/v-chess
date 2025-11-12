from chess import Coordinate
from pieces import Piece


class StraightMovingPiece(Piece):
    def moves(self):
        p = self.position

        horizontal_moves = {Coordinate(p.row, col) for col in range(0, 8)}
        vertical_moves = {Coordinate(row, p.col) for row in range(0, 8)}

        return (horizontal_moves | vertical_moves) - {Coordinate(p.row, p.col)}


class DiagonalMovingPiece(Piece):
    def moves(self):
        p = self.position

        cols = [col := p.col + i for i in range(-7, 8) if 0 <= col < 8]
        rows = [row := p.row + i for i in range(-7, 8) if 0 <= row < 8]
        inv_rows = [row := p.row - i for i in range(-7, 8) if 0 <= row < 8]

        diag = {Coordinate(row, col) for row, col in zip(rows, cols)}
        inv_diag = {Coordinate(row, col) for row, col in zip(inv_rows, cols)}

        return (diag | inv_diag) - {Coordinate(p.row, p.col)}
