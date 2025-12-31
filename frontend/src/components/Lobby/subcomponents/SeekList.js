import React from 'react';
import { Link } from 'react-router-dom';

export function SeekList({ 
    seeks, 
    selectedVariant, 
    user, 
    onCancelSeek, 
    onJoinSeek 
}) {
    const filteredSeeks = seeks.filter(s => s.variant === selectedVariant);

    if (filteredSeeks.length === 0) {
        return (
            <div className="seeks-list">
                <h2>Open Lobbies</h2>
                <p>No open {selectedVariant} lobbies found. Create one!</p>
            </div>
        );
    }

    return (
        <div className="seeks-list">
            <h2>Open Lobbies</h2>
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
                    {filteredSeeks.map(seek => {
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
                                            onClick={() => onCancelSeek(seek.id)}
                                            className="cancel-seek-btn"
                                            title="Cancel Lobby"
                                        >
                                            <svg viewBox="0 0 384 512" fill="currentColor" style={{ width: '12px', height: '12px' }}>
                                                <path d="M342.6 150.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 210.7 86.6 105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L146.7 256 41.4 361.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192 301.3 297.4 406.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.3 256 342.6 150.6z"/>
                                            </svg>
                                        </button>
                                    ) : (
                                        <button 
                                            onClick={() => onJoinSeek(seek.id)}
                                            disabled={!user}
                                        >
                                            Join
                                        </button>
                                    )}
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
}
