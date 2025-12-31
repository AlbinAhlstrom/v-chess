import React, { useState, useEffect, useRef } from 'react';
import Piece from '../../Pieces/Piece';
import LegalMoveDot from '../../LegalMoveDot/LegalMoveDot';
import HighlightSquare from '../../HighlightSquare/HighlightSquare';
import Confetti from '../Confetti';
import SoundManager from '../../../helpers/soundManager';
import '../Rules.css';

function CrazyhouseTutorialBoard() {
    const [pieces, setPieces] = useState([
        { id: 'wr', type: 'R', color: 'w', file: 0, rank: 3 }, // White Rook at a1 (relative 4x4)
        { id: 'bb', type: 'b', color: 'b', file: 2, rank: 1 }, // Black Bishop at c3 (relative 4x4)
    ]);
    const [reserve, setReserve] = useState([]); // List of piece types: ['B']
    const [message, setMessage] = useState("Crazyhouse: Capture the Black Bishop to add it to your reserve!");
    const [completed, setCompleted] = useState(false);
    const [selected, setSelected] = useState(null);
    const [legalMoves, setLegalMoves] = useState([]);
    const [selectedReserve, setSelectedReserve] = useState(null); // index in reserve
    const [warpPieceId, setWarpPieceId] = useState(null); // ID of piece to animate drop
    const [pocketingPiece, setPocketingPiece] = useState(null); // { type, file, rank }
    const [pocketArrival, setPocketArrival] = useState(false);
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
        if (completed || pocketingPiece) return;
        const sq = getSquareFromCoords(e.clientX, e.clientY);
        if (!sq) return;

        // Handling Drops
        if (selectedReserve !== null) {
            const isOccupied = pieces.some(p => p.file === sq.file && p.rank === sq.rank);
            if (!isOccupied) {
                const type = reserve[selectedReserve];
                const dropId = `drop-${Date.now()}`;
                const newPiece = { id: dropId, type, color: 'w', file: sq.file, rank: sq.rank };
                setPieces(prev => [...prev, newPiece]);
                setReserve(prev => prev.filter((_, i) => i !== selectedReserve));
                setSelectedReserve(null);
                setWarpPieceId(dropId);
                setCompleted(true);
                SoundManager.play('clink');
                setMessage("Excellent! You dropped a piece from your reserve onto the board. This is the heart of Crazyhouse!");
                
                // Clear warp effect after animation
                setTimeout(() => setWarpPieceId(null), 600);
            }
            return;
        }

        const clickedPiece = pieces.find(p => p.file === sq.file && p.rank === sq.rank);

        if (clickedPiece && clickedPiece.color === 'w') {
            setSelected(sq);
            setLegalMoves([{ file: 2, rank: 1 }]); // Only allow capture for the tutorial
            setMessage("Now capture that Bishop!");
            return;
        }

        if (selected && sq.file === 2 && sq.rank === 1) {
            // Capture logic
            setPocketingPiece({ type: 'B', file: 2, rank: 1 });
            setPieces(prev => prev.filter(p => p.id !== 'bb').map(p => 
                p.id === 'wr' ? { ...p, file: 2, rank: 1 } : p
            ));
            setSelected(null);
            setLegalMoves([]);
            SoundManager.play('capture');
            
            // Wait for flight animation (0.5s)
            setTimeout(() => {
                setReserve(['B']);
                setPocketingPiece(null);
                setPocketArrival(true);
                SoundManager.play('clink');
                setTimeout(() => setPocketArrival(false), 300);
                setMessage("Bishop captured! It's now in your reserve. Click it in the tray, then click an empty square to drop it!");
            }, 500);
        } else if (clickedPiece && clickedPiece.color === 'b') {
            return;
        } else {
            setSelected(null);
            setLegalMoves([]);
        }
    };

    const handlePieceDragStart = ({ file, rank, piece }) => {
        if (completed || pocketingPiece) return;
        if (piece !== 'R') return;
        setSelected({ file, rank });
        setLegalMoves([{ file: 2, rank: 1 }]);
    };

    const handlePieceDrop = ({ clientX, clientY }) => {
        if (completed || pocketingPiece) return;
        const sq = getSquareFromCoords(clientX, clientY);
        if (sq && sq.file === 2 && sq.rank === 1) {
            setPocketingPiece({ type: 'B', file: 2, rank: 1 });
            setPieces(prev => prev.filter(p => p.id !== 'bb').map(p => 
                p.id === 'wr' ? { ...p, file: 2, rank: 1 } : p
            ));
            setSelected(null);
            setLegalMoves([]);
            SoundManager.play('capture');
            
            setTimeout(() => {
                setReserve(['B']);
                setPocketingPiece(null);
                setPocketArrival(true);
                SoundManager.play('clink');
                setTimeout(() => setPocketArrival(false), 300);
                setMessage("Bishop captured! It's now in your reserve. Click it in the tray, then click an empty square to drop it!");
            }, 500);
        }
    };

    const reset = () => {
        setPieces([
            { id: 'wr', type: 'R', color: 'w', file: 0, rank: 3 },
            { id: 'bb', type: 'b', color: 'b', file: 2, rank: 1 },
        ]);
        setReserve([]);
        setCompleted(false);
        setSelected(null);
        setLegalMoves([]);
        setSelectedReserve(null);
        setPocketingPiece(null);
        setMessage("Crazyhouse: Capture the Black Bishop to add it to your reserve!");
    };

    return (
        <div className="crazyhouse-tutorial">
            <div className="tutorial-board" ref={boardRef} onClick={handleBoardClick}>
                {[0, 1, 2, 3].map(rank => [0, 1, 2, 3].map(file => (
                    <div key={`${file}-${rank}`} className={`tutorial-square ${(rank + file) % 2 === 1 ? 'black-square' : 'white-square'}`} />
                )))}
                {selected && <HighlightSquare file={selected.file} rank={selected.rank} color="rgba(255, 255, 0, 0.5)" />}
                {legalMoves.map((m, i) => <LegalMoveDot key={i} file={m.file} rank={m.rank} />)}
                {pieces.map(p => (
                    <Piece key={p.id} piece={p.type} file={p.file} rank={p.rank} 
                           onDragStartCallback={handlePieceDragStart} onDropCallback={handlePieceDrop}
                           className={p.id === warpPieceId ? 'drop-warp' : ''} />
                ))}
                
                {pocketingPiece && (
                    <div 
                        className="pocketing-animation"
                        style={{
                            left: `${pocketingPiece.file * 25}%`,
                            top: `${pocketingPiece.rank * 25}%`,
                            backgroundImage: `url("/images/pieces/${pocketingPiece.type}.png")`
                        }}
                    />
                )}
                <Confetti trigger={completed && !hasPlayedConfetti.current} />
            </div>
            
            <div className="reserve-tray" style={{ position: 'relative' }}>
                {pocketArrival && <div className="pocket-flare"></div>}
                <h4>Your Reserve</h4>
                <div className="reserve-slots">
                    {reserve.map((type, i) => (
                        <div key={i} 
                             className={`reserve-piece ${selectedReserve === i ? 'selected' : ''}`}
                             onClick={() => {
                                 setSelectedReserve(i);
                                 setMessage("Piece selected from reserve. Now click any empty square on the board!");
                             }}
                             style={{ backgroundImage: `url("/images/pieces/${type}.png")` }}
                        />
                    ))}
                    {reserve.length === 0 && <span className="empty-hint">Tray Empty</span>}
                </div>
            </div>

            <div className="tutorial-controls">
                <p>{message}</p>
                {completed && <button onClick={reset}>Reset Tutorial</button>}
            </div>
        </div>
    );
}

export default CrazyhouseTutorialBoard;
