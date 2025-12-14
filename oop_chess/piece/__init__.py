from typing import Type
from .piece import *
from .rook import Rook
from .knight import Knight
from .bishop import Bishop
from .queen import Queen
from .king import King
from .pawn import Pawn


piece_from_char: dict[str, Type[Piece]] = {
    "R": Rook,
    "r": Rook,
    "N": Knight,
    "n": Knight,
    "B": Bishop,
    "b": Bishop,
    "Q": Queen,
    "q": Queen,
    "K": King,
    "k": King,
    "P": Pawn,
    "p": Pawn,
}
