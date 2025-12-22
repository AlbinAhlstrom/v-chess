const API_BASE = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000/api";

export const getAllLegalMoves = async (gameId) => {
    const res = await fetch(`${API_BASE}/moves/all_legal`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ game_id: gameId }),
    });
    return res.json();
};

export const createGame = async (variant = "standard", fen = null, timeControl = null) => {
    const res = await fetch(`${API_BASE}/game/new`, { 
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            variant, 
            fen,
            time_control: timeControl 
        })
    });
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

export const getGame = async (gameId) => {
    const res = await fetch(`${API_BASE}/game/${gameId}`);
    return res.json();
};


