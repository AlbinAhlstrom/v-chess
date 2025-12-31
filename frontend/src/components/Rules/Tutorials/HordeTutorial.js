import React, { useState, useEffect, useRef } from 'react';
import Piece from '../../Pieces/Piece';
import LegalMoveDot from '../../LegalMoveDot/LegalMoveDot';
import HighlightSquare from '../../HighlightSquare/HighlightSquare';
import Confetti from '../Confetti';
import SoundManager from '../../../helpers/soundManager';
import '../Rules.css';

function HordeTutorialBoard() {
    const [pieces, setPieces] = useState([
        { id: 'wp1', type: 'P', color: 'w', file: 0, rank: 1 }, // White Pawn at a3
        { id: 'wp2', type: 'P', color: 'w', file: 1, rank: 1 }, // White Pawn at b3
        { id: 'bk', type: 'k', color: 'b', file: 0, rank: 0 }, // Black King at a4
    ]);
    const [message, setMessage] = useState("Horde: As White, your goal is to checkmate the Black King!");
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
                            if (sq.file === 1 && sq.rank === 1) {
                                moves.push({ file: 1, rank: 0 }); // Key move for mate
                            }
                            setLegalMoves(moves);
                            SoundManager.play('move');
                            return;
                        }
        if (selected && selected.file === 1 && selected.rank === 1 && sq.file === 1 && sq.rank === 0) {
            setPieces(prev => prev.map(p => 
                (p.file === 1 && p.rank === 1) ? { ...p, file: 1, rank: 0 } : p
            ));
            setSelected(null);
            setLegalMoves([]);
            setCompleted(true);
            setMessage("CHECKMATE! The King is overrun by the horde. White wins!");
        } else if (clickedPiece && clickedPiece.color === 'b') {
            return;
        } else {
            setSelected(null);
            setLegalMoves([]);
        }
    };

    const handlePieceDragStart = ({ file, rank, piece }) => {
        if (completed) return;
        if (piece !== 'P' || file !== 1) return;
        setSelected({ file, rank });
        setLegalMoves([{ file: 1, rank: 0 }]);
    };

    const handlePieceDrop = ({ clientX, clientY }) => {
        if (completed) return;
        const sq = getSquareFromCoords(clientX, clientY);
        if (sq && sq.file === 1 && sq.rank === 0 && selected && selected.file === 1) {
            setPieces(prev => prev.map(p => 
                (p.file === 1 && p.rank === 1) ? { ...p, file: 1, rank: 0 } : p
            ));
            setSelected(null);
            setLegalMoves([]);
            setCompleted(true);
            setMessage("CHECKMATE! The King is overrun by the horde. White wins!");
        }
    };

    const reset = () => {
        setPieces([
            { id: 'wp1', type: 'P', color: 'w', file: 0, rank: 1 },
            { id: 'wp2', type: 'P', color: 'w', file: 1, rank: 1 },
            { id: 'bk', type: 'k', color: 'b', file: 0, rank: 0 },
        ]);
        setCompleted(false);
        setSelected(null);
        setLegalMoves([]);
        setMessage("Horde: As White, your goal is to checkmate the Black King!");
    };

    return (
        <div className="horde-tutorial">
            <div className="tutorial-board" ref={boardRef} onClick={handleBoardClick}>
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
                        className={p.color === 'w' ? (completed ? 'horde-pawn-victory' : 'horde-pawn') : ''}
                    />
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

export default HordeTutorialBoard;
