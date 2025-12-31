import React, { useState, useEffect, useRef } from 'react';
import Piece from '../../Pieces/Piece';
import LegalMoveDot from '../../LegalMoveDot/LegalMoveDot';
import HighlightSquare from '../../HighlightSquare/HighlightSquare';
import Confetti from '../Confetti';
import SoundManager from '../../../helpers/soundManager';
import '../Rules.css';

function KOTHTutorialBoard() {
    const [pieces, setPieces] = useState([
        { id: 'wk', type: 'K', color: 'w', file: 0, rank: 3 }, // White King at a1 (4x4)
        { id: 'bk', type: 'k', color: 'b', file: 3, rank: 0 }, // Black King at d4 (4x4)
    ]);
    const [message, setMessage] = useState("King of the Hill: Race your King to the center squares!");
    const [completed, setCompleted] = useState(false);
    const [selected, setSelected] = useState(null);
    const [legalMoves, setLegalMoves] = useState([]);
    const [victoryAura, setVictoryAura] = useState(false);
    const [isShaking, setIsShaking] = useState(false);
    const boardRef = useRef(null);
    const hasPlayedConfetti = useRef(false);

    useEffect(() => {
        if (completed && !hasPlayedConfetti.current) {
            hasPlayedConfetti.current = true;
        }
    }, [completed]);

    const centerSquares = [
        { file: 1, rank: 1 }, { file: 2, rank: 1 },
        { file: 1, rank: 2 }, { file: 2, rank: 2 }
    ];

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
        if (completed || isShaking) return;
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
                    if (nf >= 0 && nf < 4 && nr >= 0 && nr < 4) moves.push({ file: nf, rank: nr });
                }
            }
            setLegalMoves(moves);
            return;
        }

        if (selected) {
            const isLegal = legalMoves.some(m => m.file === sq.file && m.rank === sq.rank);
            if (isLegal) {
                const isCenter = centerSquares.some(c => c.file === sq.file && c.rank === sq.rank);
                setPieces(prev => prev.map(p => p.id === 'wk' ? { ...p, file: sq.file, rank: sq.rank } : p));
                setSelected(null);
                setLegalMoves([]);
                
                if (isCenter) {
                    setCompleted(true);
                    setVictoryAura(true);
                    setIsShaking(true);
                    setTimeout(() => setIsShaking(false), 500);
                    setMessage("THE SUMMIT REACHED! In King of the Hill, the center is an instant victory.");
                } else {
                    SoundManager.play('move');
                    setMessage("Good move! Keep climbing toward the center summit.");
                }
            } else {
                setSelected(null);
                setLegalMoves([]);
            }
        } else if (clickedPiece && clickedPiece.color === 'b') {
            return;
        }
        else {
            setSelected(null);
            setLegalMoves([]);
        }
    };

    const handlePieceDragStart = ({ file, rank, piece }) => {
        if (completed || isShaking) return;
        if (piece !== 'K') return;
        setSelected({ file, rank });
        const moves = [];
        for (let df = -1; df <= 1; df++) {
            for (let dr = -1; dr <= 1; dr++) {
                if (df === 0 && dr === 0) continue;
                const nf = file + df, nr = rank + dr;
                if (nf >= 0 && nf < 4 && nr >= 0 && nr < 4) moves.push({ file: nf, rank: nr });
            }
        }
        setLegalMoves(moves);
    };

    const handlePieceDrop = ({ clientX, clientY }) => {
        if (completed || isShaking) return;
        const sq = getSquareFromCoords(clientX, clientY);
        if (sq && selected) {
            const isLegal = legalMoves.some(m => m.file === sq.file && m.rank === sq.rank);
            if (isLegal) {
                const isCenter = centerSquares.some(c => c.file === sq.file && c.rank === sq.rank);
                setPieces(prev => prev.map(p => p.id === 'wk' ? { ...p, file: sq.file, rank: sq.rank } : p));
                setSelected(null);
                setLegalMoves([]);
                if (isCenter) {
                    setCompleted(true);
                    setVictoryAura(true);
                    setIsShaking(true);
                    setTimeout(() => setIsShaking(false), 500);
                    setMessage("THE SUMMIT REACHED! In King of the Hill, the center is an instant victory.");
                } else {
                    SoundManager.play('move');
                    setMessage("Good move! Keep climbing toward the center summit.");
                }
            }
        }
    };

    const reset = () => {
        setPieces([
            { id: 'wk', type: 'K', color: 'w', file: 0, rank: 3 },
            { id: 'bk', type: 'k', color: 'b', file: 3, rank: 0 },
        ]);
        setCompleted(false);
        setVictoryAura(false);
        setIsShaking(false);
        setSelected(null);
        setLegalMoves([]);
        setMessage("King of the Hill: Race your King to the center squares!");
    };

    return (
        <div className="koth-tutorial">
            <div className={`tutorial-board ${isShaking ? 'shaking' : ''}`} ref={boardRef} onClick={handleBoardClick}>
                {[0, 1, 2, 3].map(rank => [0, 1, 2, 3].map(file => {
                    const isSummit = centerSquares.some(c => c.file === file && c.rank === rank);
                    const isBlack = (rank + file) % 2 === 1;
                    return (
                        <div key={`${file}-${rank}`} 
                             className={`tutorial-square ${isBlack ? 'black-square' : 'white-square'} ${isSummit ? 'summit-square' : ''}`} 
                        />
                    );
                }))}
                {selected && <HighlightSquare file={selected.file} rank={selected.rank} color="rgba(255, 255, 0, 0.5)" />}
                {legalMoves.map((m, i) => <LegalMoveDot key={i} file={m.file} rank={m.rank} />)}
                {pieces.map(p => (
                    <Piece key={p.id} piece={p.type} file={p.file} rank={p.rank} 
                           onDragStartCallback={handlePieceDragStart} onDropCallback={handlePieceDrop}
                           className={p.id === 'wk' && victoryAura ? 'koth-aura' : ''} />
                ))}
                
                {victoryAura && (
                    <div className="victory-pillar-container">
                        <div className="victory-pillar"></div>
                    </div>
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

export default KOTHTutorialBoard;
