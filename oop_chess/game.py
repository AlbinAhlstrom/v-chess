from copy import deepcopy

from oop_chess.board import Board
from oop_chess.move import Move
from oop_chess.piece.king import King
from oop_chess.piece.pawn import Pawn
from oop_chess.enums import Color, CastlingRight
from oop_chess.square import Square
from oop_chess.exceptions import IllegalMoveException, IllegalBoardException
from oop_chess.piece.rook import Rook


class Game:
    """Represents a chess game.

    Responsible for turn management.
    The majority of the game logic is handled in the Board class.
    """

    def __init__(self, board: Board):
        self.board = board
        self.history = []

    @property
    def is_over(self):
        return not bool(self.legal_moves)

    @property
    def is_checkmate(self):
        return self.is_over and self.board.current_player_in_check

    @property
    def is_check(self):
        return self.board.current_player_in_check

    @property
    def is_draw(self):
         return self.is_over and not self.board.current_player_in_check

    def add_to_history(self):
        self.history.append(deepcopy(self.board))

    def is_move_pseudo_legal(self, move: Move) -> tuple[bool, str]:
        """Determine if a move is pseudolegal."""
        piece = self.board.get_piece(move.start)
        target = self.board.get_piece(move.end)

        if piece is None:
            return False, "No piece moved."

        if piece.color != self.board.player_to_move:
            return False, "Wrong piece color."

        if isinstance(piece, King) and abs(move.start.col - move.end.col) == 2:
            return self._is_castling_pseudo_legal(move, piece)

        if move.end not in piece.theoretical_moves:
            return False, "Move not in piece moveset."

        if target and target.color == self.board.player_to_move:
            return False, "Can't capture own piece."

        if isinstance(piece, Pawn):
            if move.is_vertical and target is not None:
                return False, "Cant capture forwards with pawn."

            if (
                move.is_diagonal
                and target is None
                and move.end != self.board.ep_square
            ):
                return False, "Diagonal pawn move requires a capture."
            if move.end.row == piece.promotion_row and not move.promotion_piece is not None:
                return False, "Pawns must promote when reaching last row."

        if not isinstance(piece, Pawn):
            if move.end not in self.board.unblocked_paths(piece):
                return False, "Path is blocked."

        if move.promotion_piece:
            if not move.end.is_promotion_row(self.board.player_to_move):
                return False, "Can only promote on the last row."

            if isinstance(move.promotion_piece, King):
                return False, "Can't promote to king."

        return True, "Move is pseudo legal."

    def _is_castling_pseudo_legal(self, move: Move, piece: King) -> tuple[bool, str]:
        """Determine if a castling move is pseudolegal."""
        required_right = None
        squares_to_check = []
        rook_start_square = None

        if piece.color == Color.WHITE:
            if move.end == Square(7, 6):
                required_right = CastlingRight.WHITE_SHORT
                squares_to_check = [Square(7, 5), Square(7, 6)]
                rook_start_square = Square(7, 7)
            else:
                required_right = CastlingRight.WHITE_LONG
                squares_to_check = [Square(7, 3), Square(7, 2)]
                rook_start_square = Square(7, 0)
        else:
            if move.end == Square(0, 6):
                required_right = CastlingRight.BLACK_SHORT
                squares_to_check = [Square(0, 5), Square(0, 6)]
                rook_start_square = Square(0, 7)
            else:
                required_right = CastlingRight.BLACK_LONG
                squares_to_check = [Square(0, 3), Square(0, 2)]
                rook_start_square = Square(0, 0)

        if required_right is None:
            return False, "Invalid castling move."

        if required_right not in self.board.castling_rights:
            return False, f"Castling right {required_right.value} not available."

        rook_piece = self.board.get_piece(rook_start_square)
        if not (rook_piece and isinstance(rook_piece, Rook) and rook_piece.color == piece.color):
            return False, f"Rook not present at {rook_start_square} or is not a {piece.color.name} Rook for castling."

        if self.board.player_in_check(piece.color):
            return False, "Cannot castle while in check."

        for sq in squares_to_check:
            if self.board.is_under_attack(sq, piece.color.opposite):
                return False, f"Cannot castle through or into attacked square {sq}."

        return True, ""

    @property
    def theoretical_moves(self):
        moves = []
        pieces = self.board.current_players_pieces
        if any([piece.square is None for piece in pieces]):
            raise AttributeError("Found piece without square")

        for piece in pieces:
            for end in piece.theoretical_moves:
                moves.append(Move(piece.square, end))
        return moves


    @property
    def pseudo_legal_moves(self) -> list[Move]:
        return [move for move in self.theoretical_moves if self.is_move_pseudo_legal(move)[0]]

    @property
    def legal_moves(self) -> list[Move]:
        self.board.update_castling_rights()
        return [move for move in self.theoretical_moves if self.is_move_legal(move)]

    def is_move_legal(self, move: Move) -> bool:
        return self.move_legality_reason(move) == "Move is legal"

    def move_legality_reason(self, move: Move) -> str:
        is_pseudo_legal, reason = self.is_move_pseudo_legal(move)
        if not is_pseudo_legal:
            return reason

        if self.king_left_in_check(move):
            return "King left in check"

        return "Move is legal"

    def render(self):
        """Print the board."""
        for row in range(8):
            pieces = [self.board.get_piece((row, col)) or 0 for col in range(8)]
            print(pieces)

    def king_left_in_check(self, move: Move) -> bool:
        """Returns True if king is left in check after a move."""
        initial_fen = self.board.fen
        real_board = self.board

        self.board = Board.from_fen(self.board.fen)
        self.board.make_move(move)

        is_check = self.board.inactive_player_in_check

        self.board = real_board
        assert self.board.fen == initial_fen
        return is_check

    def take_turn(self, move: Move):
        """Make a move by finding the corresponding legal move."""
        if not self.board.is_legal:
            raise IllegalBoardException(f"Board state is illegal. Reason: {self.board.status}")
        
        reason = self.move_legality_reason(move)
        if reason != "Move is legal":
            raise IllegalMoveException(f"Illegal move: {reason}")

        self.add_to_history()
        self.board.make_move(move)
        self.board.update_castling_rights()

    def undo_move(self) -> str:
        """Revert to the previous board state."""
        if not self.history:
            raise ValueError("No moves to undo.")

        self.board = self.history.pop()
        print(f"Undo move. Restored FEN: {self.board.fen}")
        return self.board.fen

    @property
    def repetitions_of_position(self) -> int:
        return sum(1 for past in self.history if past.board == self.board)
