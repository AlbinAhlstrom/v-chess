import React, { useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import Board from './Board';
import { Pieces } from '../Pieces/Pieces';

function GameBoardWrapper({ variant: propVariant, matchmaking = false, computer = false }) {
  const { variant: urlVariant } = useParams();
  const variant = urlVariant || propVariant || "standard";
  const [flipped, setFlipped] = useState(false);
  const [isLatest, setIsLatest] = useState(true);
  
  const handleFenChange = useCallback((newFen) => {
    // FEN state tracking removed from App
  }, []);

  const showCoordinates = (() => {
    const saved = localStorage.getItem('showBoardCoordinates');
    return saved !== null ? JSON.parse(saved) : false;
  })();

  return (
    <div className="App">
      <Board flipped={flipped} showCoordinates={showCoordinates} pointerEvents={isLatest ? 'auto' : 'none'}>
        <Pieces 
          onFenChange={handleFenChange} 
          variant={variant} 
          matchmaking={matchmaking}
          computer={computer}
          setFlipped={setFlipped}
          setIsLatest={setIsLatest}
        />
      </Board>
    </div>
  );
}

export default GameBoardWrapper;
