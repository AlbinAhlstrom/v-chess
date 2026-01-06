from v_chess.game import Game, IllegalMoveException
from v_chess.move import Move
from v_chess.enums import MoveLegalityReason


def main():
    """Starts a simple CLI game loop for standard chess."""
    game = Game()

    while True:
        print(game.state.board)

        if game.is_over:
            message = "Checkmate" if game.is_checkmate else "Draw"
            print(f"Game Over: {message} ({game.game_over_reason.value})")
            break

        print(f"Player to move: {game.state.turn}")
        print(f"Legal moves: {[str(move) for move in game.legal_moves]}")
        print(f"{game.state.fen=}")

        uci_str = input("Enter a move: ")

        try:
            move = Move(uci_str, player_to_move=game.state.turn)
            game.take_turn(move)

        except (ValueError, IllegalMoveException) as e:
            print(e)
            continue


if __name__ == "__main__":
    main()