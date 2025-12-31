import React from 'react';

export function HistoryDisplay({ 
    moveHistory, 
    viewedIndex, 
    onJumpToMove, 
    onStepBackward, 
    onStepForward 
}) {
    return (
        <>
            <div className="mobile-history-bar">
                <div className="mobile-history-scroll">
                    <span 
                        className={`history-item start-pos ${viewedIndex === 0 ? 'active' : ''}`}
                        onClick={() => onJumpToMove(0)}
                    >
                        Start
                    </span>
                    {moveHistory.map((move, i) => (
                        <span 
                            key={i} 
                            className={`history-item ${viewedIndex === i + 1 ? 'active' : ''}`}
                            onClick={() => onJumpToMove(i + 1)}
                        >
                            {move}
                        </span>
                    ))}
                </div>
                <div className="history-nav-controls">
                    <button 
                        className="nav-btn" 
                        onClick={onStepBackward} 
                        title="Previous"
                        disabled={viewedIndex <= 0}
                    >
                        <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                            <path d="M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z"/>
                        </svg>
                    </button>
                    <button 
                        className="nav-btn" 
                        onClick={onStepForward} 
                        title="Next"
                        disabled={viewedIndex === -1 || viewedIndex >= moveHistory.length}
                    >
                        <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                            <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
                        </svg>
                    </button>
                </div>
            </div>

            <div className="move-history">
                <div className="history-header">Moves</div>
                {moveHistory.reduce((rows, move, index) => {
                    if (index % 2 === 0) rows.push([move]);
                    else rows[rows.length - 1].push(move);
                    return rows;
                }, []).map((row, i) => (
                    <div key={i} className="history-row">
                        <span style={{ color: '#888' }}>{i + 1}.</span>
                        <span>{row[0]}</span>
                        <span>{row[1] || ''}</span>
                    </div>
                ))}
            </div>
        </>
    );
}
