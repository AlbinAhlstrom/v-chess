from oop_chess.game import Game
from oop_chess.move import Move


def test_king_attacked_by_pawn_is_check():
    fen = "k7/8/8/8/8/8/1p6/K7 w - - 0 1"
    assert Game(fen=fen).is_check


def test_king_attacked_by_knight_is_check():
    fen = "k7/8/8/8/8/8/2n5/K7 w - - 0 1"
    assert Game(fen=fen).is_check


def test_king_attacked_by_rook_is_check():
    fen = "k7/8/8/8/8/8/2n5/K7 w - - 0 1"
    assert Game(fen=fen).is_check


def test_king_attacked_by_bishop_is_check():
    fen = "k6b/8/8/8/8/8/8/K7 w - - 0 1"
    assert Game(fen=fen).is_check


def test_king_attacked_by_queen_is_check():
    diagonal_fen = "k6q/8/8/8/8/8/8/K7 w - - 0 1"
    straight_fen = "k7/q7/8/8/8/8/8/K7 w - - 0 1"
    assert Game(fen=diagonal_fen).is_check
    assert Game(fen=straight_fen).is_check


def test_escape_by_capturing_attacker():
    fen = "k7/8/8/8/8/8/r6R/K7 w - - 0 1"
    game = Game(fen=fen)
    rook_captures_rook = Move.from_uci("h2a2")

    assert game.is_check
    assert game.is_move_legal(rook_captures_rook)


def test_escape_by_king_captures_attacker():
    fen = "k7/8/8/8/8/8/r7/K7 w - - 0 1"
    game = Game(fen=fen)
    king_captures_rook = Move.from_uci("a1a2")

    assert game.is_check
    assert game.is_move_legal(king_captures_rook)


def test_escape_by_moving_king_to_safe_square():
    fen = "k7/8/8/8/8/8/1p6/K7 w - - 0 1"
    game = Game(fen=fen)
    king_moves_in_front_of_pawn = Move.from_uci("a1b1")

    assert game.is_check
    assert game.is_move_legal(king_moves_in_front_of_pawn)


def test_escape_by_blocking_line_of_sight():
    fen = "k7/r7/8/8/8/8/7R/K7 w - - 0 1"
    game = Game(fen=fen)
    rook_blocks_rook = Move.from_uci("h2a2")

    assert game.is_check
    assert game.is_move_legal(rook_blocks_rook)
