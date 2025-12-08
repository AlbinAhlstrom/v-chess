import React from 'react';
import './Pieces.css';

function Piece({ piece, file, rank }) {
    const pieceStyle = {
        left: `calc(${file} * var(--square-size))`,
        top: `calc(${rank} * var(--square-size))`,
    };
    const onDragStart = e => {
        e.dataTransfer.setData("text/plain",`${piece},${file},${rank}`)
        e.dataTransfer.effectAllowed = "move"
        setTimeout(() => {
            e.target.style.display = "none"
        }, 0)
    }

    return (
        <div
            className={`piece ${piece}`}
            style={pieceStyle}
            draggable={true}
            onDragStart={onDragStart}
        />
    );
}

export default Piece;
