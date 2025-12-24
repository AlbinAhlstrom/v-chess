import React from 'react';

function PlayerNameDisplay({ 
    isOpponent, 
    isFlipped, 
    playerName, 
    opponentName, 
    takebackOffer, 
    user, 
    timers, 
    turn, 
    formatTime 
}) {
    const displayClass = isOpponent ? "opponent-name" : "player-name";
    
    // Logic for which name to show based on flipping
    let nameToShow;
    if (isOpponent) {
        nameToShow = isFlipped ? playerName : opponentName;
    } else {
        nameToShow = isFlipped ? opponentName : playerName;
    }

    // Logic for which timer to show
    const timerKey = isOpponent 
        ? (isFlipped ? 'w' : 'b') 
        : (isFlipped ? 'b' : 'w');
    
    const isTimerActive = turn === timerKey;

    return (
        <div className={`player-name-display ${displayClass}`}>
            <span className="name-text">{nameToShow}</span>
            
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
