import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getWsBase, getMe } from '../../api';
import './Lobby.css';
import '../Pieces/Pieces.css'; // Reuse dialog/config styles
import GameConfig from '../Pieces/subcomponents/GameConfig';

const VARIANTS = [
    { id: 'standard', title: 'Standard', icon: '♟️' },
    { id: 'antichess', title: 'Antichess', icon: '🚫' },
    { id: 'atomic', title: 'Atomic', icon: '⚛️' },
    { id: 'chess960', title: 'Chess960', icon: '🎲' },
    { id: 'crazyhouse', title: 'Crazyhouse', icon: '🏰' },
    { id: 'horde', title: 'Horde', icon: '🧟' },
    { id: 'kingofthehill', title: 'King of the Hill', icon: '⛰️' },
    { id: 'racingkings', title: 'Racing Kings', icon: '🏎️' },
    { id: 'threecheck', title: 'Three Check', icon: '3️⃣' },
];

const STARTING_TIME_VALUES = [
    0.25, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 
    25, 30, 35, 40, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180
];

const INCREMENT_VALUES = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    25, 30, 35, 40, 45, 60, 90, 120, 150, 180
];

function Lobby() {
    const [seeks, setSeeks] = useState([]);
    const [user, setUser] = useState(null);
    const [selectedVariant, setSelectedVariant] = useState("standard");
    const [selectedColor, setSelectedColor] = useState("white");
    
    // Match Pieces.js state structure
    const [isTimeControlEnabled, setIsTimeControlEnabled] = useState(true);
    const [startingTime, setStartingTime] = useState(10);
    const [increment, setIncrement] = useState(2);
    
    const socketRef = useRef(null);
    const navigate = useNavigate();

    useEffect(() => {
        getMe().then(data => setUser(data.user));
    }, []);

    useEffect(() => {
        const wsUrl = `${getWsBase()}/lobby`;
        const socket = new WebSocket(wsUrl);
        socketRef.current = socket;

        socket.onerror = (err) => {
            // Silently handle connection errors to avoid noisy console logs
            // especially when testing locally without a backend
        };

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
                color: selectedColor,
                time_control: isTimeControlEnabled ? {
                    limit: startingTime * 60,
                    increment: increment
                } : null,
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
            <h1>Create Game</h1>
            
            <div className="create-seek-panel">
                <h2>Variant</h2>
                
                <GameConfig 
                    VARIANTS={VARIANTS}
                    selectedVariant={selectedVariant}
                    setSelectedVariant={setSelectedVariant}
                    selectedColor={selectedColor}
                    setSelectedColor={setSelectedColor}
                    isTimeControlEnabled={isTimeControlEnabled}
                    setIsTimeControlEnabled={setIsTimeControlEnabled}
                    startingTime={startingTime}
                    setStartingTime={setStartingTime}
                    STARTING_TIME_VALUES={STARTING_TIME_VALUES}
                    increment={increment}
                    setIncrement={setIncrement}
                    INCREMENT_VALUES={INCREMENT_VALUES}
                    showColorSelect={true}
                />

                <div className="lobby-actions">
                    <button onClick={createSeek} className="create-button">Create Game Lobby</button>
                    <button 
                        onClick={() => navigate(selectedVariant === 'standard' ? '/otb' : `/otb/${selectedVariant}`)} 
                        className="otb-button"
                    >
                        Play Over the Board
                    </button>
                </div>
            </div>

            <div className="seeks-list">
                <h2>Open Lobbies</h2>
                {seeks.length === 0 ? <p>No open lobbies found. Create one!</p> : (
                    <table>
                        <thead>
                            <tr>
                                <th>Player</th>
                                <th>Variant</th>
                                <th>Time</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {seeks.map(seek => {
                                const isMySeek = user && String(seek.user_id) === String(user.id);
                                if (user) {
                                    console.log(`Lobby Check: MyID=${user.id} (${typeof user.id}) vs SeekOwnerID=${seek.user_id} (${typeof seek.user_id}) -> Match? ${isMySeek}`);
                                }
                                return (
                                <tr key={seek.id}>
                                    <td>{seek.user_name}</td>
                                    <td>{seek.variant}</td>
                                    <td>{seek.time_control ? `${seek.time_control.limit / 60}+${seek.time_control.increment}` : 'Unlimited'}</td>
                                    <td>
                                        {isMySeek ? (
                                            <button 
                                                onClick={() => cancelSeek(seek.id)}
                                                className="cancel-seek-btn"
                                                title="Cancel Lobby"
                                            >
                                                <svg viewBox="0 0 384 512" fill="currentColor" style={{ width: '12px', height: '12px' }}>
                                                    <path d="M342.6 150.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 210.7 86.6 105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L146.7 256 41.4 361.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192 301.3 297.4 406.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.3 256 342.6 150.6z"/>
                                                </svg>
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
                            )})}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}

export default Lobby;