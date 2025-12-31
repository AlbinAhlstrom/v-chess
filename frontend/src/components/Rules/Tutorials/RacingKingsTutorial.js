import React, { useState, useEffect, useRef } from 'react';
import Piece from '../../Pieces/Piece';
import LegalMoveDot from '../../LegalMoveDot/LegalMoveDot';
import HighlightSquare from '../../HighlightSquare/HighlightSquare';
import Confetti from '../Confetti';
import SoundManager from '../../../helpers/soundManager';
import '../Rules.css';

function RacingKingsTutorialBoard() {
    const [pieces, setPieces] = useState([
        { id: 'wk', type: 'K', color: 'w', file: 0, rank: 3 }, // White King at a1
        { id: 'br', type: 'r', color: 'b', file: 2, rank: 0 }, // Black Rook at c4 (controls file 2)
    ]);
    const [message, setMessage] = useState("Racing Kings: Race your King to the top! Note: Checks are ILLEGAL.");
    const [completed, setCompleted] = useState(false);
    const [selected, setSelected] = useState(null);
    const [legalMoves, setLegalMoves] = useState([]);
    const [turboTrail, setTurboTrail] = useState(null); // { file, rank }
    const boardRef = useRef(null);
    const hasPlayedConfetti = useRef(false);

    useEffect(() => {
        if (completed && !hasPlayedConfetti.current) {
            hasPlayedConfetti.current = true;
        }
    }, [completed]);

    const getSquareFromCoords = (clientX, clientY) => {
        if (!boardRef.current) return null;
        const rect = boardRef.current.getBoundingClientRect();
        const x = clientX - rect.left;
        const y = clientY - rect.top;
        const squareSize = rect.width / 4;
        const file = Math.floor(x / squareSize);
        const rank = Math.floor(y / squareSize);
        if (file >= 0 && file < 4 && rank >= 0 && rank < 4) return { file, rank };
        return null;
    };

    const handleBoardClick = (e) => {
        if (completed) return;
        const sq = getSquareFromCoords(e.clientX, e.clientY);
        if (!sq) return;

        const clickedPiece = pieces.find(p => p.file === sq.file && p.rank === sq.rank);

        if (clickedPiece && clickedPiece.color === 'w') {
            setSelected(sq);
            const moves = [];
            for (let df = -1; df <= 1; df++) {
                for (let dr = -1; dr <= 1; dr++) {
                    if (df === 0 && dr === 0) continue;
                    const nf = sq.file + df, nr = sq.rank + dr;
                    // Check bounds and the "No Checks" rule (can't move into Rook's line on file 2)
                    if (nf >= 0 && nf < 4 && nr >= 0 && nr < 4 && nf !== 2) {
                        moves.push({ file: nf, rank: nr });
                    }
                }
            }
            setLegalMoves(moves);
            return;
        }

        if (selected) {
            const isLegal = legalMoves.some(m => m.file === sq.file && m.rank === sq.rank);
            if (isLegal) {
                const oldPos = { file: selected.file, rank: selected.rank };
                setPieces(prev => prev.map(p => p.id === 'wk' ? { ...p, file: sq.file, rank: sq.rank } : p));
                setTurboTrail(oldPos);
                setSelected(null);
                setLegalMoves([]);
                SoundManager.play('whoosh');
                
                setTimeout(() => setTurboTrail(null), 500);

                if (sq.rank === 0) {
                    setCompleted(true);
                    setMessage("FINISH LINE CROSSED! You win the race. Remember, checks are never allowed!");
                } else {
                    setMessage("Great zoom! Keep climbing, but stay out of the Rook's line of fire.");
                }
            } else if (sq.file === 2) {
                setMessage("FORBIDDEN! In Racing Kings, you cannot move into check.");
                setSelected(null);
                setLegalMoves([]);
            } else {
                setSelected(null);
                setLegalMoves([]);
            }
        } else if (clickedPiece && clickedPiece.color === 'b') {
            return;
        } else {
            setSelected(null);
            setLegalMoves([]);
        }
    };

    const handlePieceDragStart = ({ file, rank, piece }) => {
        if (completed) return;
        if (piece !== 'K') return;
        setSelected({ file, rank });
        const moves = [];
        for (let df = -1; df <= 1; df++) {
            for (let dr = -1; dr <= 1; dr++) {
                if (df === 0 && dr === 0) continue;
                const nf = file + df, nr = rank + dr;
                if (nf >= 0 && nf < 4 && nr >= 0 && nr < 4 && nf !== 2) {
                    moves.push({ file: nf, rank: nr });
                }
            }
        }
        setLegalMoves(moves);
    };

    const handlePieceDrop = ({ clientX, clientY }) => {
        if (completed) return;
        const sq = getSquareFromCoords(clientX, clientY);
        if (sq && selected) {
            const isLegal = legalMoves.some(m => m.file === sq.file && m.rank === sq.rank);
            if (isLegal) {
                const oldPos = { file: selected.file, rank: selected.rank };
                setPieces(prev => prev.map(p => p.id === 'wk' ? { ...p, file: sq.file, rank: sq.rank } : p));
                setTurboTrail(oldPos);
                setSelected(null);
                setLegalMoves([]);
                SoundManager.play('whoosh');
                
                setTimeout(() => setTurboTrail(null), 500);

                if (sq.rank === 0) {
                    setCompleted(true);
                    setMessage("FINISH LINE CROSSED! You win the race. Remember, checks are never allowed!");
                }
            }
        }
    };

    const reset = () => {
        setPieces([
            { id: 'wk', type: 'K', color: 'w', file: 0, rank: 3 },
            { id: 'br', type: 'r', color: 'b', file: 2, rank: 0 },
        ]);
        setCompleted(false);
        setSelected(null);
        setLegalMoves([]);
        setTurboTrail(null);
        setMessage("Racing Kings: Race your King to the top! Note: Checks are ILLEGAL.");
    };

    return (
        <div className="racing-kings-tutorial">
            <div className="tutorial-board" ref={boardRef} onClick={handleBoardClick}>
                {[0, 1, 2, 3].map(rank => [0, 1, 2, 3].map(file => {
                    const isTarget = rank === 0;
                    const isDanger = file === 2;
                    return (
                        <div key={`${file}-${rank}`} 
                             className={`tutorial-square ${(rank + file) % 2 === 1 ? 'black-square' : 'white-square'} ${isTarget ? 'finish-line' : ''} ${isDanger ? 'danger-line' : ''}`} 
                        />
                    );
                }))}
                {turboTrail && (
                    <div className="speed-streak" 
                         style={{ 
                             left: `${turboTrail.file * 25}%`, 
                             top: `${turboTrail.rank * 25}%`,
                         }} />
                )}
                {selected && <HighlightSquare file={selected.file} rank={selected.rank} color="rgba(255, 255, 0, 0.5)" />}
                {legalMoves.map((m, i) => <LegalMoveDot key={i} file={m.file} rank={m.rank} />)}
                {pieces.map(p => (
                    <Piece key={p.id} piece={p.type} file={p.file} rank={p.rank} 
                           onDragStartCallback={handlePieceDragStart} onDropCallback={handlePieceDrop} />
                ))}
                <Confetti trigger={completed && !hasPlayedConfetti.current} />
            </div>
            <div className="tutorial-controls">
                <p>{message}</p>
                {completed && <button onClick={reset}>Reset Tutorial</button>}
            </div>
        </div>
    );
}

export default RacingKingsTutorialBoard;
