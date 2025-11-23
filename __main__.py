from chess.piece.rook import Rook
from chess.piece.knight import Knight
from chess.piece.bishop import Bishop
from chess.piece.queen import Queen
from chess.piece.king import King
from chess.piece.pawn import Pawn
from chess.piece.color import Color
from chess.board import Board
from chess.game import Game
from chess.move import Move
from chess.square import Square, Coordinate


def get_square_from_string(square: str, board: Board) -> tuple[Square]:
    try:
        return board.get_square(square)
    except ValueError:
        print(f"{square} is not a valid square.")


def execute_action(action: str, game):
    match action:
        case "u":
            game.undo_last_move()
        case _:
            if len(action) != 4:
                print("Move must consist of two valid squares without separation.")
            start = game.board.get_square(action[:2])
            end = game.board.get_square(action[2:])
            move = game.board.get_move(start, end)
            print(f"{move.__dict__=}")

            if game.move_is_legal(move):
                game.add_to_history()
                game.make_move(move)
            else:
                print("Please make a legal move.")


def main():
    """Set up and print the initial chess board.

    This function initializes an 8x8 chess board with all pieces in their
    standard starting positions. It prints the board layout using unicode
    characters for pieces and 0 for empty squares.

    printed output:
        [♜, ♞, ♝, ♛, ♚, ♝, ♞, ♜]
        [♟, ♟, ♟, ♟, ♟, ♟, ♟, ♟]
        [0, 0, 0, 0, 0, 0, 0, 0]
        [0, 0, 0, 0, 0, 0, 0, 0]
        [0, 0, 0, 0, 0, 0, 0, 0]
        [0, 0, 0, 0, 0, 0, 0, 0]
        [♙, ♙, ♙, ♙, ♙, ♙, ♙, ♙]
        [♖, ♘, ♗, ♕, ♔, ♗, ♘, ♖]
    """

    game = Game()
    while True:
        game.render()
        print()
        print(f"Current players king in check={game.board.current_player_in_check}")
        print("Valid actions: ")
        print("Move - 'e2e4'")
        print("Undo - u")
        print(f"{str(game.board.en_passant_square)=}")
        action = input("Enter a move: ")
        execute_action(action, game)


if __name__ == "__main__":
    main()
