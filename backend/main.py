from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chess.game import Game
from chess.board import Board
from pydantic import BaseModel

app = FastAPI()

origins = [
    "http://localhost:3000"
    "http://127.0.0.1:3000"
    "http://localhost:8000"
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

board = Board.starting_setup()
game = Game(board)


class MoveRequest(BaseModel):
    move_uci: str


@app.get("/api/board")
def get_board_state():
    """Returns the current state of the board."""

    board_fen = game.board.fen
    return {"status": "ok", "fen": board_fen, "message": "Initial board state loaded."}


@app.post("/api/move")
def make_move(move_request: MoveRequest):
    """Makes a move."""
    move = move_request.move_uci
    fen = game.execute_action(move)
    return {
        "fen": fen,
        "status": "success",
    }
