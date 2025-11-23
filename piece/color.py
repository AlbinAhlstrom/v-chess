from enum import Enum


class Color(Enum):
    """Representation of piece/player color.

    Attributes:
        BLACK: Represents black pieces/player.
        WHITE: Represents white pieces/player.
    """

    BLACK = 0
    WHITE = 1

    @property
    def opposite(self):
        return Color.BLACK if self == Color.WHITE else Color.WHITE

    def __eq__(self, other) -> bool:
        return isinstance(other, Color) and self.value == other.value
