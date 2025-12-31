import React, { useState } from 'react';
import { HistoryDisplay } from './HistoryDisplay';
import { SidebarGameControls } from './SidebarGameControls';

function GameSidebar({ 
    matchmaking, 
    moveHistory, 
    onUndo,
    onTakeback,
    onReset, 
    onNewGame, 
    onResign, 
    onDraw,
    handleAcceptDraw,
    handleDeclineDraw,
    handleAcceptTakeback,
    handleDeclineTakeback,
    onImport,
    onCopyFen,
    takebackOffer,
    drawOffer,
    user,
    isGameOver,
    onRematch,
    onNewOpponent,
    gameId,
    isQuickMatch,
    onJumpToMove,
    onStepForward,
    onStepBackward,
    viewedIndex
}) {
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    return (
        <div className="game-sidebar" onClick={e => e.stopPropagation()}>
            <HistoryDisplay 
                moveHistory={moveHistory}
                viewedIndex={viewedIndex}
                onJumpToMove={onJumpToMove}
                onStepBackward={onStepBackward}
                onStepForward={onStepForward}
            />

            <SidebarGameControls 
                matchmaking={matchmaking}
                isGameOver={isGameOver}
                onUndo={onUndo}
                onTakeback={onTakeback}
                onResign={onResign}
                onDraw={onDraw}
                onReset={onReset}
                onNewGame={onNewGame}
                onRematch={onRematch}
                onNewOpponent={onNewOpponent}
                onImport={onImport}
                onCopyFen={onCopyFen}
                onMenuToggle={() => setIsMenuOpen(!isMenuOpen)}
                isMenuOpen={isMenuOpen}
                takebackOffer={takebackOffer}
                drawOffer={drawOffer}
                user={user}
                gameId={gameId}
                isQuickMatch={isQuickMatch}
                handleAcceptTakeback={handleAcceptTakeback}
                handleDeclineTakeback={handleDeclineTakeback}
                handleAcceptDraw={handleAcceptDraw}
                handleDeclineDraw={handleDeclineDraw}
            />
        </div>
    );
}

export default GameSidebar;