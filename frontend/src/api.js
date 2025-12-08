const API_BASE = "http://127.0.0.1:8000/api";

export const getFen = () => {return "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";}

export const createGame = async () => {
    const res = await fetch(`${API_BASE}/game/new`, { method: "POST" });
    return res.json();
};

export const getLegalMoves = async (gameId, square) => {
    const res = await fetch(`${API_BASE}/moves/legal`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ game_id: gameId, square }),
    });
    return res.json();
};

export const makeMove = async (gameId, moveUci) => {
    const res = await fetch(`${API_BASE}/move`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ game_id: gameId, move_uci: moveUci }),
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail);
    }
    return res.json();
};
