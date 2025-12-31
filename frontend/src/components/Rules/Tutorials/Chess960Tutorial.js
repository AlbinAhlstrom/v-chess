import React, { useState } from 'react';
import Piece from '../../Pieces/Piece';
import SoundManager from '../../../helpers/soundManager';
import '../Rules.css';

function Chess960TutorialBoard() {
    const [pieces, setPieces] = useState([
        { id: 'wr', type: 'R', color: 'w', file: 0, rank: 3 },
        { id: 'wn', type: 'N', color: 'w', file: 1, rank: 3 },
        { id: 'wb', type: 'B', color: 'w', file: 2, rank: 3 },
        { id: 'wk', type: 'K', color: 'w', file: 3, rank: 3 },
    ]);
    const [message, setMessage] = useState("Chess960: The starting positions of pieces are randomized!");
    const [isShuffling, setIsShuffling] = useState(false);
    const [completed, setCompleted] = useState(false);
    
    const randomize = () => {
        setIsShuffling(true);
        SoundManager.play('whoosh');
        
        // Randomize 10 times quickly for visual glitch effect
        let count = 0;
        const interval = setInterval(() => {
            const types = ['R', 'N', 'B', 'K'];
            for (let i = types.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [types[i], types[j]] = [types[j], types[i]];
            }
            setPieces(prev => prev.map((p, i) => ({ ...p, type: types[i] })));
            
            count++;
            if (count > 8) {
                clearInterval(interval);
                setIsShuffling(false);
                setCompleted(true);
                SoundManager.play('lock');
                setMessage("POSITION LOCKED! In a full game, there are 960 possible starting positions.");
            }
        }, 60);
    };

    return (
        <div className="chess960-tutorial">
            <div className={`tutorial-board ${isShuffling ? 'shuffling-board' : ''}`}>
                {[0, 1, 2, 3].map(rank => [0, 1, 2, 3].map(file => (
                    <div key={`${file}-${rank}`} className={`tutorial-square ${(rank + file) % 2 === 1 ? 'black-square' : 'white-square'}`} />
                )))}
                {pieces.map(p => (
                    <Piece 
                        key={p.id} 
                        piece={p.type} 
                        file={p.file} 
                        rank={p.rank} 
                        className={isShuffling ? 'quantum-glitch' : ''}
                    />
                ))}
            </div>
            <div className="tutorial-controls">
                <p>{message}</p>
                <button onClick={randomize} disabled={isShuffling}>Randomize Position</button>
            </div>
        </div>
    );
}

export default Chess960TutorialBoard;
