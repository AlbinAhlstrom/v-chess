import React from 'react';
import GameConfig from './GameConfig';

function NewGameDialog({ 
    setNewGameDialogOpen, 
    opponentName, 
    setOpponentName, 
    VARIANTS, 
    newGameSelectedVariant, 
    setNewGameSelectedVariant, 
    isTimeControlEnabled, 
    setIsTimeControlEnabled, 
    startingTime, 
    setStartingTime, 
    STARTING_TIME_VALUES, 
    increment, 
    setIncrement, 
    INCREMENT_VALUES, 
    handleStartNewGame 
}) {
    return (
        <div className="new-game-dialog-overlay" onClick={() => setNewGameDialogOpen(false)}>
            <div className="new-game-dialog" onClick={e => e.stopPropagation()}>
                <h2>New Game</h2>
                
                <div className="player-names-input">
                    <div className="setting-row">
                        <label>Opponent Name</label>
                        <input 
                            type="text" 
                            value={opponentName} 
                            onChange={(e) => setOpponentName(e.target.value)}
                            placeholder="Anonymous Opponent"
                        />
                    </div>
                </div>

                <GameConfig 
                    VARIANTS={VARIANTS}
                    selectedVariant={newGameSelectedVariant}
                    setSelectedVariant={setNewGameSelectedVariant}
                    isTimeControlEnabled={isTimeControlEnabled}
                    setIsTimeControlEnabled={setIsTimeControlEnabled}
                    startingTime={startingTime}
                    setStartingTime={setStartingTime}
                    STARTING_TIME_VALUES={STARTING_TIME_VALUES}
                    increment={increment}
                    setIncrement={setIncrement}
                    INCREMENT_VALUES={INCREMENT_VALUES}
                />

                <div className="dialog-actions">
                    <button className="cancel-btn" onClick={() => setNewGameDialogOpen(false)}>Cancel</button>
                    <button className="start-btn" onClick={handleStartNewGame}>Start game</button>
                </div>
            </div>
        </div>
    );
}

export default NewGameDialog;