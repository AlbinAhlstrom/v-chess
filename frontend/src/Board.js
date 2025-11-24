import React, { useState, useEffect } from 'react';
import Square from './Square';
import { fenToBoardArray } from './fenUtils';
import './Board.css';

function Board() {
    const [boardArray, setBoardArray] = useState(Array(8).fill(Array(8).fill(null)));
    const [fen, setFen] = useState('Loading...');
    const [selectedSquare, setSelectedSquare] = useState(null);

    useEffect(() => {
        fetch('/api/board')
            .then(res => res.json())
            .then(data => {
                const fenString = data.fen;
                setFen(fenString);

                const newBoardArray = fenToBoardArray(fenString);

                setBoardArray(newBoardArray); 
            })
            .catch(error => console.error('Error fetching FEN:', error));
    }, []);

    const isLight = (row, col) => (row + col) % 2 === 0;

    return (
        <div className="chessboard-container">
            <div className="chessboard">
                {boardArray.map((row, rowIndex) => (
                    row.map((pieceChar, colIndex) => (
                        <Square
                            key={`${rowIndex}-${colIndex}`}
                            isLight={isLight(rowIndex, colIndex)}
                            pieceChar={pieceChar}
                        />
                    ))
                ))}
            </div>
        </div>
    );
}

export default Board;
