import React from 'react';

export function GamePreferences({ 
    autoPromote, 
    handleAutoPromoteToggle, 
    showCoordinates, 
    handleCoordinatesToggle 
}) {
    return (
        <section className='settings-section'>
            <h2>Game Preferences</h2>
            <div className='preference-row'>
                <div className='preference-info'>
                    <span className='label'>Auto Promote to Queen</span>
                    <p className='description'>Automatically promote pawns to Queen when reaching the last row.</p>
                </div>
                <label className='switch'>
                    <input type='checkbox' checked={autoPromote} onChange={handleAutoPromoteToggle} />
                    <span className='slider round'></span>
                </label>
            </div>

            <div className='preference-row'>
                <div className='preference-info'>
                    <span className='label'>Show Board Coordinates</span>
                    <p className='description'>Display rank (1-8) and file (a-h) labels on the board edges.</p>
                </div>
                <label className='switch'>
                    <input type='checkbox' checked={showCoordinates} onChange={handleCoordinatesToggle} />
                    <span className='slider round'></span>
                </label>
            </div>
        </section>
    );
}
