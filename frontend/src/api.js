// Helper to get consistent API base
const getApiBase = () => {
    if (process.env.REACT_APP_API_URL) return process.env.REACT_APP_API_URL;
    
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    
    // If we are running on the production server (v-chess.com or the EC2 IP)
    // and serving from the same host as the API
    if (hostname === 'v-chess.com' || hostname === 'www.v-chess.com' || hostname === '51.21.197.139') {
        return `${protocol}//${hostname}/api`;
    }
    
    // Production domains (Vercel)
    if (hostname.endsWith('.vercel.app')) {
        return `https://api.v-chess.com/api`;
    }
    
    // Local development
    return `http://${hostname}:8000/api`;
};

// Helper to get consistent WS base
export const getWsBase = () => {
    if (process.env.REACT_APP_WS_URL) return process.env.REACT_APP_WS_URL;
    
    const hostname = window.location.hostname;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

    if (hostname === 'v-chess.com' || hostname === 'www.v-chess.com' || hostname === '51.21.197.139') {
        return `${protocol}//${hostname}/ws`;
    }

    if (hostname.endsWith('.vercel.app')) {
        return `wss://api.v-chess.com/ws`;
    }

    return `ws://${hostname}:8000/ws`;
};

const API_BASE = getApiBase();

const fetchWithLog = async (url, options = {}) => {
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            console.error(`[API] HTTP error ${response.status} fetching ${url}`);
        }
        return response;
    } catch (error) {
        console.error(`[API] Network error fetching ${url}:`, error);
        throw error;
    }
};

export const getAllLegalMoves = async (gameId) => {
    const res = await fetchWithLog(`${API_BASE}/moves/all_legal`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ game_id: gameId }),
        credentials: 'include'
    });
    return res.json();
};

export const createGame = async (variant = "standard", fen = null, timeControl = null, playAs = "white", isComputer = false) => {
    const res = await fetchWithLog(`${API_BASE}/game/new`, { 
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            variant, 
            fen,
            time_control: timeControl,
            play_as: playAs,
            is_computer: isComputer
        }),
        credentials: 'include'
    });
    return res.json();
};

export const getLegalMoves = async (gameId, square) => {
    const res = await fetchWithLog(`${API_BASE}/moves/legal`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ game_id: gameId, square }),
        credentials: 'include'
    });
    return res.json();
};

export const getGame = async (gameId) => {
    const res = await fetchWithLog(`${API_BASE}/game/${gameId}`, {
        credentials: 'include'
    });
    return res.json();
};

export const getGameFens = async (gameId) => {
    const res = await fetchWithLog(`${API_BASE}/game/${gameId}/fens`, {
        credentials: 'include'
    });
    return res.json();
};

export const getMe = async () => {
    const res = await fetchWithLog(`${API_BASE}/me`, {
        credentials: 'include'
    });
    return res.json();
};

export const getUserRatings = async (userId) => {
    const res = await fetchWithLog(`${API_BASE}/ratings/${userId}`, {
        credentials: 'include'
    });
    return res.json();
};

export const getUserProfile = async (userId) => {
    const res = await fetchWithLog(`${API_BASE}/user/${userId}`, {
        credentials: 'include'
    });
    return res.json();
};

export const getUserGames = async (userId, filters = {}) => {
    const params = new URLSearchParams(filters);
    const res = await fetchWithLog(`${API_BASE}/user/${userId}/games?${params.toString()}`, {
        credentials: 'include'
    });
    return res.json();
};

export const getLeaderboard = (variant) => {
    return fetch(`${API_BASE}/leaderboard/${variant}`).then(res => res.json());
};

export const updateUserSettings = (settings) => {
    return fetchWithLog(`${API_BASE}/user/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
        credentials: 'include'
    }).then(res => res.json());
};

export const setUsername = (username) => {
    return fetchWithLog(`${API_BASE}/user/set_username`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username }),
        credentials: 'include'
    }).then(res => res.json());
};

export const getAuthLinks = () => {
    const hostname = window.location.hostname;
    const isProd = hostname === 'v-chess.com' || hostname === 'www.v-chess.com' || hostname.endsWith('.vercel.app');
    const base = isProd ? "https://api.v-chess.com/auth" : `http://${hostname}:8000/auth`;
    return {
        loginLink: `${base}/login`,
        logoutLink: `${base}/logout`
    };
};