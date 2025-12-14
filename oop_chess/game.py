from copy import deepcopy
from typing import Optional
from dataclasses import replace

from oop_chess.board import Board
from oop_chess.game_state import GameState
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
    """

    def __init__(self, fen: str | Board | None = None, board: Optional[Board] = None, state: Optional[GameState] = None):
        if isinstance(fen, Board):
            board = fen
            fen = None
        
        if state:
            self.state = state
        elif fen:
            self.state = GameState.from_fen(fen)
        elif board:
            # Legacy support: assume standard start rights/turn
            self.state = replace(GameState.starting_setup(), board=board)
        else:
            self.state = GameState.starting_setup()
            
        self.history: list[GameState] = []
        self.move_history: list[str] = []

    @property
    def board(self) -> Board:
        return self.state.board

    @property
    def is_over(self):
        return not bool(self.legal_moves)

    @property
    def is_checkmate(self):
        # Checkmate: In Check AND No Legal Moves
        return self.is_check and self.is_over

    @property
    def is_check(self):
        # Check if current player is in check
        return self.board.is_check(self.state.turn)

    @property
    def is_draw(self):
         return self.is_over and not self.is_check

    def add_to_history(self):
        self.history.append(self.state)

    def is_move_pseudo_legal(self, move: Move) -> tuple[bool, str]:
        """Determine if a move is pseudolegal."""
        piece = self.board.get_piece(move.start)
        target = self.board.get_piece(move.end)

        if piece is None:
            return False, "No piece moved."

        if piece.color != self.state.turn:
            return False, "Wrong piece color."

        if isinstance(piece, King) and abs(move.start.col - move.end.col) == 2:
            return self._is_castling_pseudo_legal(move, piece)

        if move.end not in piece.theoretical_moves(move.start):
            # Special check for Pawn double push
            is_pawn_double_push = False
            if isinstance(piece, Pawn):
                is_start_rank = (move.start.row == 6 if piece.color == Color.WHITE else move.start.row == 1)
                direction = piece.direction
                one_step = move.start.get_step(direction)
                two_step = one_step.get_step(direction) if one_step else None
                if is_start_rank and move.end == two_step:
                    is_pawn_double_push = True
            
            if not is_pawn_double_push:
                return False, "Move not in piece moveset."

        if target and target.color == self.state.turn:
            return False, "Can't capture own piece."

        if isinstance(piece, Pawn):
            if move.is_vertical and target is not None:
                return False, "Cant capture forwards with pawn."

            if (
                move.is_diagonal
                and target is None
                and move.end != self.state.ep_square
            ):
                return False, "Diagonal pawn move requires a capture."
            if move.end.row == piece.promotion_row and not move.promotion_piece is not None:
                return False, "Pawns must promote when reaching last row."

        if move.end not in self.board.unblocked_paths(piece, piece.theoretical_move_paths(move.start)):
             # Re-check Pawn Double Push blockage
            is_pawn_double_push = False
            if isinstance(piece, Pawn):
                 is_start_rank = (move.start.row == 6 if piece.color == Color.WHITE else move.start.row == 1)
                 direction = piece.direction
                 one_step = move.start.get_step(direction)
                 two_step = one_step.get_step(direction) if one_step else None
                 if is_start_rank and move.end == two_step:
                     if self.board.get_piece(one_step) is None and self.board.get_piece(two_step) is None:
                         is_pawn_double_push = True
            
            if not is_pawn_double_push:
                return False, "Path is blocked."

        if move.promotion_piece:
            if not move.end.is_promotion_row(self.state.turn):
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

        if required_right not in self.state.castling_rights:
            return False, f"Castling right {required_right.value} not available."

        rook_piece = self.board.get_piece(rook_start_square)
        if not (rook_piece and isinstance(rook_piece, Rook) and rook_piece.color == piece.color):
            return False, f"Rook not present at {rook_start_square} or is not a {piece.color.name} Rook for castling."

        if self.board.is_check(piece.color):
            return False, "Cannot castle while in check."

        for sq in squares_to_check:
            if self.board.is_under_attack(sq, piece.color.opposite):
                return False, f"Cannot castle through or into attacked square {sq}."

        return True, ""

    @property
    def theoretical_moves(self):
        moves = []
        for sq, piece in self.board.board.items():
            if piece and piece.color == self.state.turn:
                for end in piece.theoretical_moves(sq):
                    moves.append(Move(sq, end))
                
                # Add Pawn Double Push
                if isinstance(piece, Pawn):
                     is_start_rank = (sq.row == 6 if piece.color == Color.WHITE else sq.row == 1)
                     if is_start_rank:
                         direction = piece.direction
                         one_step = sq.get_step(direction)
                         two_step = one_step.get_step(direction) if one_step else None
                         if two_step:
                             moves.append(Move(sq, two_step))

                # Add Castling
                if isinstance(piece, King):
                     row = 7 if piece.color == Color.WHITE else 0
                     moves.append(Move(sq, Square(row, 6))) # Short
                     moves.append(Move(sq, Square(row, 2))) # Long

        return moves


    @property
    def pseudo_legal_moves(self) -> list[Move]:
        return [move for move in self.theoretical_moves if self.is_move_pseudo_legal(move)[0]]

    @property
    def legal_moves(self) -> list[Move]:
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
        self.board.print()

    def king_left_in_check(self, move: Move) -> bool:
        """Returns True if king is left in check after a move."""
        # Use GameState application
        next_state = self.state.apply_move(move)
        # Note: apply_move switches turn. 
        # So we check if the player who MOVED (now opponent) is in check?
        # No, 'inactive_player_in_check' checks 'state.turn.opposite'.
        # In next_state, turn is Opponent. Opposite is Mover.
        # So inactive_player_in_check checks Mover.
        return next_state.inactive_player_in_check

    def take_turn(self, move: Move):
        """Make a move by finding the corresponding legal move."""
        if not self.state.is_legal:
            raise IllegalBoardException(f"Board state is illegal. Reason: {self.state.status}")
        
        reason = self.move_legality_reason(move)
        if reason != "Move is legal":
            raise IllegalMoveException(f"Illegal move: {reason}")

        san = move.get_san(self)

        self.add_to_history()
        self.state = self.state.apply_move(move)

        if self.is_checkmate:
            san += "#"
        elif self.is_check:
            san += "+"
        
        self.move_history.append(san)

    def undo_move(self) -> str:
        """Revert to the previous board state."""
        if not self.history:
            raise ValueError("No moves to undo.")

        self.state = self.history.pop()
        if self.move_history:
            self.move_history.pop()
        print(f"Undo move. Restored FEN: {self.state.fen}")
        return self.state.fen

    @property
    def repetitions_of_position(self) -> int:
        # Repetition based on FEN (or parts of it)
        # Assuming FEN captures necessary state
        current_fen_key = " ".join(self.state.fen.split()[:4]) # placement, turn, rights, ep
        count = 1
        for past_state in self.history:
            past_fen_key = " ".join(past_state.fen.split()[:4])
            if past_fen_key == current_fen_key:
                count += 1
        return count
