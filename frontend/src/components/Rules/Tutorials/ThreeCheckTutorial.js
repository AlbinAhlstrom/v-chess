import React, { useState, useEffect, useRef } from 'react';
import Piece from '../../Pieces/Piece';
import LegalMoveDot from '../../LegalMoveDot/LegalMoveDot';
import HighlightSquare from '../../HighlightSquare/HighlightSquare';
import Confetti from '../Confetti';
import SoundManager from '../../../helpers/soundManager';
import '../Rules.css';

function ThreeCheckTutorialBoard() {
    const [pieces, setPieces] = useState([
        { id: 'wq', type: 'Q', color: 'w', file: 0, rank: 3 }, // White Queen at a1
        { id: 'bk', type: 'k', color: 'b', file: 2, rank: 1 }, // Black King at c3
    ]);
    const [checks, setChecks] = useState(0);
    const [message, setMessage] = useState("Three-Check: Deliver 3 checks to the Black King to win!");
    const [completed, setCompleted] = useState(false);
    const [selected, setSelected] = useState(null);
    const [legalMoves, setLegalMoves] = useState([]);
    const [checkFlash, setCheckFlash] = useState(false);
    const [strikeSquare, setStrikeSquare] = useState(null); // { file, rank }
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

    const isCheck = (queenFile, queenRank, kingFile, kingRank) => {
        // Vertical/Horizontal
        if (queenFile === kingFile || queenRank === kingRank) return true;
        // Diagonal
        if (Math.abs(queenFile - kingFile) === Math.abs(queenRank - kingRank)) return true;
        return false;
    };

    const handleBoardClick = (e) => {
        if (completed || checkFlash) return;
        const sq = getSquareFromCoords(e.clientX, e.clientY);
        if (!sq) return;

        const clickedPiece = pieces.find(p => p.file === sq.file && p.rank === sq.rank);

        if (clickedPiece && clickedPiece.color === 'w') {
            setSelected(sq);
            const moves = [];
            // Queen moves on 4x4
            for (let f = 0; f < 4; f++) {
                for (let r = 0; r < 4; r++) {
                    if (f === sq.file && r === sq.rank) continue;
                    if (f === sq.file || r === sq.rank || Math.abs(f - sq.file) === Math.abs(r - sq.rank)) {
                        if (!(f === 2 && r === 1)) moves.push({ file: f, rank: r }); // Can't land on King
                    }
                }
            }
            setLegalMoves(moves);
            return;
        }

        if (selected) {
            const isLegal = legalMoves.some(m => m.file === sq.file && m.rank === sq.rank);
            if (isLegal) {
                const king = pieces.find(p => p.id === 'bk');
                const deliverCheck = isCheck(sq.file, sq.rank, king.file, king.rank);
                
                setPieces(prev => prev.map(p => p.id === 'wq' ? { ...p, file: sq.file, rank: sq.rank } : p));
                setSelected(null);
                setLegalMoves([]);

                if (deliverCheck) {
                    const nextChecks = checks + 1;
                    setChecks(nextChecks);
                    setCheckFlash(true);
                    setStrikeSquare({ file: king.file, rank: king.rank });
                    SoundManager.play('strike');
                    
                    setTimeout(() => {
                        setCheckFlash(false);
                        setStrikeSquare(null);
                    }, 600);

                    if (nextChecks >= 3) {
                        setCompleted(true);
                        setMessage("3RD CHECK DELIVERED! Absolute victory by Three-Check rules.");
                    } else {
                        setMessage(`CHECK! Strike ${nextChecks}/3 landed. Finish him!`);
                    }
                } else {
                    setMessage("Move delivered, but it wasn't a check. Aim for the King!");
                }
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
        if (completed || checkFlash) return;
        if (piece !== 'Q') return;
        setSelected({ file, rank });
        const moves = [];
        for (let f = 0; f < 4; f++) {
            for (let r = 0; r < 4; r++) {
                if (f === file && r === rank) continue;
                if (f === file || r === rank || Math.abs(f - file) === Math.abs(r - rank)) {
                    if (!(f === 2 && r === 1)) moves.push({ file: f, rank: r });
                }
            }
        }
        setLegalMoves(moves);
    };

    const handlePieceDrop = ({ clientX, clientY }) => {
        if (completed || checkFlash) return;
        const sq = getSquareFromCoords(clientX, clientY);
        if (sq && selected) {
            const isLegal = legalMoves.some(m => m.file === sq.file && m.rank === sq.rank);
            if (isLegal) {
                const king = pieces.find(p => p.id === 'bk');
                const deliverCheck = isCheck(sq.file, sq.rank, king.file, king.rank);
                
                setPieces(prev => prev.map(p => p.id === 'wq' ? { ...p, file: sq.file, rank: sq.rank } : p));
                setSelected(null);
                setLegalMoves([]);

                if (deliverCheck) {
                    const nextChecks = checks + 1;
                    setChecks(nextChecks);
                    setCheckFlash(true);
                    setStrikeSquare({ file: king.file, rank: king.rank });
                    SoundManager.play('strike');
                    
                    setTimeout(() => {
                        setCheckFlash(false);
                        setStrikeSquare(null);
                    }, 600);

                    if (nextChecks >= 3) {
                        setCompleted(true);
                        setMessage("3RD CHECK DELIVERED! Absolute victory by Three-Check rules.");
                    } else {
                        setMessage(`CHECK! Strike ${nextChecks}/3 landed. Finish him!`);
                    }
                } else {
                    setMessage("Move delivered, but it wasn't a check. Aim for the King!");
                }
            }
        }
    };

    const reset = () => {
        setPieces([
            { id: 'wq', type: 'Q', color: 'w', file: 0, rank: 3 },
            { id: 'bk', type: 'k', color: 'b', file: 2, rank: 1 },
        ]);
        setChecks(0);
        setCompleted(false);
        setSelected(null);
        setLegalMoves([]);
        setCheckFlash(false);
        setStrikeSquare(null);
        setMessage("Three-Check: Deliver 3 checks to the Black King to win!");
    };

    return (
        <div className="three-check-tutorial">
            <div className="health-gauge-container">
                <div className="health-label">KING HEALTH</div>
                <div className="health-bar-bg">
                    <div className="health-bar-fill" style={{ width: `${(3 - checks) * 33.33}%` }}></div>
                </div>
                <div className="checks-label">Checks: {checks} / 3</div>
            </div>
            <div className={`tutorial-board ${checkFlash && checks === 3 ? 'extreme-shake' : ''}`} ref={boardRef} onClick={handleBoardClick}>
                {[0, 1, 2, 3].map(rank => [0, 1, 2, 3].map(file => (
                    <div key={`${file}-${rank}`} className={`tutorial-square ${(rank + file) % 2 === 1 ? 'black-square' : 'white-square'}`} />
                )))}
                {selected && <HighlightSquare file={selected.file} rank={selected.rank} color="rgba(255, 255, 0, 0.5)" />}
                {legalMoves.map((m, i) => <LegalMoveDot key={i} file={m.file} rank={m.rank} />)}
                {pieces.map(p => (
                    <Piece key={p.id} piece={p.type} file={p.file} rank={p.rank} 
                           onDragStartCallback={handlePieceDragStart} onDropCallback={handlePieceDrop}
                           className={p.id === 'bk' && checkFlash ? 'check-pulse' : ''} />
                ))}
                
                {strikeSquare && (
                    <div className="check-strike-visceral" 
                         style={{ left: `${strikeSquare.file * 25}%`, top: `${strikeSquare.rank * 25}%` }}>
                        <div className="strike-line"></div>
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

export default ThreeCheckTutorialBoard;
