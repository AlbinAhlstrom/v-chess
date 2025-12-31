import { useState, useEffect, useRef } from 'react';
import { getWsBase, getMe } from '../../../api';

export function useLobby(navigate) {
    const [seeks, setSeeks] = useState([]);
    const [user, setUser] = useState(null);
    const [isQuickMatching, setIsQuickMatching] = useState(false);
    const [elapsedTime, setElapsedTime] = useState(0);
    const socketRef = useRef(null);
    const userRef = useRef(null);

    useEffect(() => {
        getMe().then(data => {
            setUser(data.user);
            userRef.current = data.user;
        }).catch(err => console.error("Failed to fetch user in Lobby hook:", err));
    }, []);

    useEffect(() => {
        let interval;
        if (isQuickMatching) {
            setElapsedTime(0);
            interval = setInterval(() => setElapsedTime(prev => prev + 1), 1000);
        } else {
            setElapsedTime(0);
        }
        return () => clearInterval(interval);
    }, [isQuickMatching]);

    useEffect(() => {
        let socket;
        let isMounted = true;
        const timeoutId = setTimeout(() => {
            if (!isMounted) return;
            socket = new WebSocket(`${getWsBase()}/lobby`);
            socketRef.current = socket;
            socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === "seeks") setSeeks(data.seeks);
                else if (data.type === "seek_created") setSeeks(prev => [...prev, data.seek]);
                else if (data.type === "seek_removed") setSeeks(prev => prev.filter(s => s.id !== data.seek_id));
                else if (data.type === "seek_accepted") navigate(`/matchmaking-game/${data.game_id}`, { state: { gameMode: 'lobby' } });
                else if (data.type === "quick_match_found") {
                    if (data.users.includes(String(userRef.current?.id))) {
                        navigate(`/matchmaking-game/${data.game_id}`, { state: { gameMode: 'quick' } });
                    }
                }
            };
        }, 100);
        return () => {
            isMounted = false;
            clearTimeout(timeoutId);
            socket?.close();
        };
    }, [navigate]);

    const sendSocketMessage = (data) => {
        if (socketRef.current?.readyState === WebSocket.OPEN) {
            socketRef.current.send(JSON.stringify(data));
        }
    };

    return {
        seeks, user, isQuickMatching, setIsQuickMatching, elapsedTime, sendSocketMessage
    };
}
