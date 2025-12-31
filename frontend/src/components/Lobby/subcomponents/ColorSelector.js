import React from 'react';

export function ColorSelector({ selectedColor, onSelectColor }) {
    return (
        <div className="color-selection-container">
            <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>Play as:</label>
            <div className="variants-grid">
                <button
                    className={`variant-select-btn ${selectedColor === 'white' ? 'active' : ''}`}
                    onClick={() => onSelectColor('white')}
                >
                    <span className="variant-icon">⚪</span>
                    <span>White</span>
                </button>
                <button
                    className={`variant-select-btn ${selectedColor === 'black' ? 'active' : ''}`}
                    onClick={() => onSelectColor('black')}
                >
                    <span className="variant-icon">⚫</span>
                    <span>Black</span>
                </button>
                <button
                    className={`variant-select-btn ${selectedColor === 'random' ? 'active' : ''}`}
                    onClick={() => onSelectColor('random')}
                >
                    <span className="variant-icon">❓</span>
                    <span>Random</span>
                </button>
            </div>
        </div>
    );
}
