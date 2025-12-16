# Unit Test Checklist

This checklist tracks the implementation of missing unit and component tests to ensure robust coverage of the python chess logic.

## Organization
- [x] Create `tests/unit` directory.
- [x] Move existing unit tests (`test_square.py`, `test_piece.py`, etc.) to `tests/unit`.

## Board Component (`oop_chess/board.py`)
- [ ] **Basic Operations**: Test `set_piece`, `get_piece`, `remove_piece` for correctness.
- [ ] **Movement**: Test `move_piece` updates internal state correctly.
- [ ] **Copying**: Test `board.copy()` returns a deep copy (modifying copy doesn't affect original).
- [ ] **King Finding**: Test `find_king(color)` returns correct square or None if missing.
- [ ] **Pieces Retrieval**: Test `get_pieces(type, color)` returns correct list of pieces.

## GameState & FEN (`oop_chess/game_state.py`, `oop_chess/fen_helpers.py`)
- [ ] **FEN Parsing**: Test `GameState.from_fen()` with valid FEN strings (start, mid-game, complex).
- [ ] **FEN Serialization**: Test `state.fen` property produces valid FEN strings (round-trip test).
- [ ] **Edge Cases**:
    - [ ] Parsing FEN with no castling rights (`-`).
    - [ ] Parsing FEN with en-passant target.
    - [ ] Invalid FEN inputs (wrong number of fields, invalid characters).
- [ ] **Immutability**: Verify `GameState` is immutable (or treated as such).

## Move Component (`oop_chess/move.py`)
- [ ] **UCI Parsing**: Test `Move(uci_string)` for various valid/invalid inputs.
    - [ ] Normal moves (`e2e4`).
    - [ ] Promotion moves (`a7a8q`).
    - [ ] Invalid strings (wrong length, invalid coords).
- [ ] **Properties**:
    - [ ] `is_vertical`
    - [ ] `is_horizontal`
    - [ ] `is_diagonal`
- [ ] **Equality**: Test `__eq__` for Move objects.

## Piece Logic (`oop_chess/piece/*.py`)
- [ ] **Knight**: Verify exact `theoretical_moves` set for center vs corner placement (L-shape).
- [ ] **Bishop**: Verify diagonal paths (blocked and unblocked).
- [ ] **Rook**: Verify straight paths (blocked and unblocked).
- [ ] **Queen**: Verify star movement (blocked and unblocked).
- [ ] **King**: Verify 1-step moves in all directions.
- [ ] **Pawn**: (Already partially covered, but ensure):
    - [ ] Single push, double push (start rank).
    - [ ] Captures (diagonal).
    - [ ] En-passant square logic (if coupled with piece).

## Rules Logic (`oop_chess/rules.py`)
- [ ] **Castling Rights**: Test `apply_move` correctly updates/revokes castling rights:
    - [ ] King moves -> lose all rights.
    - [ ] Rook moves -> lose rights for that side.
    - [ ] Rook captured -> lose rights for that side.
- [ ] **En Passant**: Test `apply_move` sets `ep_square` correctly for double pawn push and clears it on next move.
- [ ] **Halfmove Clock**: Test reset on pawn move/capture, increment otherwise.
