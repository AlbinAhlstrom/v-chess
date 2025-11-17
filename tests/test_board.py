import pytest

from chess.square import Square
from chess.board import Board
from chess.piece.color import Color


def test_coordinate_str_and_repr():
    c = Square(0, 0)
    assert str(c) == "a8"
    assert repr(c) == "Square(0, 0)"
    assert hash(c) == hash((0, 0))


@pytest.mark.parametrize("row,col", [(-1, 0), (8, 0), (0, -1), (0, 8)])
def test_invalid_coordinate_raises(row, col):
    with pytest.raises(ValueError):
        Square(row, col)


def test_color_enum_values():
    assert Color.WHITE.value == 1
    assert Color.BLACK.value == 0


def test_boardstate_initialization_and_repetition():
    board = [[None for _ in range(8)] for _ in range(8)]
    history = [board.copy()]
    state = Board(
        board=board,
        history=history,
        player_to_move=Color.WHITE,
        castling_allowed=[Color.WHITE, Color.BLACK],
        en_passant_square=None,
        halfmove_clock=0,
    )

    assert state.board == board
    assert state.player_to_move == Color.WHITE
    assert state.repetitions_of_position == 1
