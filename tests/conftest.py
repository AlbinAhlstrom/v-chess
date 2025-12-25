from hypothesis import strategies as st
import pytest
from fastapi.testclient import TestClient
from backend.main import app

from v_chess.square import Square
from v_chess.enums import Color
from v_chess.piece.piece import Piece
from v_chess.piece import piece_from_char
from typing import Type


random_row_col = st.integers(min_value=0, max_value=7)
piece_types: list[Type[Piece]] = list(set(piece_from_char.values()))
random_color = st.sampled_from(Color)
random_piece_cls = st.sampled_from(piece_types)


@st.composite
def random_square(draw):
    return draw(st.builds(Square, random_row_col, random_row_col))


@st.composite
def random_piece(draw):
    piece_cls = draw(random_piece_cls)
    color = draw(random_color)
    return piece_cls(color)


@st.composite
def random_square_str(draw):
    file_char = draw(st.sampled_from("abcdefgh"))
    rank_char = draw(st.sampled_from("12345678"))
    return file_char + rank_char

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
