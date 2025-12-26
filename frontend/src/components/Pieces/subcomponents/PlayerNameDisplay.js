import React from 'react';

function PlayerNameDisplay({ 
    isOpponent, 
    isFlipped, 
    player,
    ratingDiff,
    takebackOffer, 
    user, 
    timers, 
    turn, 
    formatTime 
}) {
    const displayClass = isOpponent ? "opponent-name" : "player-name";
    
    const playerName = player ? player.name : "Anonymous";
    const rating = player && player.rating ? player.rating : null;

    // Logic for which timer to show
    const timerKey = isOpponent 
        ? (isFlipped ? 'w' : 'b') 
        : (isFlipped ? 'b' : 'w');
    
    const isTimerActive = turn === timerKey;

    return (
        <div className={`player-name-display ${displayClass}`}>
            <div className="player-info">
                <span className="name-text">{playerName}</span>
                {rating && <span className="rating-text"> ({rating})</span>}
                {ratingDiff !== null && ratingDiff !== undefined && (
                    <span style={{
                        marginLeft: '8px',
                        backgroundColor: ratingDiff >= 0 ? '#4CAF50' : '#F44336',
                        color: 'white',
                        padding: '1px 5px',
                        borderRadius: '3px',
                        fontSize: '0.9em',
                        fontWeight: 'bold'
                    }}>
                        {ratingDiff > 0 ? `+${ratingDiff}` : ratingDiff}
                    </span>
                )}
            </div>
            
            {isOpponent && takebackOffer && user && takebackOffer.by_user_id !== user.id && (
                <span className="takeback-prompt">Accept takeback?</span>
            )}
            
            {timers && (
                <span className={`clock-display ${isTimerActive ? 'active' : ''}`}>
                    {formatTime(timers[timerKey])}
                </span>
            )}
        </div>
    );
}

export default PlayerNameDisplay;
