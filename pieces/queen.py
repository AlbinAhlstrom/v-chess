from board import Color
from pieces.movement import StraightMovingPiece


class Queen(StraightMovingPiece):
    def __str__(self):
        match self.color:
            case Color.WHITE:
                return "♕"
            case Color.BLACK:
                return "♛"

    def moves():
        pass

    @property
    def value(self):
        return 9
