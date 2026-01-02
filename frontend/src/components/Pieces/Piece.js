import React from 'react';
import './Pieces.css';
import { usePieceDrag } from './hooks/usePieceDrag';

function Piece({ 
    piece, file, rank, actualFile, actualRank, 
    onDragStartCallback, onDragEndCallback, onDropCallback, onDragHoverCallback, 
    className = '', canMove = false, onPieceClick 
}) {
    const realFile = actualFile !== undefined ? actualFile : file;
    const realRank = actualRank !== undefined ? actualRank : rank;

    const fileChar = String.fromCharCode(97 + realFile);
    const rankChar = 8 - realRank;
    const squareStr = `${fileChar}${rankChar}`;

    const pieceStyle = {
        left: `calc(${file} * var(--square-size))`,
        top: `calc(${rank} * var(--square-size))`,
        '--piece-image': `url("/images/pieces/${piece}.png")`
    };

    const { handlePointerDown, handlePointerMove, handlePointerUp } = usePieceDrag({
        piece, realFile, realRank, pieceStyle,
        onDragStartCallback, onDragEndCallback, onDropCallback, onDragHoverCallback,
        onPieceClick
    });

    return (
        <div
            className={`piece ${piece} ${className}`}
            style={{...pieceStyle, touchAction: 'none'}}
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
            data-piece={piece}
            data-square={squareStr}
        />
    );
}

export default React.memo(Piece);