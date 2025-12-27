import React from 'react';
import { useNavigate } from 'react-router-dom';

const UNDO_ICON = (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
        <path d="M9.4 233.4c-12.5 12.5-12.5 32.8 0 45.3l160 160c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L109.2 288 416 288c17.7 0 32-14.3 32-32s-14.3-32-32-32l-306.7 0L214.6 118.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0l-160 160z"/>
    </svg>
);

const EXPORT_ICON = (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
        <path d="M307 34.8c-11.5 5.1-19 16.6-19 29.2v64H176C78.8 128 0 206.8 0 304C0 417.3 81.5 467.9 100.2 478.1c2.5 1.4 5.3 1.9 7.8 1.9c10.9 0 19.7-8.9 19.7-19.7c0-7.5-4.3-14.4-9.8-19.5C108.8 431.9 96 414.4 96 384c0-53 43-96 96-96h96v64c0 12.6 7.4 24.1 19 29.2s25 3 34.4-5.4l160-144c6.7-6.1 10.6-14.7 10.6-24s-3.9-17.9-10.6-24l-160-144c-9.4-8.5-22.9-10.6-34.4-5.4z"/>
    </svg>
);

const NEW_GAME_ICON = (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
        <path d="M256 80c0-17.7-14.3-32-32-32s-32 14.3-32 32V224H48c-17.7 0-32 14.3-32 32s14.3 32 32 32H192V432c0 17.7 14.3 32 32 32s32-14.3 32-32V288H400c17.7 0 32-14.3 32-32s-14.3-32-32-32H256V80z"/>
    </svg>
);

const IMPORT_ICON = (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
        <path d="M128 64c0-35.3 28.7-64 64-64H352V128c0 17.7 14.3 32 32 32H512V448c0 35.3-28.7 64-64 64H192c-35.3 0-64-28.7-64-64V336H302.1l-39 39c-9.4 9.4-9.4 24.6 0 33.9s24.6 9.4 33.9 0l80-80c9.4-9.4 9.4-24.6 0-33.9l-80-80c-9.4-9.4-24.6-9.4-33.9 0s-9.4 24.6 0 33.9l39 39H128V64zm0 224v48H24c-13.3 0-24-10.7-24-24s10.7-24 24-24H128zM512 128H384c-17.7 0-32-14.3-32-32V0L512 128z"/>
    </svg>
);

const RESET_ICON = (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
        <path d="M463.5 224H472c13.3 0 24-10.7 24-24V72c0-9.7-5.8-18.5-14.8-22.2s-19.3-1.7-26.2 5.2L413.4 96.6c-87.6-86.5-228.7-86.2-315.8 1c-87.5 87.5-87.5 229.3 0 316.8s229.3 87.5 316.8 0c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0c-62.5 62.5-163.8 62.5-226.3 0s-62.5-163.8 0-226.3c62.2-62.2 162.7-62.5 225.3-1L327 183c-6.9 6.9-8.9 17.2-5.2 26.2s12.5 14.8 22.2 14.8H463.5z"/>
    </svg>
);

const MORE_ICON = (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
        <path d="M64 360a56 56 0 1 0 0 112 56 56 0 1 0 0-112zm0-160a56 56 0 1 0 0 112 56 56 0 1 0 0-112zM120 96A56 56 0 1 0 8 96a56 56 0 1 0 112 0z"/>
    </svg>
);

const DRAW_ICON = (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
        <path d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM369 209L241 337c-9.4 9.4-24.6 9.4-33.9 0l-64-64c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0l47 47L335 175c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9z" opacity="0.2"/>
        <text x="50%" y="55%" dominantBaseline="middle" textAnchor="middle" fontSize="280" fontWeight="900" fontFamily="system-ui" fill="currentColor">½</text>
    </svg>
);

const RESIGN_ICON = (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
        <path d="M48 24C48 10.7 37.3 0 24 0S0 10.7 0 24V64 350.5 400v88c0 13.3 10.7 24 24 24s24-10.7 24-24V400h80 8 24 80c21.7 0 40.6-14.6 46.2-35.3l12.3-45.2c6-22.1 26-37.5 48.9-37.5H424c13.3 0 24-10.7 24-24V72c0-13.3-10.7-24-24-24H338.6c-22.9 0-43 15.4-48.9 37.5l-12.3 45.2c-5.6 20.7-24.5 35.3-46.2 35.3H152V120 64H48V24z"/>
    </svg>
);

const REMATCH_ICON = (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
        <path d="M463.5 224H472c13.3 0 24-10.7 24-24V72c0-9.7-5.8-18.5-14.8-22.2s-19.3-1.7-26.2 5.2L413.4 96.6c-87.6-86.5-228.7-86.2-315.8 1c-87.5 87.5-87.5 229.3 0 316.8s229.3 87.5 316.8 0c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0c-62.5 62.5-163.8 62.5-226.3 0s-62.5-163.8 0-226.3c62.2-62.2 162.7-62.5 225.3-1L327 183c-6.9 6.9-8.9 17.2-5.2 26.2s12.5 14.8 22.2 14.8H463.5z"/>
    </svg>
);

const NEW_OPPONENT_ICON = (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
        <path d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM232 344V280H168c-13.3 0-24-10.7-24-24s10.7-24 24-24h64V168c0-13.3 10.7-24 24-24s24 10.7 24 24v64h64c13.3 0 24 10.7 24 24s-10.7 24-24 24H280v64c0 13.3-10.7 24-24 24s-24-10.7-24-24z"/>
    </svg>
);

const ANALYSIS_ICON = (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
        <path d="M416 208c0 45.9-14.9 88.3-40 122.7L502.6 457.4c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0L330.7 376c-34.4 25.2-76.8 40-122.7 40C93.1 416 0 322.9 0 208S93.1 0 208 0S416 93.1 416 208zM208 352a144 144 0 1 0 0-288 144 144 0 1 0 0 288z"/>
    </svg>
);

function GameSidebar({ 
    matchmaking, 
    moveHistory, 
    onUndo,
    onTakeback,
    handleReset, 
    handleNewGameClick, 
    handleMenuToggle, 
    handleResign, 
    handleOfferDraw,
    handleAcceptDraw,
    handleDeclineDraw,
    handleAcceptTakeback,
    handleDeclineTakeback,
    isMenuOpen,
    copyFenToClipboard,
    handleImportClick,
    takebackOffer,
    drawOffer,
    user,
    isGameOver,
    handleRematch,
    handleNewOpponent,
    gameId,
    isQuickMatch
}) {
    const navigate = useNavigate();
    return (
        <div className="game-sidebar" onClick={e => e.stopPropagation()}>
            <div className="move-history">
                <div className="history-header">
                    Moves
                </div>
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

            <div className="game-controls">
                {matchmaking ? (
                    <>
                        {!isGameOver ? (
                            <>
                                {takebackOffer && user && takebackOffer.by_user_id !== user.id ? (
                                    <div className="takeback-prompt-container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '5px' }}>
                                        <span className="takeback-prompt" style={{ fontSize: '12px', color: '#ffd700', fontWeight: 'bold' }}>Accept takeback?</span>
                                        <div className="takeback-actions">
                                            <button 
                                                onClick={handleAcceptTakeback}
                                                title="Accept Takeback"
                                                className="control-button accept-btn"
                                            >
                                                <svg viewBox="0 0 448 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
                                                    <path d="M438.6 105.4c12.5 12.5 12.5 32.8 0 45.3l-256 256c-12.5 12.5-32.8 12.5-45.3 0l-128-128c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0L160 338.7 393.4 105.4c12.5-12.5 32.8-12.5 45.3 0z"/>
                                                </svg>
                                            </button>
                                            <button 
                                                onClick={handleDeclineTakeback}
                                                title="Decline Takeback"
                                                className="control-button decline-btn"
                                            >
                                                <svg viewBox="0 0 384 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
                                                    <path d="M342.6 150.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 210.7 86.6 105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L146.7 256 41.4 361.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192 301.3 297.4 406.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.3 256 342.6 150.6z"/>
                                                </svg>
                                            </button>
                                        </div>
                                    </div>
                                ) : (
                                    <button 
                                        onClick={onTakeback}
                                        title={takebackOffer ? "Takeback Offered..." : "Offer Takeback"}
                                        className={`control-button ${takebackOffer ? 'waiting' : ''}`}
                                        disabled={!!takebackOffer}
                                    >
                                        {UNDO_ICON}
                                    </button>
                                )}
                                {drawOffer && user && drawOffer.by_user_id !== user.id ? (
                                    <div className="takeback-prompt-container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '5px' }}>
                                        <span className="takeback-prompt" style={{ fontSize: '12px', color: '#ffd700', fontWeight: 'bold' }}>Accept draw?</span>
                                        <div className="takeback-actions">
                                            <button 
                                                onClick={handleAcceptDraw}
                                                title="Accept Draw"
                                                className="control-button accept-btn"
                                            >
                                                <svg viewBox="0 0 448 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
                                                    <path d="M438.6 105.4c12.5 12.5 12.5 32.8 0 45.3l-256 256c-12.5 12.5-32.8 12.5-45.3 0l-128-128c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0L160 338.7 393.4 105.4c12.5-12.5 32.8-12.5 45.3 0z"/>
                                                </svg>
                                            </button>
                                            <button 
                                                onClick={handleDeclineDraw}
                                                title="Decline Draw"
                                                className="control-button decline-btn"
                                            >
                                                <svg viewBox="0 0 384 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
                                                    <path d="M342.6 150.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 210.7 86.6 105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L146.7 256 41.4 361.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192 301.3 297.4 406.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.3 256 342.6 150.6z"/>
                                                </svg>
                                            </button>
                                        </div>
                                    </div>
                                ) : (
                                    <button 
                                        onClick={handleOfferDraw}
                                        title={drawOffer ? "Draw Offered..." : "Offer Draw"}
                                        className={`control-button ${drawOffer ? 'waiting' : ''}`}
                                        disabled={!!drawOffer}
                                    >
                                        {DRAW_ICON}
                                    </button>
                                )}
                                <button 
                                    onClick={handleResign}
                                    title="Surrender"
                                    className="control-button"
                                >
                                    {RESIGN_ICON}
                                </button>
                            </>
                        ) : (
                            <>
                                <button 
                                    onClick={handleRematch}
                                    title="Rematch"
                                    className="control-button"
                                >
                                    {REMATCH_ICON}
                                </button>
                                <button 
                                    onClick={handleNewOpponent}
                                    title={isQuickMatch ? "New Opponent" : "Recreate Lobby"}
                                    className="control-button"
                                >
                                    {NEW_OPPONENT_ICON}
                                </button>
                                <button 
                                    onClick={() => navigate(`/analysis/${gameId}`)}
                                    title="Analysis Board"
                                    className="control-button"
                                >
                                    {ANALYSIS_ICON}
                                </button>
                            </>
                        )}
                    </>
                ) : (
                    <>
                        <button 
                            onClick={onUndo}
                            title="Undo"
                            className="control-button"
                        >
                            {UNDO_ICON}
                        </button>
                        <button 
                            onClick={handleReset}
                            title="Reset Game"
                            className="control-button"
                        >
                            {RESET_ICON}
                        </button>
                        <button 
                            onClick={handleNewGameClick}
                            title="New Game"
                            className="control-button"
                        >
                            {NEW_GAME_ICON}
                        </button>
                    </>
                )}
                <button 
                    onClick={handleMenuToggle}
                    title="More"
                    className="control-button"
                >
                    {MORE_ICON}
                </button>

                {isMenuOpen && (
                    <div className="more-menu-dropdown">
                         <button className="menu-item" onClick={copyFenToClipboard}>
                            {EXPORT_ICON} Export Game
                         </button>
                         <button className="menu-item" onClick={handleImportClick}>
                            {IMPORT_ICON} Import Game
                         </button>
                    </div>
                )}
            </div>
        </div>
    );
}

export default GameSidebar;
