import React, { useEffect, useRef } from 'react';

export function HistoryDisplay({ 
    moveHistory, 
    viewedIndex, 
    onJumpToMove, 
    onStepBackward, 
    onStepForward 
}) {
    const activeMobileRef = useRef(null);
    const activeDesktopRef = useRef(null);

    // Determine the actual active move index (1-based)
    // 0 = Start, 1 = 1st move...
    // If viewedIndex is -1, it means "Live" (latest move), so index is moveHistory.length
    const activeIndex = viewedIndex === -1 ? moveHistory.length : viewedIndex;

    useEffect(() => {
        if (activeMobileRef.current) {
            activeMobileRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        }
        if (activeDesktopRef.current) {
            activeDesktopRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }, [activeIndex]);

    return (
        <>
            <div className="mobile-history-bar">
                <div className="mobile-history-scroll">
                    <span 
                        className={`history-item start-pos ${activeIndex === 0 ? 'active' : ''}`}
                        onClick={() => onJumpToMove(0)}
                        ref={activeIndex === 0 ? activeMobileRef : null}
                    >
                        Start
                    </span>
                    {moveHistory.map((move, i) => {
                        const moveIndex = i + 1;
                        const isActive = activeIndex === moveIndex;
                        const isWhiteMove = i % 2 === 0;
                        const moveNumber = Math.floor(i / 2) + 1;

                        return (
                            <span 
                                key={i} 
                                className={`history-item ${isActive ? 'active' : ''}`}
                                onClick={() => onJumpToMove(moveIndex)}
                                ref={isActive ? activeMobileRef : null}
                            >
                                {isWhiteMove ? `${moveNumber}. ${move}` : move}
                            </span>
                        );
                    })}
                </div>
                <div className="history-nav-controls">
                    <button 
                        className="nav-btn" 
                        onClick={onStepBackward} 
                        title="Previous"
                        disabled={activeIndex === 0}
                    >
                        <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                            <path d="M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z"/>
                        </svg>
                    </button>
                    <button 
                        className="nav-btn" 
                        onClick={onStepForward} 
                        title="Next"
                        disabled={viewedIndex === -1}
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
                }, []).map((row, i) => {
                    const whiteMoveIndex = i * 2 + 1;
                    const blackMoveIndex = i * 2 + 2;
                    const isWhiteActive = activeIndex === whiteMoveIndex;
                    const isBlackActive = activeIndex === blackMoveIndex;

                    return (
                        <div key={i} className="history-row">
                            <span style={{ color: '#888' }}>{i + 1}.</span>
                            <span 
                                className={`history-move ${isWhiteActive ? 'active' : ''}`}
                                onClick={() => onJumpToMove(whiteMoveIndex)}
                                ref={isWhiteActive ? activeDesktopRef : null}
                            >
                                {row[0]}
                            </span>
                            <span 
                                className={`history-move ${isBlackActive ? 'active' : ''}`}
                                onClick={() => row[1] && onJumpToMove(blackMoveIndex)}
                                ref={isBlackActive ? activeDesktopRef : null}
                            >
                                {row[1] || ''}
                            </span>
                        </div>
                    );
                })}
            </div>
        </>
    );
}
