import React from 'react';
import './HighlightSquare.css';

function HighlightSquare({ file, rank, isDark, color }) {
    const style = {
        left: `calc(${file} * var(--square-size))`,
        top: `calc(${rank} * var(--square-size))`,
        backgroundColor: color || undefined
    };

    return (
        <div className={`highlight-square ${isDark ? 'dark' : ''}`} style={style}></div>
    );
}

export default HighlightSquare;
