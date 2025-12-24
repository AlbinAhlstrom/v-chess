import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getWsBase, getMe } from '../../api';
import './Lobby.css';

const VARIANTS = [
    "standard", "antichess", "atomic", "chess960", 
    "crazyhouse", "horde", "kingofthehill", "racingkings", "threecheck"
];

function Lobby() {
    const [seeks, setSeeks] = useState([]);
    const [user, setUser] = useState(null);
    const [selectedVariant, setSelectedVariant] = useState("standard");
    const [timeLimit, setTimeLimit] = useState(10);
    const [increment, setIncrement] = useState(5);
    const socketRef = useRef(null);
    const navigate = useNavigate();

    useEffect(() => {
        getMe().then(data => setUser(data.user));
    }, []);

    useEffect(() => {
        const wsUrl = `${getWsBase()}/lobby`;
        const socket = new WebSocket(wsUrl);
        socketRef.current = socket;

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === "seeks") {
                setSeeks(data.seeks);
            } else if (data.type === "seek_created") {
                setSeeks(prev => [...prev, data.seek]);
            } else if (data.type === "seek_removed") {
                setSeeks(prev => prev.filter(s => s.id !== data.seek_id));
            } else if (data.type === "seek_accepted") {
                navigate(`/matchmaking-game/${data.game_id}`);
            }
        };

        return () => {
            socket.close();
        };
    }, [navigate]);

    const createSeek = () => {
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
            socketRef.current.send(JSON.stringify({
                type: "create_seek",
                variant: selectedVariant,
                time_control: {
                    limit: timeLimit * 60,
                    increment: increment
                },
                user: user
            }));
        }
    };

    const joinSeek = (seekId) => {
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
            socketRef.current.send(JSON.stringify({
                type: "join_seek",
                seek_id: seekId,
                user: user
            }));
        }
    };

    const cancelSeek = (seekId) => {
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
            socketRef.current.send(JSON.stringify({
                type: "cancel_seek",
                seek_id: seekId
            }));
        }
    };

    return (
        <div className="lobby-container">
            <h1>Game Lobby</h1>
            
            <div className="create-seek-panel">
                <h2>Create a Game</h2>
                <div className="form-group">
                    <label>Variant:</label>
                    <select value={selectedVariant} onChange={(e) => setSelectedVariant(e.target.value)}>
                        {VARIANTS.map(v => <option key={v} value={v}>{v}</option>)}
                    </select>
                </div>
                <div className="form-group">
                    <label>Time Limit (min):</label>
                    <input type="number" value={timeLimit} onChange={(e) => setTimeLimit(parseInt(e.target.value))} />
                </div>
                <div className="form-group">
                    <label>Increment (sec):</label>
                    <input type="number" value={increment} onChange={(e) => setIncrement(parseInt(e.target.value))} />
                </div>
                <button onClick={createSeek} className="create-button">Create Seek</button>
            </div>

            <div className="seeks-list">
                <h2>Open Seeks</h2>
                {seeks.length === 0 ? <p>No open seeks. Create one!</p> : (
                    <table>
                        <thead>
                            <tr>
                                <th>Player</th>
                                <th>Variant</th>
                                <th>Time Control</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {seeks.map(seek => (
                                <tr key={seek.id}>
                                    <td>{seek.user_name}</td>
                                    <td>{seek.variant}</td>
                                    <td>{seek.time_control.limit / 60}+{seek.time_control.increment}</td>
                                    <td>
                                        {user && String(seek.user_id) === String(user.id) ? (
                                            <button 
                                                onClick={() => cancelSeek(seek.id)}
                                                className="cancel-seek-btn"
                                            >
                                                Cancel
                                            </button>
                                        ) : (
                                            <button 
                                                onClick={() => joinSeek(seek.id)}
                                                disabled={!user}
                                            >
                                                Join
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}

export default Lobby;