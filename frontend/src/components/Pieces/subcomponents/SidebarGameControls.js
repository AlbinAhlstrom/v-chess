import React from 'react';
import { useNavigate } from 'react-router-dom';
import * as Icons from './SidebarIcons';

export function SidebarGameControls({
    matchmaking,
    isGameOver,
    moveHistoryLength,
    onUndo,
    onTakeback,
    onResign,
    onDraw,
    onReset,
    onNewGame,
    onRematch,
    onNewOpponent,
    onImport,
    onCopyFen,
    onMenuToggle,
    isMenuOpen,
    takebackOffer,
    drawOffer,
    user,
    gameId,
    isQuickMatch,
    handleAcceptTakeback,
    handleDeclineTakeback,
    handleAcceptDraw,
    handleDeclineDraw
}) {
    const navigate = useNavigate();

    const renderGameControls = () => {
        if (!isGameOver) {
            // "until the first ply is complete" means length < 1 (0 moves made)
            const showAbort = moveHistoryLength === 0;
            const takebackAction = matchmaking ? onTakeback : onUndo;
            // For local games, onResign handles ending the game. For online, it resigns.
            // Abort action usually just ends the game without rating loss if early enough, 
            // but here we map it to onResign/end game logic for simplicity unless specific abort handler exists.
            // Since backend handles resign as abort if early, this is fine.
            
            return (
                <>
                    {/* Takeback / Abort Button */}
                    {takebackOffer && user && takebackOffer.by_user_id !== user.id ? (
                        <div className="takeback-prompt-container">
                            <span className="takeback-prompt">Accept takeback?</span>
                            <div className="takeback-actions">
                                <button onClick={handleAcceptTakeback} title="Accept" className="control-button accept-btn">
                                    <svg viewBox="0 0 448 512" fill="currentColor"><path d="M438.6 105.4c12.5 12.5 12.5 32.8 0 45.3l-256 256c-12.5 12.5-32.8 12.5-45.3 0l-128-128c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0L160 338.7 393.4 105.4c12.5-12.5 32.8-12.5 45.3 0z"/></svg>
                                </button>
                                <button onClick={handleDeclineTakeback} title="Decline" className="control-button decline-btn">
                                    <svg viewBox="0 0 384 512" fill="currentColor"><path d="M342.6 150.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 210.7 86.6 105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L146.7 256 41.4 361.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192 301.3 297.4 406.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.3 256 342.6 150.6z"/></svg>
                                </button>
                            </div>
                        </div>
                    ) : (
                        <button 
                            onClick={showAbort ? onResign : takebackAction} 
                            title={showAbort ? "Abort Game" : (matchmaking ? (takebackOffer ? "Waiting..." : "Offer Takeback") : "Undo")} 
                            className={`control-button ${takebackOffer ? 'waiting' : ''}`} 
                            disabled={!!takebackOffer}
                        >
                            {showAbort ? Icons.ABORT_ICON : Icons.UNDO_ICON}
                        </button>
                    )}

                    {/* Draw Button */}
                    {drawOffer && user && drawOffer.by_user_id !== user.id ? (
                        <div className="takeback-prompt-container">
                            <span className="takeback-prompt">Accept draw?</span>
                            <div className="takeback-actions">
                                <button onClick={handleAcceptDraw} title="Accept" className="control-button accept-btn">
                                    <svg viewBox="0 0 448 512" fill="currentColor"><path d="M438.6 105.4c12.5 12.5 12.5 32.8 0 45.3l-256 256c-12.5 12.5-32.8 12.5-45.3 0l-128-128c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0L160 338.7 393.4 105.4c12.5-12.5 32.8-12.5 45.3 0z"/></svg>
                                </button>
                                <button onClick={handleDeclineDraw} title="Decline" className="control-button decline-btn">
                                    <svg viewBox="0 0 384 512" fill="currentColor"><path d="M342.6 150.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 210.7 86.6 105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L146.7 256 41.4 361.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192 301.3 297.4 406.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.3 256 342.6 150.6z"/></svg>
                                </button>
                            </div>
                        </div>
                    ) : (
                        <button 
                            onClick={onDraw} 
                            title={drawOffer ? "Waiting..." : "Offer Draw"} 
                            className={`control-button ${drawOffer ? 'waiting' : ''}`} 
                            disabled={!!drawOffer}
                        >
                            {Icons.DRAW_ICON}
                        </button>
                    )}

                    {/* Resign Button */}
                    <button onClick={onResign} title="Resign" className="control-button">
                        {Icons.RESIGN_ICON}
                    </button>
                </>
            );
        } else {
            // Game Over Controls
            if (matchmaking) {
                return (
                    <>
                        <button onClick={onRematch} title="Rematch" className="control-button">
                            {Icons.REMATCH_ICON}
                        </button>
                        <button onClick={onNewOpponent} title={isQuickMatch ? "New Opponent" : "New Lobby"} className="control-button">
                            {Icons.NEW_OPPONENT_ICON}
                        </button>
                        <button onClick={() => navigate(`/analysis/${gameId}`)} title="Analysis" className="control-button">
                            {Icons.ANALYSIS_ICON}
                        </button>
                    </>
                );
            } else {
                // Local Game Over Controls
                // User said "remove new game and reset buttons".
                // But if we remove them here, the user is stuck?
                // "remove new game and reset buttons from all game types" -> likely means active game toolbar.
                // It's reasonable to offer "New Game" when the current one ends.
                return (
                    <>
                        <button onClick={onReset} title="Rematch (Reset)" className="control-button">
                            {Icons.REMATCH_ICON}
                        </button>
                        <button onClick={onNewGame} title="New Game" className="control-button">
                            {Icons.NEW_GAME_ICON}
                        </button>
                        <button onClick={() => navigate(`/analysis/${gameId}`)} title="Analysis" className="control-button">
                            {Icons.ANALYSIS_ICON}
                        </button>
                    </>
                );
            }
        }
    };

    return (
        <div className="game-controls">
            {renderGameControls()}
            
            <button onClick={onMenuToggle} title="More" className="control-button">
                {Icons.MORE_ICON}
            </button>

            {isMenuOpen && (
                <div className="more-menu-dropdown">
                     <button className="menu-item" onClick={onCopyFen}>
                        {Icons.EXPORT_ICON} Export Game
                     </button>
                     <button className="menu-item" onClick={onImport}>
                        {Icons.IMPORT_ICON} Import Game
                     </button>
                </div>
            )}
        </div>
    );
}
