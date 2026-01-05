from v_chess.game import Game, IllegalMoveException
from v_chess.move import Move
from v_chess.enums import MoveLegalityReason


def main():
    """Simple cli game-loop."""
    game = Game()

    while True:
        print(game.state.board)

        if game.rules.is_game_over():
            message = "Checkmate" if game.rules.is_checkmate else "Draw"
            print(message)
            break

        print(f"Player to move: {game.state.turn}")
        print(f"Legal moves: {[str(move) for move in game.rules.get_legal_moves()]}")
        print(f"{game.state.fen=}")

        uci_str = input("Enter a move: ")

        try:
            move = Move(uci_str, player_to_move=game.state.turn)
            if game.rules.validate_move(move) == MoveLegalityReason.LEGAL:
                game.take_turn(move)
            else:
                print(game.rules.validate_move(move).value)

        except (ValueError, IllegalMoveException) as e:
            print(e)
            continue


if __name__ == "__main__":
    main()

