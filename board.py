class Board:
    """Represents the current state of a chessboard.

    Tracks the board layout, move history, player turn, castling rights,
    en passant square, and halfmove clock.
    """

    def __init__(
        self,
        board: list[list[Piece | None]],
        history: list[Board],
        player_to_move: Color,
        castling_allowed: list[Color],
        en_passant_square: Coordinate | None,
        halfmove_clock: int,
    ):
        """
        Args:
            board: 8x8 board matrix containing either Piece or None.
            history: Past board states.
            player_to_move: Piece color of the player whose turn it is.
            castling_allowed: Colors of players still allowed to castle.
            en_passant_square: Target square for en passant.
            halfmove_clock: Counter for 50-move rule.
        """
        self.board = board
        self.history = history
        self.player_to_move = player_to_move
        self.castling_allowed = castling_allowed
        self.en_passant_square = en_passant_square
        self.halfmove_clock = halfmove_clock

    @classmethod
    def starting_setup(cls) -> Board:
        """Return a list of lists representing the starting chess board.

        Returns:
            8x8 board with pieces in standard starting positions.
        """
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        board = [[None for _ in range(8)] for _ in range(8)]

        board[1] = [Pawn(Color.BLACK, Coordinate(1, col)) for col in range(8)]
        board[6] = [Pawn(Color.WHITE, Coordinate(6, col)) for col in range(8)]

        board[0] = [
            piece(Color.BLACK, Coordinate(0, col))
            for col, piece in enumerate(piece_order)
        ]
        board[7] = [
            piece(Color.WHITE, Coordinate(7, col))
            for col, piece in enumerate(piece_order)
        ]

        return cls(
            board=board,
            history=[board.copy()],
            player_to_move=Color.WHITE,
            castling_allowed=[Color.WHITE, Color.BLACK],
            en_passant_square=None,
            halfmove_clock=0,
        )

    @property
    def repetitions_of_position(self) -> int:
        """Count how many times the current board state has occurred.

        Used to track draw by threefold repetition.

        Returns:
            Number of repetitions of the current board position.
        """
        return sum(1 for past in self.history if past == self.board)
