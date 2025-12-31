import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAuthLinks, createGame } from '../../api';
import './Lobby.css';
import '../Pieces/Pieces.css'; 

// Subcomponents
import GameConfig from '../Pieces/subcomponents/GameConfig';
import { MatchingOverlay } from './subcomponents/MatchingOverlay';
import { SeekList } from './subcomponents/SeekList';
import { ColorSelector } from './subcomponents/ColorSelector';

// Hooks
import { useLobby } from './hooks/useLobby';

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
    const navigate = useNavigate();
    const { 
        seeks, user, isQuickMatching, setIsQuickMatching, elapsedTime, sendSocketMessage 
    } = useLobby(navigate);

    const [selectedVariant, setSelectedVariant] = useState("standard");
    const [selectedColor, setSelectedColor] = useState("random");
    const [gameMode, setGameMode] = useState("quick");
    const [ratingRange, setRatingRange] = useState(200);
    
    const [isTimeControlEnabled, setIsTimeControlEnabled] = useState(true);
    const [startingTime, setStartingTime] = useState(10);
    const [increment, setIncrement] = useState(0);

    useEffect(() => {
        if (user) {
            if (user.default_time !== undefined) setStartingTime(user.default_time);
            if (user.default_increment !== undefined) setIncrement(user.default_increment);
            if (user.default_time_control_enabled !== undefined) setIsTimeControlEnabled(user.default_time_control_enabled);
        }
    }, [user]);

    const formatDuration = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const handlePlay = async () => {
        if (!user && (gameMode === 'quick' || gameMode === 'lobby')) {
            window.location.href = getAuthLinks().loginLink;
            return;
        }

        const tc = isTimeControlEnabled ? { limit: startingTime * 60, increment: increment } : null;

        if (gameMode === 'quick') {
            if (isQuickMatching) {
                sendSocketMessage({ type: "leave_quick_match" });
                setIsQuickMatching(false);
            } else {
                sendSocketMessage({ type: "join_quick_match", variant: selectedVariant, time_control: tc, range: ratingRange });
                setIsQuickMatching(true);
            }
        } else if (gameMode === 'lobby') {
            sendSocketMessage({ type: "create_seek", variant: selectedVariant, color: selectedColor, time_control: tc, user });
        } else if (gameMode === 'computer') {
            try {
                const data = await createGame(selectedVariant, null, tc, selectedColor, true);
                if (data.game_id) navigate(`/computer-game/${data.game_id}`);
            } catch (err) { console.error(err); }
        } else if (gameMode === 'otb') {
            navigate(selectedVariant === 'standard' ? '/otb' : `/otb/${selectedVariant}`);
        }
    };

    return (
        <div className="lobby-container">
            {isQuickMatching && (
                <MatchingOverlay 
                    elapsedTime={elapsedTime} 
                    formatDuration={formatDuration}
                    selectedVariant={selectedVariant}
                    onCancel={() => { sendSocketMessage({ type: "leave_quick_match" }); setIsQuickMatching(false); }}
                    onPlayBot={async () => { setIsQuickMatching(false); handlePlay(); }}
                    onSwitchToRandom={() => {
                        sendSocketMessage({ type: "leave_quick_match" });
                        setSelectedVariant('random');
                        sendSocketMessage({ type: "join_quick_match", variant: 'random', time_control: isTimeControlEnabled ? { limit: startingTime * 60, increment: increment } : null, range: ratingRange });
                    }}
                />
            )}
            
            <div className="create-seek-panel">
                <h2>Variant</h2>
                <GameConfig VARIANTS={VARIANTS} selectedVariant={selectedVariant} setSelectedVariant={setSelectedVariant} selectedColor={selectedColor} setSelectedColor={setSelectedColor} isTimeControlEnabled={isTimeControlEnabled} setIsTimeControlEnabled={setIsTimeControlEnabled} startingTime={startingTime} setStartingTime={setStartingTime} STARTING_TIME_VALUES={STARTING_TIME_VALUES} increment={increment} setIncrement={setIncrement} INCREMENT_VALUES={INCREMENT_VALUES} showColorSelect={false} gameMode={gameMode} />

                <div className="divider" />
                <h2>Game Mode</h2>
                <div className="mode-selector">
                    {GAME_MODES.map(mode => (
                        <button key={mode.id} className={`variant-select-btn ${gameMode === mode.id ? 'active' : ''}`} onClick={() => { setGameMode(mode.id); if (isQuickMatching && mode.id !== 'quick') { sendSocketMessage({ type: "leave_quick_match" }); setIsQuickMatching(false); } }}>
                            <span className="variant-icon">{mode.icon}</span>
                            <div style={{ whiteSpace: 'pre-line' }}>{mode.title}</div>
                        </button>
                    ))}
                </div>

                {gameMode !== 'quick' && gameMode !== 'otb' && <ColorSelector selectedColor={selectedColor} onSelectColor={setSelectedColor} />}

                {gameMode === 'lobby' && <SeekList seeks={seeks} selectedVariant={selectedVariant} user={user} onCancelSeek={(id) => sendSocketMessage({ type: "cancel_seek", seek_id: id })} onJoinSeek={(id) => sendSocketMessage({ type: "join_seek", seek_id: id, user })} />}

                <div className="lobby-actions">
                    {gameMode === 'quick' && (
                        <div className="quick-match-section">
                            <div className="range-selector">
                                <label>Rating Range: ±{ratingRange}</label>
                                <input type="range" min="50" max="1000" step="50" value={ratingRange} onChange={(e) => setRatingRange(parseInt(e.target.value))} disabled={isQuickMatching} />
                            </div>
                        </div>
                    )}
                    <button onClick={handlePlay} className={`play-main-button ${isQuickMatching ? 'matching' : ''}`}>
                        {isQuickMatching ? <><span className="spinner"></span> Cancel Matching</> : <>{(!user && (gameMode === 'quick' || gameMode === 'lobby')) ? 'Login to Play' : (gameMode === 'lobby' ? 'Create Lobby' : `Play ${GAME_MODES.find(m => m.id === gameMode).title.replace('\n', ' ')}`)}</>}
                    </button>
                </div>
            </div>
        </div>
    );
}

export default Lobby;
