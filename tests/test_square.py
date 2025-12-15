from hypothesis import given
from oop_chess.square import Square
from conftest import random_row_col, random_square, random_square_str


@given(row=random_row_col, col=random_row_col)
def test_square_from_row_col_is_valid(row: int, col: int):
    """Checks that creating a Square with valid indices (0-7) does not raise an error."""
    try:
        Square(row, col)
    except ValueError:
        assert False, f"Square({row}, {col}) raised ValueError unexpectedly."


@given(square=random_square())
def test_square_to_str_round_trip(square: Square):
    """
    Checks that converting a Square to its algebraic notation and back
    results in the original row and column.
    """

    notation = str(square)
    back_to_square = Square(notation)
    assert back_to_square == square


@given(notation=random_square_str())
def test_square_from_str_round_trip(notation: str):
    """
    Checks that converting from algebraic notation to a Square and back
    results in the original notation.
    """

    square = Square(notation)
    back_to_notation = str(square)
    assert back_to_notation == notation.lower()
