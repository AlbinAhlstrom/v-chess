import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { getWsBase, getMe, createGame } from '../../api';
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
    { id: 'random', title: 'Random', icon: '❓' },
];

const STARTING_TIME_VALUES = [
    0.25, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 
    25, 30, 35, 40, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180
];

const INCREMENT_VALUES = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    25, 30, 35, 40, 45, 60, 90, 120, 150, 180
];

const GAME_MODES = [
    { id: 'quick', title: 'Quick Match', icon: '⏱️' },
    { id: 'lobby', title: 'Lobby Game', icon: '🏠' },
    { id: 'computer', title: 'vs Computer', icon: '🤖' },
    { id: 'otb', title: 'Local\nGame', icon: '👥' },
];

function Lobby() {
    const [seeks, setSeeks] = useState([]);
    const [user, setUser] = useState(null);
    const [selectedVariant, setSelectedVariant] = useState("standard");
    const [selectedColor, setSelectedColor] = useState("random");
    const [gameMode, setGameMode] = useState("quick"); // 'lobby', 'quick', 'otb', 'computer'
    const [isQuickMatching, setIsQuickMatching] = useState(false);
    const [ratingRange, setRatingRange] = useState(200);
    const [matchStartTime, setMatchStartTime] = useState(null);
    const [elapsedTime, setElapsedTime] = useState(0);
    
    // Match Pieces.js state structure
    const [isTimeControlEnabled, setIsTimeControlEnabled] = useState(true);
    const [startingTime, setStartingTime] = useState(10);
    const [increment, setIncrement] = useState(0);
    
    const socketRef = useRef(null);
    const userRef = useRef(null);
    const navigate = useNavigate();

    useEffect(() => {
        getMe()
            .then(data => {
                setUser(data.user);
                userRef.current = data.user;
                if (data.user) {
                    if (data.user.default_time !== undefined) setStartingTime(data.user.default_time);
                    if (data.user.default_increment !== undefined) setIncrement(data.user.default_increment);
                    if (data.user.default_time_control_enabled !== undefined) setIsTimeControlEnabled(data.user.default_time_control_enabled);
                }
            })
            .catch(err => console.error("Failed to fetch user in Lobby:", err));
    }, []);

    useEffect(() => {
        let interval;
        if (isQuickMatching) {
            document.body.style.overflow = 'hidden';
            setMatchStartTime(Date.now());
            setElapsedTime(0);
            interval = setInterval(() => {
                setElapsedTime(prev => prev + 1);
            }, 1000);
        } else {
            document.body.style.overflow = 'auto';
            setMatchStartTime(null);
            setElapsedTime(0);
        }
        return () => {
            clearInterval(interval);
            document.body.style.overflow = 'auto';
        };
    }, [isQuickMatching]);

    useEffect(() => {
        let socket;
        let isMounted = true;
        let timeoutId = setTimeout(() => {
            if (!isMounted) return;

            const wsUrl = `${getWsBase()}/lobby`;
            socket = new WebSocket(wsUrl);
            socketRef.current = socket;

            socket.onerror = (err) => {
                // Silently handle connection errors
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
                    navigate(`/matchmaking-game/${data.game_id}`, { state: { gameMode: 'lobby' } });
                } else if (data.type === "quick_match_found") {
                    if (data.users.includes(String(userRef.current?.id))) {
                        navigate(`/matchmaking-game/${data.game_id}`, { state: { gameMode: 'quick' } });
                    }
                }
            };
        }, 100); // 100ms delay to ensure page is stable

        return () => {
            isMounted = false;
            clearTimeout(timeoutId);
            if (socket) {
                socket.close();
            }
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

    const joinQuickMatch = () => {
        if (!user) return;
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
            socketRef.current.send(JSON.stringify({
                type: "join_quick_match",
                variant: selectedVariant,
                time_control: isTimeControlEnabled ? {
                    limit: startingTime * 60,
                    increment: increment
                } : null,
                range: ratingRange
            }));
            setIsQuickMatching(true);
        }
    };

    const leaveQuickMatch = () => {
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
            socketRef.current.send(JSON.stringify({
                type: "leave_quick_match"
            }));
            setIsQuickMatching(false);
        }
    };

    const playVsComputer = async () => {
        try {
            const data = await createGame(
                selectedVariant, 
                null, 
                isTimeControlEnabled ? { limit: startingTime * 60, increment: increment } : null,
                selectedColor,
                true // isComputer
            );
            if (data.game_id) {
                navigate(`/computer-game/${data.game_id}`);
            }
        } catch (err) {
            console.error("Failed to create computer game:", err);
        }
    };

    const handlePlay = () => {
        if (gameMode === 'quick') {
            if (isQuickMatching) leaveQuickMatch();
            else joinQuickMatch();
        } else if (gameMode === 'lobby') {
            createSeek();
        } else if (gameMode === 'computer') {
            playVsComputer();
        } else if (gameMode === 'otb') {
            navigate(selectedVariant === 'standard' ? '/otb' : `/otb/${selectedVariant}`);
        }
    };

    const switchToRandom = () => {
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
            // First leave current
            socketRef.current.send(JSON.stringify({ type: "leave_quick_match" }));
            // Then join with random
            setSelectedVariant('random');
            socketRef.current.send(JSON.stringify({
                type: "join_quick_match",
                variant: 'random',
                time_control: isTimeControlEnabled ? {
                    limit: startingTime * 60,
                    increment: increment
                } : null,
                range: ratingRange
            }));
            setElapsedTime(0);
        }
    };

    const playBotInstead = async () => {
        leaveQuickMatch();
        await playVsComputer();
    };

    const formatDuration = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div className="lobby-container">
            {isQuickMatching && (
                <div className="matching-overlay">
                    <div className="matching-modal">
                        <div className="spinner-large"></div>
                        <h2>Searching for Game...</h2>
                        <p className="elapsed-time">Time Elapsed: {formatDuration(elapsedTime)}</p>
                        
                        <div className="matching-alternatives">
                            <p>Is matchmaking taking a long time?</p>
                            <div className="alternative-buttons">
                                <button onClick={playBotInstead} className="alt-button bot">
                                    🤖 Play against a Bot
                                </button>
                                {selectedVariant !== 'random' && (
                                    <button onClick={switchToRandom} className="alt-button any">
                                        ❓ Search any Variant
                                    </button>
                                )}
                            </div>
                        </div>

                        <button onClick={leaveQuickMatch} className="cancel-match-button">
                            Cancel Search
                        </button>
                    </div>
                </div>
            )}
            
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
                    showColorSelect={false} // Handle color selection separately below
                    gameMode={gameMode}
                />

                <div className="divider" />

                <h2>Game Mode</h2>
                <div className="mode-selector">
                    {GAME_MODES.map(mode => (
                        <button
                            key={mode.id}
                            className={`variant-select-btn ${gameMode === mode.id ? 'active' : ''}`}
                            onClick={() => {
                                setGameMode(mode.id);
                                if (isQuickMatching && mode.id !== 'quick') leaveQuickMatch();
                            }}
                        >
                            <span className="variant-icon">{mode.icon}</span>
                            <div style={{ whiteSpace: 'pre-line' }}>{mode.title}</div>
                        </button>
                    ))}
                </div>

                {gameMode !== 'quick' && gameMode !== 'otb' && (
                    <div className="color-selection-container">
                        <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>Play as:</label>
                        <div className="variants-grid">
                            <button
                                className={`variant-select-btn ${selectedColor === 'white' ? 'active' : ''}`}
                                onClick={() => setSelectedColor('white')}
                            >
                                <span className="variant-icon">⚪</span>
                                <span>White</span>
                            </button>
                            <button
                                className={`variant-select-btn ${selectedColor === 'black' ? 'active' : ''}`}
                                onClick={() => setSelectedColor('black')}
                            >
                                <span className="variant-icon">⚫</span>
                                <span>Black</span>
                            </button>
                            <button
                                className={`variant-select-btn ${selectedColor === 'random' ? 'active' : ''}`}
                                onClick={() => setSelectedColor('random')}
                            >
                                <span className="variant-icon">❓</span>
                                <span>Random</span>
                            </button>
                        </div>
                    </div>
                )}

                {gameMode === 'lobby' && (
                    <div className="seeks-list">
                        <h2>Open Lobbies</h2>
                        {seeks.filter(s => s.variant === selectedVariant).length === 0 ? (
                            <p>No open {selectedVariant} lobbies found. Create one!</p>
                        ) : (
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
                                    {seeks
                                        .filter(s => s.variant === selectedVariant)
                                        .map(seek => {
                                            const isMySeek = user && String(seek.user_id) === String(user.id);
                                            return (
                                            <tr key={seek.id}>
                                                <td>
                                                    <Link to={`/profile/${seek.user_id}`} className="lobby-player-link">
                                                        {seek.user_name}
                                                    </Link>
                                                </td>
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
                )}

                <div className="lobby-actions">
                    {gameMode === 'quick' && (
                        <div className="quick-match-section">
                            <div className="range-selector">
                                <label>Rating Range: ±{ratingRange}</label>
                                <input 
                                    type="range" 
                                    min="50" 
                                    max="1000" 
                                    step="50" 
                                    value={ratingRange} 
                                    onChange={(e) => setRatingRange(parseInt(e.target.value))}
                                    disabled={isQuickMatching}
                                />
                            </div>
                        </div>
                    )}
                    
                    <button 
                        onClick={handlePlay} 
                        className={`play-main-button ${isQuickMatching ? 'matching' : ''}`}
                        disabled={!user && gameMode !== 'otb'}
                    >
                                                {isQuickMatching ? (
                                                    <><span className="spinner"></span> Cancel Matching</>
                                                ) : (
                                                    <>{gameMode === 'lobby' ? 'Create Lobby' : `Play ${GAME_MODES.find(m => m.id === gameMode).title.replace('\n', ' ')}`}</>
                                                )}
                                            </button>                                    </div>
                                </div>
                            </div>
                        );
                    }
export default Lobby;