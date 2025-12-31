import React, { useState, useEffect, useRef } from 'react';
import Piece from '../../Pieces/Piece';
import LegalMoveDot from '../../LegalMoveDot/LegalMoveDot';
import HighlightSquare from '../../HighlightSquare/HighlightSquare';
import Confetti from '../Confetti';
import SoundManager from '../../../helpers/soundManager';
import '../Rules.css';

function StandardTutorialBoard() {
    const [pieces, setPieces] = useState([
        { id: 'wk', type: 'K', color: 'w', file: 1, rank: 2 }, // White King at b2
        { id: 'wr', type: 'R', color: 'w', file: 2, rank: 3 }, // White Rook at c1
        { id: 'bk', type: 'k', color: 'b', file: 0, rank: 0 }, // Black King at a4
    ]);
    const [message, setMessage] = useState("Standard Chess: Checkmate the Black King! (Hint: Move the Rook to the top)");
    const [completed, setCompleted] = useState(false);
    const [selected, setSelected] = useState(null);
    const [legalMoves, setLegalMoves] = useState([]);
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
            if (clickedPiece.type === 'R') {
                for (let i = 0; i < 4; i++) {
                    if (i !== sq.file) moves.push({ file: i, rank: sq.rank });
                    if (i !== sq.rank) moves.push({ file: sq.file, rank: i });
                }
            } else {
                for (let df = -1; df <= 1; df++) {
                    for (let dr = -1; dr <= 1; dr++) {
                        if (df === 0 && dr === 0) continue;
                        const nf = sq.file + df, nr = sq.rank + dr;
                        if (nf >= 0 && nf < 4 && nr >= 0 && nr < 4) moves.push({ file: nf, rank: nr });
                    }
                }
            }
            setLegalMoves(moves);
            return;
        }

        if (selected) {
            const isLegal = legalMoves.some(m => m.file === sq.file && m.rank === sq.rank);
            if (isLegal) {
                setPieces(prev => prev.map(p => 
                    (p.file === selected.file && p.rank === selected.rank) ? { ...p, file: sq.file, rank: sq.rank } : p
                ));
                setSelected(null);
                setLegalMoves([]);
                
                if (sq.file === 2 && sq.rank === 0) {
                    setCompleted(true);
                    SoundManager.play('slam');
                    setMessage("CHECKMATE! The Rook delivers the final blow. Victory!");
                } else {
                    SoundManager.play('move');
                    setMessage("Good move, keep pushing the King into the corner!");
                }
            } else if (clickedPiece && clickedPiece.color === 'b') {
                return;
            } else {
                setSelected(null);
                setLegalMoves([]);
            }
        } else {
            setSelected(null);
            setLegalMoves([]);
        }
    };

    const handlePieceDragStart = ({ file, rank, piece }) => {
        if (completed) return;
        setSelected({ file, rank });
        const moves = [];
        if (piece === 'R') {
            for (let i = 0; i < 4; i++) {
                if (i !== file) moves.push({ file: i, rank });
                if (i !== rank) moves.push({ file, rank: i });
            }
        } else {
            for (let df = -1; df <= 1; df++) {
                for (let dr = -1; dr <= 1; dr++) {
                    if (df === 0 && dr === 0) continue;
                    const nf = file + df, nr = rank + dr;
                    if (nf >= 0 && nf < 4 && nr >= 0 && nr < 4) moves.push({ file: nf, rank: nr });
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
                setPieces(prev => prev.map(p => 
                    (p.file === selected.file && p.rank === selected.rank) ? { ...p, file: sq.file, rank: sq.rank } : p
                ));
                setSelected(null);
                setLegalMoves([]);
                if (sq.file === 2 && sq.rank === 0) {
                    setCompleted(true);
                    setMessage("CHECKMATE! The Rook delivers the final blow. Victory!");
                }
            }
        }
    };

    const reset = () => {
        setPieces([
            { id: 'wk', type: 'K', color: 'w', file: 1, rank: 2 },
            { id: 'wr', type: 'R', color: 'w', file: 2, rank: 3 },
            { id: 'bk', type: 'k', color: 'b', file: 0, rank: 0 },
        ]);
        setCompleted(false);
        setSelected(null);
        setLegalMoves([]);
        setMessage("Standard Chess: Checkmate the Black King! (Hint: Move the Rook to the top)");
    };

    return (
        <div className="standard-tutorial">
            <div className={`tutorial-board ${completed ? 'royal-victory' : ''}`} ref={boardRef} onClick={handleBoardClick}>
                {[0, 1, 2, 3].map(rank => [0, 1, 2, 3].map(file => (
                    <div key={`${file}-${rank}`} className={`tutorial-square ${(rank + file) % 2 === 1 ? 'black-square' : 'white-square'}`} />
                )))}
                {selected && <HighlightSquare file={selected.file} rank={selected.rank} color="rgba(255, 255, 0, 0.5)" />}
                {legalMoves.map((m, i) => <LegalMoveDot key={i} file={m.file} rank={m.rank} />)}
                {pieces.map(p => (
                    <Piece 
                        key={p.id} 
                        piece={p.type} 
                        file={p.file} 
                        rank={p.rank} 
                        onDragStartCallback={handlePieceDragStart} 
                        onDropCallback={handlePieceDrop}
                        className={completed ? (p.color === 'w' ? 'victory-gold' : 'royal-collapse') : (selected && selected.file === p.file && selected.rank === p.rank ? 'piece-lift' : '')}
                    />
                ))}
                
                {completed && (
                    <div className="standard-shockwave" style={{ left: '0%', top: '0%' }}></div>
                )}
                
                <Confetti trigger={completed && !hasPlayedConfetti.current} />
            </div>
            <div className="tutorial-controls">
                <p>{message}</p>
                {completed && <button onClick={reset}>Reset Tutorial</button>}
            </div>
        </div>
    );
}

export default StandardTutorialBoard;
