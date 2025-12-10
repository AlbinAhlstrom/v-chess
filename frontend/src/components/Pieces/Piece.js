import React from 'react';
import './Pieces.css';

function Piece({ piece, file, rank, onDragStartCallback, onDragEndCallback }) {

    const pieceStyle = {

        left: `calc(${file} * var(--square-size))`,

        top: `calc(${rank} * var(--square-size))`,

        '--piece-image': `url("/images/pieces/${piece}.png")`

    };

    const onDragStart = e => {

        e.dataTransfer.setData("text/plain",`${piece},${file},${rank}`)

        e.dataTransfer.effectAllowed = "move"

        if (onDragStartCallback) {
            onDragStartCallback({ file, rank, piece });
        }

        setTimeout(() => {

            e.target.style.display = "none"

        }, 0)

    }



    const onDragEnd = e => {

        e.target.style.display = "block"
        if (onDragEndCallback) {
            onDragEndCallback();
        }

    }



    return (

        <div

            className="piece"

            style={pieceStyle}

            draggable={true}

            onDragStart={onDragStart}

            onDragEnd={onDragEnd}

        />

    );

}

export default Piece;
