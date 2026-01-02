import React, { useState, useEffect, useRef, useCallback } from 'react';
import Piece from '../../Pieces/Piece';
import LegalMoveDot from '../../LegalMoveDot/LegalMoveDot';
import HighlightSquare from '../../HighlightSquare/HighlightSquare';
import Confetti from '../Confetti';
import SoundManager from '../../../helpers/soundManager';
import '../Rules.css';

const LEVELS = [
    {
        id: 'rook-mastery',
        title: "The Rook",
        message: "Rooks move straight (vertical or horizontal). Capture the coins at a4, d4, and d1!",
        pieces: [{ id: 'wr', type: 'R', color: 'w', file: 0, rank: 3 }], // a1
        coins: [{ file: 0, rank: 0 }, { file: 3, rank: 0 }, { file: 3, rank: 3 }], // a4, d4, d1
        goal: (p, coins) => coins.length === 0,
        maxMoves: 3
    },
    {
        id: 'bishop-mastery',
        title: "The Bishop",
        message: "Bishops move diagonally. Capture the coins at a1 and d4!",
        pieces: [{ id: 'wb', type: 'B', color: 'w', file: 1, rank: 2 }], // b2
        coins: [{ file: 0, rank: 3 }, { file: 3, rank: 0 }], // a1, d4
        goal: (p, coins) => coins.length === 0,
        maxMoves: 2
    },
    {
        id: 'queen-mastery',
        title: "The Queen",
        message: "The Queen moves like a Rook AND a Bishop. Capture a1, d4, and a4!",
        pieces: [{ id: 'wq', type: 'Q', color: 'w', file: 3, rank: 3 }], // d1
        coins: [{ file: 0, rank: 3 }, { file: 3, rank: 0 }, { file: 0, rank: 0 }], // a1, d4, a4
        goal: (p, coins) => coins.length === 0,
        maxMoves: 3
    },
    {
        id: 'king-mastery',
        title: "The King",
        message: "The King moves 1 square in any direction. Capture b2 and c3!",
        pieces: [{ id: 'wk', type: 'K', color: 'w', file: 0, rank: 3 }], // a1
        coins: [{ file: 1, rank: 2 }, { file: 2, rank: 1 }], // b2, c3
        goal: (p, coins) => coins.length === 0,
        maxMoves: 2
    },
    {
        id: 'knight-mastery',
        title: "The Knight",
        message: "Knights move in an 'L' shape (2 squares one way, 1 square sideways). Capture c2, b4, and d3!",
        pieces: [{ id: 'wn', type: 'N', color: 'w', file: 0, rank: 3 }], // a1
        coins: [{ file: 2, rank: 2 }, { file: 1, rank: 0 }, { file: 3, rank: 1 }], // c2, b4, d3
        goal: (p, coins) => coins.length === 0,
        maxMoves: 3
    },
    {
        id: 'pawn-mastery',
        title: "The Pawn",
        message: "Pawns move forward 1 step. Move to a2, then capture diagonally at b3 and a4.",
        pieces: [{ id: 'wp', type: 'P', color: 'w', file: 0, rank: 3 }], // a1
        coins: [{ file: 1, rank: 1 }, { file: 0, rank: 0 }], // b3, a4
        goal: (p, coins) => coins.length === 0,
        customLogic: 'pawn-mastery'
    },
    {
        id: 'pawn-logic',
        title: "Pawn Logic: Blockage",
        message: "Try to move forward to capture the Black pawn at b2.",
        pieces: [
            { id: 'wp1', type: 'P', color: 'w', file: 1, rank: 3 }, // b1
            { id: 'bp1', type: 'p', color: 'b', file: 1, rank: 2 }, // b2
        ],
        subSteps: [
            { id: 'block', message: "Try to move forward to capture the Black pawn at b2." },
            { id: 'move-a2', message: "Blocked! Pawns cannot capture straight. Move your other pawn forward to a2." },
            { id: 'capture', message: "Now capture the Black pawn diagonally!" }
        ]
    },
    {
        id: 'check-lesson',
        title: "What is Check?",
        message: "Move your Rook to d1 to put the Black King in check!",
        pieces: [
            { id: 'wk', type: 'K', color: 'w', file: 0, rank: 3 }, // a1
            { id: 'wr', type: 'R', color: 'w', file: 3, rank: 0 }, // d4
            { id: 'bk', type: 'k', color: 'b', file: 3, rank: 3 }, // d1
        ],
        goal: (pieces) => pieces.find(p => p.id === 'wr').rank === 3 // Moved to d1
    },
    {
        id: 'mate-lesson',
        title: "What is Checkmate?",
        message: "The King is trapped! Move your Rook to a1 to deliver Checkmate.",
        pieces: [
            { id: 'wk', type: 'K', color: 'w', file: 2, rank: 2 }, // c2
            { id: 'wr', type: 'R', color: 'w', file: 3, rank: 3 }, // d1
            { id: 'bk', type: 'k', color: 'b', file: 2, rank: 3 }, // c1
        ],
        goal: (pieces) => pieces.find(p => p.id === 'wr').file === 0 // Moved to a1
    }
];

function StandardTutorialBoard() {
    const [levelIndex, setLevelIndex] = useState(0);
    const [subStep, setSubStep] = useState(0);
    const [pieces, setPieces] = useState(LEVELS[0].pieces);
    const [coins, setCoins] = useState(LEVELS[0].coins || []);
    const [message, setMessage] = useState(LEVELS[0].message);
    const [movesCount, setMovesCount] = useState(0);
    const [completed, setCompleted] = useState(false);
    const [failed, setFailed] = useState(false);
    const [selected, setSelected] = useState(null);
    const [legalMoves, setLegalMoves] = useState([]);
    const [isProcessing, setIsProcessing] = useState(false);
    
    const boardRef = useRef(null);
    const hasPlayedConfetti = useRef(false);
    const currentLevel = LEVELS[levelIndex];

    const resetLevel = useCallback(() => {
        const lvl = LEVELS[levelIndex];
        setPieces(lvl.pieces);
        setCoins(lvl.coins || []);
        setMessage(lvl.message);
        setMovesCount(0);
        setSubStep(0);
        setCompleted(false);
        setFailed(false);
        setSelected(null);
        setLegalMoves([]);
        setIsProcessing(false);
        hasPlayedConfetti.current = false;
    }, [levelIndex]);

    useEffect(() => {
        resetLevel();
    }, [levelIndex, resetLevel]);

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

    const getLegalMoves = (piece, currentPieces) => {
        const moves = [];
        const { file, rank, type, color } = piece;

        const isOccupiedByFriendly = (f, r) => currentPieces.some(p => p.file === f && p.rank === r && p.color === color);
        const isOccupiedByEnemy = (f, r) => currentPieces.some(p => p.file === f && p.rank === r && p.color !== color);

        if (type.toUpperCase() === 'R') {
            const dirs = [[0, 1], [0, -1], [1, 0], [-1, 0]];
            dirs.forEach(([df, dr]) => {
                for (let i = 1; i < 4; i++) {
                    const nf = file + df * i, nr = rank + dr * i;
                    if (nf < 0 || nf >= 4 || nr < 0 || nr >= 4) break;
                    if (isOccupiedByFriendly(nf, nr)) break;
                    moves.push({ file: nf, rank: nr });
                    if (isOccupiedByEnemy(nf, nr)) break;
                }
            });
        } else if (type.toUpperCase() === 'B') {
            const dirs = [[1, 1], [1, -1], [-1, 1], [-1, -1]];
            dirs.forEach(([df, dr]) => {
                for (let i = 1; i < 4; i++) {
                    const nf = file + df * i, nr = rank + dr * i;
                    if (nf < 0 || nf >= 4 || nr < 0 || nr >= 4) break;
                    if (isOccupiedByFriendly(nf, nr)) break;
                    moves.push({ file: nf, rank: nr });
                    if (isOccupiedByEnemy(nf, nr)) break;
                }
            });
        } else if (type.toUpperCase() === 'Q') {
            const dirs = [[0, 1], [0, -1], [1, 0], [-1, 0], [1, 1], [1, -1], [-1, 1], [-1, -1]];
            dirs.forEach(([df, dr]) => {
                for (let i = 1; i < 4; i++) {
                    const nf = file + df * i, nr = rank + dr * i;
                    if (nf < 0 || nf >= 4 || nr < 0 || nr >= 4) break;
                    if (isOccupiedByFriendly(nf, nr)) break;
                    moves.push({ file: nf, rank: nr });
                    if (isOccupiedByEnemy(nf, nr)) break;
                }
            });
        } else if (type.toUpperCase() === 'N') {
            const jumps = [[1, 2], [1, -2], [-1, 2], [-1, -2], [2, 1], [2, -1], [-2, 1], [-2, -1]];
            jumps.forEach(([df, dr]) => {
                const nf = file + df, nr = rank + dr;
                if (nf >= 0 && nf < 4 && nr >= 0 && nr < 4 && !isOccupiedByFriendly(nf, nr)) {
                    moves.push({ file: nf, rank: nr });
                }
            });
        } else if (type.toUpperCase() === 'K') {
            for (let df = -1; df <= 1; df++) {
                for (let dr = -1; dr <= 1; dr++) {
                    if (df === 0 && dr === 0) continue;
                    const nf = file + df, nr = rank + dr;
                    if (nf >= 0 && nf < 4 && nr >= 0 && nr < 4 && !isOccupiedByFriendly(nf, nr)) {
                        moves.push({ file: nf, rank: nr });
                    }
                }
            }
        } else if (type.toUpperCase() === 'P') { // White Pawn
            if (rank > 0 && !currentPieces.some(p => p.file === file && p.rank === rank - 1)) {
                moves.push({ file, rank: rank - 1 });
            }
            // Capture coins or pieces
            [[-1, -1], [1, -1]].forEach(([df, dr]) => {
                const nf = file + df, nr = rank + dr;
                if (nf >= 0 && nf < 4 && nr >= 0 && nr < 4) {
                    const hasEnemy = isOccupiedByEnemy(nf, nr);
                    const hasCoin = coins.some(c => c.file === nf && c.rank === nr);
                    if (hasEnemy || hasCoin) {
                        moves.push({ file: nf, rank: nr });
                    }
                }
            });
        }

        return moves;
    };

    const handleLevelLogic = (nextPieces, nextCoins, sq) => {
        if (currentLevel.id === 'pawn-logic') {
            if (subStep === 0) {
                // Should have failed to capture straight
                // The legal moves won't include b2, so handleBoardClick will reset selection
                return;
            } else if (subStep === 1) {
                if (sq.file === 0 && sq.rank === 2) { // a1 to a2
                    setMessage(currentLevel.subSteps[2].message);
                    setSubStep(2);
                }
            } else if (subStep === 2) {
                if (sq.file === 1 && sq.rank === 1) { // a2 captures b3
                    setCompleted(true);
                    SoundManager.play('success');
                }
            }
        } else if (currentLevel.id === 'check-lesson') {
            if (sq.file === 3 && sq.rank === 3) { // d4 to d1
                SoundManager.play('strike');
                setMessage("Check! The Black King is under attack. It must move.");
                setIsProcessing(true);
                setTimeout(() => {
                    setPieces(prev => prev.map(p => p.id === 'bk' ? { ...p, file: 2, rank: 3 } : p)); // Move to c1
                    SoundManager.play('move');
                    setCompleted(true);
                    SoundManager.play('success');
                    setIsProcessing(false);
                }, 1000);
            }
        } else if (currentLevel.id === 'mate-lesson') {
            if (sq.file === 0 && sq.rank === 3) { // d1 to a1
                SoundManager.play('slam');
                setMessage("Checkmate! The Black King is attacked and has no safe squares. You win!");
                setCompleted(true);
                SoundManager.play('success');
            }
        }
    };

    const executeMove = (sq) => {
        if (!selected) return;
        
        const nextPieces = pieces
            .filter(p => !(p.file === sq.file && p.rank === sq.rank)) // Capture
            .map(p => (p.file === selected.file && p.rank === selected.rank) ? { ...p, file: sq.file, rank: sq.rank } : p);
        
        const nextCoins = coins.filter(c => !(c.file === sq.file && c.rank === sq.rank));
        const collected = nextCoins.length < coins.length;
        
        setPieces(nextPieces);
        setCoins(nextCoins);
        setMovesCount(prev => prev + 1);
        setSelected(null);
        setLegalMoves([]);

        if (collected) SoundManager.play('clink');
        else SoundManager.play('move');

        handleLevelLogic(nextPieces, nextCoins, sq);

        // Standard Goal Check
        if (currentLevel.goal && currentLevel.goal(nextPieces, nextCoins)) {
            setCompleted(true);
            SoundManager.play('success');
            return;
        }

        // Standard Failure Check
        if (currentLevel.maxMoves && movesCount + 1 >= currentLevel.maxMoves && nextCoins.length > 0) {
            setFailed(true);
            SoundManager.play('error');
            return;
        }
    };

    const handleBoardInteraction = (clientX, clientY) => {
        if (completed || failed || isProcessing) return;
        const sq = getSquareFromCoords(clientX, clientY);
        if (!sq) return;

        const clickedPiece = pieces.find(p => p.file === sq.file && p.rank === sq.rank);

        // Special blockage demo for Pawn Logic
        if (currentLevel.id === 'pawn-logic' && subStep === 0 && sq.file === 1 && sq.rank === 2) {
            setMessage(currentLevel.subSteps[1].message);
            setSubStep(1);
            setPieces(prev => [
                ...prev,
                { id: 'wp2', type: 'P', color: 'w', file: 0, rank: 3 }, // Add a1 pawn
                { id: 'bp2', type: 'p', color: 'b', file: 1, rank: 1 }, // Add b3 target
            ]);
            SoundManager.play('error');
            return;
        }

        if (clickedPiece && clickedPiece.color === 'w') {
            setSelected(sq);
            setLegalMoves(getLegalMoves(clickedPiece, pieces));
            return;
        }

        if (selected) {
            const isLegal = legalMoves.some(m => m.file === sq.file && m.rank === sq.rank);
            if (isLegal) {
                executeMove(sq);
            } else {
                setSelected(null);
                setLegalMoves([]);
            }
        }
    };

    const handleBoardClick = (e) => {
        handleBoardInteraction(e.clientX, e.clientY);
    };

    const handleBoardTouch = (e) => {
        if (e.cancelable) e.preventDefault();
        const touch = e.changedTouches[0];
        handleBoardInteraction(touch.clientX, touch.clientY);
    };

    const handlePieceDragStart = ({ file, rank }) => {
        if (completed || failed || isProcessing) return;
        const piece = pieces.find(p => p.file === file && p.rank === rank);
        if (!piece || piece.color !== 'w') return;
        setSelected({ file, rank });
        setLegalMoves(getLegalMoves(piece, pieces));
    };

    const handlePieceDrop = ({ clientX, clientY }) => {
        if (completed || failed || isProcessing) return;
        const sq = getSquareFromCoords(clientX, clientY);
        if (sq && selected) {
            const isLegal = legalMoves.some(m => m.file === sq.file && m.rank === sq.rank);
            if (isLegal) executeMove(sq);
        }
    };

    const nextLevel = () => {
        if (levelIndex < LEVELS.length - 1) {
            setLevelIndex(prev => prev + 1);
        }
    };

    return (
        <div className="standard-tutorial">
            <h3>{currentLevel.title}</h3>
            <div className={`tutorial-board ${completed ? 'royal-victory' : ''}`} 
                 ref={boardRef} 
                 onClick={handleBoardClick}
                 onTouchStart={handleBoardTouch}>
                {[0, 1, 2, 3].map(rank => [0, 1, 2, 3].map(file => (
                    <div key={`${file}-${rank}`} className={`tutorial-square ${(rank + file) % 2 === 1 ? 'black-square' : 'white-square'}`} />
                )))}
                
                {coins.map((c, i) => (
                    <div 
                        key={i} 
                        className="tutorial-coin" 
                        style={{ 
                            left: `${c.file * 25}%`, 
                            top: `${c.rank * 25}%`,
                            backgroundImage: 'url("/images/coin.png")'
                        }} 
                    />
                ))}

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
                        className={`${completed ? (p.color === 'w' ? 'victory-gold' : 'royal-collapse') : ''} ${!completed && !failed && p.color === 'w' ? 'forced-move' : ''}`}
                    />
                ))}
                
                {completed && <div className="standard-shockwave" style={{ left: '0%', top: '0%' }}></div>}
                <Confetti trigger={completed && !hasPlayedConfetti.current} />
            </div>

            <div className="tutorial-controls">
                <p>{failed ? "Challenge Failed! Try again." : message}</p>
                {currentLevel.maxMoves && <p>Moves: {movesCount} / {currentLevel.maxMoves}</p>}
                <div className="button-group">
                    {(failed || (completed && levelIndex === LEVELS.length - 1)) && <button onClick={resetLevel}>Retry</button>}
                    {completed && levelIndex < LEVELS.length - 1 && <button onClick={nextLevel}>Next Level</button>}
                    {completed && levelIndex === LEVELS.length - 1 && <p>CONGRATULATIONS! You've mastered the basics.</p>}
                    {!completed && !failed && <button onClick={resetLevel} style={{ marginLeft: '10px' }}>Reset</button>}
                </div>
            </div>
        </div>
    );
}

export default StandardTutorialBoard;
