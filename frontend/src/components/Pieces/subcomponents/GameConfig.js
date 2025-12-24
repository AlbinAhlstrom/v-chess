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
                    <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>Color:</label>
                    <div className="variants-grid">
                        <button
                            className={`variant-select-btn ${selectedColor === 'white' ? 'active' : ''}`}
                            onClick={() => setSelectedColor('white')}
                        >
                            <span className="variant-icon">⚪</span>
                            <span>White</span>
                        </button>
                        <button
                            className={`variant-select-btn ${selectedColor === 'black' ? 'active' : ''}`}
                            onClick={() => setSelectedColor('black')}
                        >
                            <span className="variant-icon">⚫</span>
                            <span>Black</span>
                        </button>
                        <button
                            className={`variant-select-btn ${selectedColor === 'random' ? 'active' : ''}`}
                            onClick={() => setSelectedColor('random')}
                        >
                            <span className="variant-icon">❓</span>
                            <span>Random</span>
                        </button>
                    </div>
                </div>
            )}

            <div className="time-control-settings">
                <div className="time-control-row">
                    <div className="control-item">
                        <label className="small-label">Time Control</label>
                        <label className="switch-container compact">
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
                            <div className="control-item">
                                <label className="small-label">Starting Time</label>
                                <select 
                                    value={startingTime} 
                                    onChange={(e) => setStartingTime(parseFloat(e.target.value))}
                                    className="time-select compact"
                                >
                                    <option value={0.5}>💥 1/2 min</option>
                                    <option value={1}>💥 1 min</option>
                                    <option value={3}>⚡ 3 min</option>
                                    <option value={5}>⚡ 5 min</option>
                                    <option value={10}>⚡ 10 min</option>
                                    <option value={15}>⏱️ 15 min</option>
                                    <option value={30}>⏱️ 30 min</option>
                                </select>
                            </div>
                            <div className="control-item">
                                <label className="small-label">Increment</label>
                                <select 
                                    value={increment} 
                                    onChange={(e) => setIncrement(parseInt(e.target.value))}
                                    className="time-select compact"
                                >
                                    <option value={0}>0 sec</option>
                                    <option value={1}>1 sec</option>
                                    <option value={2}>2 sec</option>
                                    <option value={3}>3 sec</option>
                                                                    <option value={5}>5 sec</option>
                                                                    <option value={10}>10 sec</option>
                                                                    <option value={20}>20 sec</option>
                                                                    <option value={30}>30 sec</option>                                </select>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </>
    );
}

export default GameConfig;
