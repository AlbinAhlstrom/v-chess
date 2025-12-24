import React from 'react';

function GameConfig({ 
    VARIANTS, 
    selectedVariant, 
    setSelectedVariant, 
    selectedColor, 
    setSelectedColor,
    isTimeControlEnabled, 
    setIsTimeControlEnabled, 
    startingTime, 
    setStartingTime, 
    STARTING_TIME_VALUES, 
    increment, 
    setIncrement, 
    INCREMENT_VALUES,
    showColorSelect = false
}) {
    return (
        <>
            <div className="variants-grid">
                {VARIANTS.map(v => (
                    <button
                        key={v.id}
                        className={`variant-select-btn ${selectedVariant === v.id ? 'active' : ''}`}
                        onClick={() => setSelectedVariant(v.id)}
                    >
                        <span className="variant-icon">{v.icon}</span>
                        <span>{v.title}</span>
                    </button>
                ))}
            </div>

            {showColorSelect && (
                <div className="color-selection-container">
                    <label style={{ display: 'block', marginBottom: '10px' }}>Your Color:</label>
                    <div className="variants-grid">
                        <button
                            className={`variant-select-btn ${selectedColor === 'white' ? 'active' : ''}`}
                            onClick={() => setSelectedColor('white')}
                        >
                            <span className="variant-icon">⚪</span>
                            <span>White</span>
                        </button>
                        <button
                            className={`variant-select-btn ${selectedColor === 'random' ? 'active' : ''}`}
                            onClick={() => setSelectedColor('random')}
                        >
                            <span className="variant-icon">❓</span>
                            <span>Random</span>
                        </button>
                        <button
                            className={`variant-select-btn ${selectedColor === 'black' ? 'active' : ''}`}
                            onClick={() => setSelectedColor('black')}
                        >
                            <span className="variant-icon">⚫</span>
                            <span>Black</span>
                        </button>
                    </div>
                </div>
            )}

            <div className="time-control-settings">
                <div className="setting-row">
                    <label className="switch-container">
                        <span>Time Control</span>
                        <input 
                            type="checkbox" 
                            checked={isTimeControlEnabled} 
                            onChange={(e) => setIsTimeControlEnabled(e.target.checked)} 
                        />
                        <span className="slider round"></span>
                    </label>
                </div>
                
                {isTimeControlEnabled && (
                    <>
                        <div className="setting-row slider-setting">
                            <div className="slider-label">
                                <span>Starting Time</span>
                                <span>
                                    {startingTime === 0.25 ? '1/4' : 
                                     startingTime === 0.5 ? '1/2' : 
                                     startingTime === 1.5 ? '1 1/2' : 
                                     startingTime} min
                                </span>
                            </div>
                            <input 
                                type="range" 
                                min="0" 
                                max={STARTING_TIME_VALUES.length - 1} 
                                value={STARTING_TIME_VALUES.indexOf(startingTime)} 
                                onChange={(e) => setStartingTime(STARTING_TIME_VALUES[parseInt(e.target.value)])} 
                            />
                        </div>
                        <div className="setting-row slider-setting">
                            <div className="slider-label">
                                <span>Increment</span>
                                <span>{increment} sec</span>
                            </div>
                            <input 
                                type="range" 
                                min="0" 
                                max={INCREMENT_VALUES.length - 1} 
                                value={INCREMENT_VALUES.indexOf(increment)} 
                                onChange={(e) => setIncrement(INCREMENT_VALUES[parseInt(e.target.value)])} 
                            />
                        </div>
                    </>
                )}
            </div>
        </>
    );
}

export default GameConfig;
