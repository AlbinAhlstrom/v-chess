import React from 'react';

export function MatchingOverlay({ 
    elapsedTime, 
    onCancel, 
    onPlayBot, 
    onSwitchToRandom, 
    selectedVariant, 
    formatDuration 
}) {
    return (
        <div className="matching-overlay">
            <div className="matching-modal">
                <div className="spinner-large"></div>
                <h2>Searching for Game...</h2>
                <p className="elapsed-time">Time Elapsed: {formatDuration(elapsedTime)}</p>
                
                <div className="matching-alternatives">
                    <p>Is matchmaking taking a long time?</p>
                    <div className="alternative-buttons">
                        <button onClick={onPlayBot} className="alt-button bot">
                            🤖 Play against a Bot
                        </button>
                        {selectedVariant !== 'random' && (
                            <button onClick={onSwitchToRandom} className="alt-button any">
                                ❓ Search any Variant
                            </button>
                        )}
                    </div>
                </div>

                <button onClick={onCancel} className="cancel-match-button">
                    Cancel Search
                </button>
            </div>
        </div>
    );
}
