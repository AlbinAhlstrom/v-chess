from chess.board import Board
from chess.game import Game
from chess.move import Move


def main():
    board = Board.starting_setup()
    game = Game(board)

    while True:
        board.print()

        if game.is_over:
            message = "Checkmate!" if game.is_checkmate else "Draw!"
            print(message)
            break

        print(f"Player to move: {board.player_to_move}")
        print(f"Legal moves: {[str(move) for move in game.legal_moves]}")

        uci_str = input("Enter a move: ")

        try:
            move = Move.from_uci(uci_str, board.player_to_move)
        except ValueError as e:
            print(e)
            continue

        is_legal, reason = game.is_move_legal(move)
        if not is_legal:
            print(f"Illegal move: {reason}")
            continue

        board.make_move(move)


if __name__ == "__main__":
    main()
