import React from 'react';

function GameOverIndicator({ isGameOver, position, winner, isFlipped }) {
    if (!isGameOver) return null;

    const getKingSquare = (color) => {
        const kingChar = color === 'w' ? 'K' : 'k';
        for (let r = 0; r < 8; r++) {
            for (let f = 0; f < 8; f++) {
                if (position[r] && position[r][f] === kingChar) {
                    return { file: f, rank: r };
                }
            }
        }
        return color === 'w' ? { file: 4, rank: 7 } : { file: 4, rank: 0 };
    };

    const whiteKingSq = getKingSquare('w');
    const blackKingSq = getKingSquare('b');

    const getStatusColor = (color) => {
        if (!winner) return 'grey'; // Draw
        return winner === color ? '#4CAF50' : '#F44336';
    };

    const renderIndicator = (sq, color) => {
        let displayFile = isFlipped ? 7 - sq.file : sq.file;
        let displayRank = isFlipped ? 7 - sq.rank : sq.rank;
        return (
            <div key={color} style={{
                position: 'absolute',
                left: `calc(${displayFile} * var(--square-size) + var(--square-size) / 2 - 15px)`,
                top: `calc(${displayRank} * var(--square-size) + var(--square-size) / 2 - 15px)`,
                width: '30px',
                height: '30px',
                borderRadius: '50%',
                backgroundColor: getStatusColor(color),
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                zIndex: 1000,
                boxShadow: '0 2px 5px rgba(0,0,0,0.5)'
            }}>
                <img 
                    src={`/images/pieces/${color === 'w' ? 'K' : 'k'}.png`} 
                    style={{ width: '20px', height: '20px', filter: 'brightness(0) invert(1)' }} 
                    alt="" 
                />
            </div>
        );
    };

    return (
        <>
            {renderIndicator(whiteKingSq, 'w')}
            {renderIndicator(blackKingSq, 'b')}
        </>
    );
}

export default GameOverIndicator;
