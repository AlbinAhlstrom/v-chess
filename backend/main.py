from uuid import uuid4
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from chess.game import Game
from chess.board import Board
from chess.move import Move
from chess.square import Square


app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


games: dict[str, Game] = {}


def get_game(game_id: str) -> Game:
    if game_id not in games:
        raise HTTPException(status_code=404, detail=f"Game ID '{game_id}' not found.")
    return games[game_id]


class MoveRequest(BaseModel):
    game_id: str
    move_uci: str


class GameRequest(BaseModel):
    game_id: str


class SquareRequest(BaseModel):
    game_id: str
    square: str


class SquareSelection(BaseModel):
    game_id: str
    square: str


@app.post("/api/game/new")
def new_game():
    game_id = str(uuid4())
    board = Board.starting_setup()
    games[game_id] = Game(board)
    return {"game_id": game_id, "fen": board.fen, "turn": board.player_to_move}


@app.post("/api/board")
def get_board_state(req: GameRequest):
    game = get_game(req.game_id)
    return {
        "fen": game.board.fen,
        "turn": game.board.player_to_move,
        "is_over": game.is_over,
        "message": "Current board state loaded."
    }


@app.post("/api/move")
def make_move(req: MoveRequest):
    game = get_game(req.game_id)

    try:
        move = Move.from_uci(req.move_uci, game.board.player_to_move)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    is_legal, reason = game.is_move_legal(move)
    if not is_legal:
        raise HTTPException(status_code=400, detail=f"Illegal move: {reason}")

    game.take_turn(move)

    status = "active"
    if game.is_checkmate:
        status = "checkmate"
    elif game.is_draw:
        status = "draw"

    return {
        "fen": game.board.fen,
        "status": status,
        "turn": game.board.player_to_move,
        "is_over": game.is_over
    }


@app.post("/api/square/select")
def check_square_selectability(req: SquareSelection):
    game = get_game(req.game_id)

    try:
        piece = game.board.get_piece(req.square)
        is_selectable = bool(piece) and piece.color == game.board.player_to_move

        return {
            "is_selectable": is_selectable,
            "status": "success",
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {e}")


@app.post("/api/moves/legal")
def get_legal_moves_for_square(req: SquareRequest):
    game = get_game(req.game_id)

    try:
        sq_obj = Square.from_any(req.square)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid square format.")

    piece = game.board.get_piece(sq_obj)

    if piece is None:
        return {"moves": [], "status": "success"}

    if piece.color != game.board.player_to_move:
        raise HTTPException(status_code=400, detail=f"Piece belongs to the opponent ({piece.color}).")

    all_legal_moves = game.legal_moves
    piece_moves = [
        m.uci for m in all_legal_moves
        if m.start == sq_obj
    ]

    return {
        "moves": piece_moves,
        "status": "success",
    }
