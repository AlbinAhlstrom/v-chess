from pieces import Piece


class StraightMovingPiece(Piece):
    def straight_moves(self):
        horizontal_moves = {Coordinate(self.position.row, col) for col in range(0, 8)}
        vertical_moves = {Coordinate(row, self.position.col) for row in range(0, 8)}
        moves = horizontal_moves | vertical_moves - {
            Coordinate(self.position.row, self.position.col)
        }
        return moves
