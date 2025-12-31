import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import Piece from '../Pieces/Piece';
import LegalMoveDot from '../LegalMoveDot/LegalMoveDot';
import HighlightSquare from '../HighlightSquare/HighlightSquare';
import './Rules.css';

const VARIANT_RULES = {
    standard: {
        title: "Standard Chess",
        description: "The classic game of strategy.",
        rules: [
            "Checkmate the opponent's king to win.",
            "Stalemate is a draw.",
            "Standard piece movements apply."
        ]
    },
    antichess: {
        title: "Antichess",
        description: "Lose all your pieces to win.",
        rules: [
            "Capturing is mandatory.",
            "If multiple captures are available, you may choose which to make.",
            "The king has no special status (it can be captured).",
            "You win by losing all your pieces or being stalemated."
        ]
    },
    atomic: {
        title: "Atomic Chess",
        description: "Every capture is an explosion.",
        rules: [
            "When a piece is captured, an explosion occurs on the captured square.",
            "The explosion removes the capturing piece, the captured piece, and all non-pawn pieces in the surrounding 3x3 area.",
            "Pawns are only removed if they are directly involved in the capture.",
            "A player wins by exploding the opponent's king or by traditional checkmate.",
            "Kings cannot capture pieces because they would explode."
        ]
    },
    crazyhouse: {
        title: "Crazyhouse",
        description: "Captured pieces join your side.",
        rules: [
            "When you capture an opponent's piece, it is added to your reserve (in your color).",
            "On any turn, instead of moving a piece, you may 'drop' a piece from your reserve onto any empty square.",
            "Pawns cannot be dropped on the 1st or 8th ranks.",
            "A pawn dropped on the 2nd rank retains its double-move ability."
        ]
    },
    horde: {
        title: "Horde Chess",
        description: "A pawn army vs. standard pieces.",
        rules: [
            "White has 36 pawns and no other pieces.",
            "Black has a standard set of pieces.",
            "White wins by checkmating the Black king.",
            "Black wins by capturing all of White's pawns (and any promoted pieces)."
        ]
    },
    king_of_the_hill: {
        title: "King of the Hill",
        description: "Race your king to the center.",
        rules: [
            "In addition to standard checkmate, a player can win by moving their king to one of the four center squares: e4, d4, e5, or d5.",
            "The first player to reach the center wins immediately."
        ]
    },
    racing_kings: {
        title: "Racing Kings",
        description: "A race to the finish line.",
        rules: [
            "The goal is to reach the 8th rank with your king.",
            "If White reaches the 8th rank first, Black has one last turn to also reach the 8th rank, resulting in a draw.",
            "Checks are illegal. You cannot move into check, and you cannot deliver a check."
        ]
    },
    three_check: {
        title: "Three-Check",
        description: "Check the king three times to win.",
        rules: [
            "A player wins by checking the opponent's king three times.",
            "Standard checkmate also ends the game.",
            "The game status shows how many checks each player has delivered."
        ]
    },
    chess960: {
        title: "Chess960 (Fischer Random)",
        description: "Randomized starting positions.",
        rules: [
            "The starting position of the pieces is randomized on the first rank.",
            "Bishops must be on opposite colors.",
            "The king must be between the two rooks.",
            "Castling rules are the same as standard chess, but the king and rook end up on the same squares as in standard castling (c1/g1 for White, c8/g8 for Black)."
        ]
    }
};

function AtomicTutorialBoard() {
    const [pieces, setPieces] = useState([
        { id: 'wk', type: 'N', color: 'w', file: 1, rank: 3 }, // Knight at b1 (relative to 4x4)
        { id: 'bp', type: 'p', color: 'b', file: 2, rank: 1 }, // Pawn at c3 (relative to 4x4)
        { id: 'bp2', type: 'p', color: 'b', file: 1, rank: 1 }, // Pawn at b3 - will survive
        { id: 'bp3', type: 'p', color: 'b', file: 3, rank: 1 }, // Pawn at d3 - will survive
        { id: 'br', type: 'r', color: 'b', file: 1, rank: 0 }, // Rook at b4 - will explode
        { id: 'bq', type: 'q', color: 'b', file: 3, rank: 0 }, // Queen at d4 - will explode
        { id: 'bk', type: 'k', color: 'b', file: 2, rank: 0 }, // King at c4 - will explode
    ]);
    const [explosion, setExplosion] = useState(null);
    const [message, setMessage] = useState("Drag or click the White Knight to capture the middle Black Pawn!");
    const [completed, setCompleted] = useState(false);
    const [selected, setSelected] = useState(null); // { file, rank }
    const [legalMoves, setLegalMoves] = useState([]);
    const [isFlying, setIsFlying] = useState(false);
    const [isShaking, setIsShaking] = useState(false);
    const boardRef = useRef(null);

    const getSquareFromCoords = (clientX, clientY) => {
        if (!boardRef.current) return null;
        const rect = boardRef.current.getBoundingClientRect();
        const x = clientX - rect.left;
        const y = clientY - rect.top;
        const squareSize = rect.width / 4;
        
        const file = Math.floor(x / squareSize);
        const rank = Math.floor(y / squareSize);
        
        if (file >= 0 && file < 4 && rank >= 0 && rank < 4) {
            return { file, rank };
        }
        return null;
    };

    const calculateLegalMoves = (file, rank) => {
        const moves = [];
        const offsets = [[1, 2], [1, -2], [-1, 2], [-1, -2], [2, 1], [2, -1], [-2, 1], [-2, -1]];
        
        offsets.forEach(([dx, dy]) => {
            const newFile = file + dx;
            const newRank = rank + dy;
            
            if (newFile >= 0 && newFile < 4 && newRank >= 0 && newRank < 4) {
                moves.push({ file: newFile, rank: newRank });
            }
        });
        return moves;
    };

    const executeMove = (targetFile, targetRank) => {
         const knight = pieces.find(p => p.id === 'wk');
         if (!knight) return;

         const dx = Math.abs(targetFile - knight.file);
         const dy = Math.abs(targetRank - knight.rank);
         const isKnightMove = (dx === 1 && dy === 2) || (dx === 2 && dy === 1);

         if (!isKnightMove) {
             setMessage("That's not a valid Knight move!");
             setSelected(null);
             setLegalMoves([]);
             return;
         }

         const targetPiece = pieces.find(p => p.file === targetFile && p.rank === targetRank);
         
         if (targetPiece && targetPiece.color === 'b') {
            setMessage("Incoming atom bomb!");
            
            setIsFlying(true);
            setSelected(null);
            setLegalMoves([]);
            
            // 1. Move the knight in state to trigger CSS transition
            setPieces(prev => prev.map(p => p.id === 'wk' ? { ...p, file: targetFile, rank: targetRank } : p));

            // 2. Wait for flight animation to finish (0.4s)
            setTimeout(() => {
                setIsFlying(false);
                setIsShaking(true);
                setExplosion({ file: targetFile, rank: targetRank });

                // Remove pieces immediately after impact
                setPieces(prev => prev.filter(p => {
                    const pdx = Math.abs(p.file - targetFile);
                    const pdy = Math.abs(p.rank - targetRank);
                    
                    if (p.id === 'wk') return false; 
                    if (p.file === targetFile && p.rank === targetRank) return false;
                    
                    if (pdx <= 1 && pdy <= 1) {
                        if (p.type === 'p') return true; 
                        return false; 
                    }
                    return true;
                }));

                // Clear shake after a moment
                setTimeout(() => setIsShaking(false), 300);

                // Clear explosion after its animation (0.8s)
                setTimeout(() => {
                    setExplosion(null);
                    setCompleted(true);
                    setMessage("Notice: The Knight, King, and other pieces exploded. The side Pawns survived!");
                }, 800);
            }, 500);
         } else {
             setMessage("Move to capture the middle Black Pawn to see the explosion!");
             setPieces(prev => prev.map(p => p.id === 'wk' ? { ...p, file: targetFile, rank: targetRank } : p));
             setSelected(null);
             setLegalMoves([]);
         }
    };

    const handleBoardClick = (e) => {
        if (completed || explosion || isFlying || isShaking) return;
        const sq = getSquareFromCoords(e.clientX, e.clientY);
        if (!sq) return;

        const clickedPiece = pieces.find(p => p.file === sq.file && p.rank === sq.rank);

        // Select own piece (Knight)
        if (clickedPiece && clickedPiece.id === 'wk') {
            setSelected(sq);
            setLegalMoves(calculateLegalMoves(sq.file, sq.rank));
            setMessage("Knight selected. Drag or click the middle Black Pawn!");
            return;
        }

        // Move if selected
        if (selected) {
            const isLegal = legalMoves.some(m => m.file === sq.file && m.rank === sq.rank);
            if (isLegal) {
                executeMove(sq.file, sq.rank);
            } else {
                setSelected(null);
                setLegalMoves([]);
            }
        }
    };

    const handlePieceDragStart = ({ file, rank, piece }) => {
        if (completed || explosion || isFlying || isShaking) return;
        // piece is "N" (White Knight type)
        if (piece !== 'N') return; 

        setSelected({ file, rank });
        setLegalMoves(calculateLegalMoves(file, rank));
    };

    const handlePieceDrop = ({ clientX, clientY }) => {
        if (completed || explosion || isFlying || isShaking) return;
        const sq = getSquareFromCoords(clientX, clientY);
        
        if (sq && selected) {
             const isLegal = legalMoves.some(m => m.file === sq.file && m.rank === sq.rank);
             if (isLegal) {
                 executeMove(sq.file, sq.rank);
             }
        }
    };

    const reset = () => {
        setPieces([
            { id: 'wk', type: 'N', color: 'w', file: 1, rank: 3 },
            { id: 'bp', type: 'p', color: 'b', file: 2, rank: 1 },
            { id: 'bp2', type: 'p', color: 'b', file: 1, rank: 1 },
            { id: 'bp3', type: 'p', color: 'b', file: 3, rank: 1 },
            { id: 'br', type: 'r', color: 'b', file: 1, rank: 0 },
            { id: 'bq', type: 'q', color: 'b', file: 3, rank: 0 },
            { id: 'bk', type: 'k', color: 'b', file: 2, rank: 0 },
        ]);
        setExplosion(null);
        setCompleted(false);
        setSelected(null);
        setLegalMoves([]);
        setIsFlying(false);
        setIsShaking(false);
        setMessage("Drag or click the middle Black Pawn!");
    };

    return (
        <div className="atomic-tutorial">
            <div 
                className={`tutorial-board ${isShaking ? 'shaking' : ''}`}
                ref={boardRef}
                onClick={handleBoardClick}
            >
                {/* Board Squares */}
                {[0, 1, 2, 3].map(rank => (
                    [0, 1, 2, 3].map(file => {
                        const isBlack = (rank + file) % 2 === 1;
                        return (
                            <div 
                                key={`${file}-${rank}`}
                                className={`tutorial-square ${isBlack ? 'black-square' : 'white-square'}`}
                            />
                        );
                    })
                ))}
                
                {/* Highlight Selected Square */}
                {selected && (
                    <HighlightSquare 
                        file={selected.file} 
                        rank={selected.rank} 
                        color="rgba(255, 255, 0, 0.5)" 
                    />
                )}

                {/* Legal Move Dots */}
                {legalMoves.map((m, i) => (
                    <LegalMoveDot key={i} file={m.file} rank={m.rank} />
                ))}

                {/* Pieces */}
                {pieces.map(p => (
                    <Piece
                        key={p.id}
                        piece={p.type}
                        file={p.file}
                        rank={p.rank}
                        onDragStartCallback={handlePieceDragStart}
                        onDropCallback={handlePieceDrop}
                        className={p.id === 'wk' && isFlying ? 'flying-knight' : ''}
                    />
                ))}

                {/* Explosion */}
                {explosion && (
                    <div 
                        className="explosion-container"
                        style={{
                            left: `${explosion.file * 25}%`,
                            top: `${explosion.rank * 25}%`,
                            width: '25%',
                            height: '25%'
                        }}
                    >
                        <div className="explosion-ring"></div>
                        <div className="explosion-ring"></div>
                        <div className="explosion-ring"></div>
                    </div>
                )}
            </div>
            <div className="tutorial-controls">
                <p>{message}</p>
                {completed && <button onClick={reset}>Reset Tutorial</button>}
            </div>
        </div>
    );
}

function AntichessTutorialBoard() {
    const [pieces, setPieces] = useState([
        { id: 'wp', type: 'P', color: 'w', file: 1, rank: 2 }, // White Pawn at b2
        { id: 'bn', type: 'n', color: 'b', file: 2, rank: 1 }, // Black Knight at c3
    ]);
    const [message, setMessage] = useState("In Antichess, captures are mandatory! Try to move or capture.");
    const [completed, setCompleted] = useState(false);
    const [selected, setSelected] = useState(null);
    const [legalMoves, setLegalMoves] = useState([]);
    const boardRef = useRef(null);

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
            // In this setup, only capture is legal
            setLegalMoves([{ file: 2, rank: 1 }]); 
            setMessage("You MUST capture the Knight! Moving forward is illegal here.");
            return;
        }

        if (selected && sq.file === 2 && sq.rank === 1) {
            // Execute capture
            setPieces(prev => prev.filter(p => p.color === 'w').map(p => 
                p.id === 'wp' ? { ...p, file: 2, rank: 1 } : p
            ).filter(p => p.id === 'wp')); // Remove black knight
            
            // In Antichess, pieces are just removed. But we'll keep the capturing piece for the visual.
            // Wait, actually in the tutorial let's just show the capture.
            setPieces([{ id: 'wp', type: 'P', color: 'w', file: 2, rank: 1 }]);
            setSelected(null);
            setLegalMoves([]);
            setCompleted(true);
            setMessage("Great! You made the mandatory capture. Lose all your pieces to win!");
        } else {
            setSelected(null);
            setLegalMoves([]);
        }
    };

    const handlePieceDragStart = ({ file, rank, piece }) => {
        if (completed) return;
        if (piece !== 'P') return;
        setSelected({ file, rank });
        setLegalMoves([{ file: 2, rank: 1 }]);
    };

    const handlePieceDrop = ({ clientX, clientY }) => {
        if (completed) return;
        const sq = getSquareFromCoords(clientX, clientY);
        if (sq && sq.file === 2 && sq.rank === 1) {
            setPieces([{ id: 'wp', type: 'P', color: 'w', file: 2, rank: 1 }]);
            setSelected(null);
            setLegalMoves([]);
            setCompleted(true);
            setMessage("Great! You made the mandatory capture. Lose all your pieces to win!");
        }
    };

    const reset = () => {
        setPieces([
            { id: 'wp', type: 'P', color: 'w', file: 1, rank: 2 },
            { id: 'bn', type: 'n', color: 'b', file: 2, rank: 1 },
        ]);
        setCompleted(false);
        setSelected(null);
        setLegalMoves([]);
        setMessage("In Antichess, captures are mandatory! Try to move or capture.");
    };

    return (
        <div className="antichess-tutorial">
            <div className="tutorial-board" ref={boardRef} onClick={handleBoardClick}>
                {[0, 1, 2, 3].map(rank => [0, 1, 2, 3].map(file => (
                    <div key={`${file}-${rank}`} className={`tutorial-square ${(rank + file) % 2 === 1 ? 'black-square' : 'white-square'}`} />
                )))}
                {selected && <HighlightSquare file={selected.file} rank={selected.rank} color="rgba(255, 255, 0, 0.5)" />}
                {legalMoves.map((m, i) => <LegalMoveDot key={i} file={m.file} rank={m.rank} />)}
                {pieces.map(p => (
                    <Piece key={p.id} piece={p.type} file={p.file} rank={p.rank} 
                           onDragStartCallback={handlePieceDragStart} onDropCallback={handlePieceDrop} />
                ))}
            </div>
            <div className="tutorial-controls">
                <p>{message}</p>
                {completed && <button onClick={reset}>Reset Tutorial</button>}
            </div>
        </div>
    );
}

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
    const boardRef = useRef(null);

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

        // Handling Drops
        if (selectedReserve !== null) {
            const isOccupied = pieces.some(p => p.file === sq.file && p.rank === sq.rank);
            if (!isOccupied) {
                const type = reserve[selectedReserve];
                const newPiece = { id: `drop-${Date.now()}`, type, color: 'w', file: sq.file, rank: sq.rank };
                setPieces(prev => [...prev, newPiece]);
                setReserve(prev => prev.filter((_, i) => i !== selectedReserve));
                setSelectedReserve(null);
                setCompleted(true);
                setMessage("Excellent! You dropped a piece from your reserve onto the board. This is the heart of Crazyhouse!");
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
            setPieces(prev => prev.filter(p => p.id !== 'bb').map(p => 
                p.id === 'wr' ? { ...p, file: 2, rank: 1 } : p
            ));
            setReserve(['B']);
            setSelected(null);
            setLegalMoves([]);
            setMessage("Bishop captured! It's now in your reserve. Click it in the tray, then click an empty square to drop it!");
        } else {
            setSelected(null);
            setLegalMoves([]);
        }
    };

    const handlePieceDragStart = ({ file, rank, piece }) => {
        if (completed) return;
        if (piece !== 'R') return;
        setSelected({ file, rank });
        setLegalMoves([{ file: 2, rank: 1 }]);
    };

    const handlePieceDrop = ({ clientX, clientY }) => {
        if (completed) return;
        const sq = getSquareFromCoords(clientX, clientY);
        if (sq && sq.file === 2 && sq.rank === 1) {
            setPieces(prev => prev.filter(p => p.id !== 'bb').map(p => 
                p.id === 'wr' ? { ...p, file: 2, rank: 1 } : p
            ));
            setReserve(['B']);
            setSelected(null);
            setLegalMoves([]);
            setMessage("Bishop captured! It's now in your reserve. Click it in the tray, then click an empty square to drop it!");
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
                           onDragStartCallback={handlePieceDragStart} onDropCallback={handlePieceDrop} />
                ))}
            </div>
            
            <div className="reserve-tray">
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

function KOTHTutorialBoard() {
    const [pieces, setPieces] = useState([
        { id: 'wk', type: 'K', color: 'w', file: 0, rank: 3 }, // White King at a1 (4x4)
        { id: 'bk', type: 'k', color: 'b', file: 3, rank: 0 }, // Black King at d4 (4x4)
    ]);
    const [message, setMessage] = useState("King of the Hill: Race your King to the center squares!");
    const [completed, setCompleted] = useState(false);
    const [selected, setSelected] = useState(null);
    const [legalMoves, setLegalMoves] = useState([]);
    const boardRef = useRef(null);

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
        if (completed) return;
        const sq = getSquareFromCoords(e.clientX, e.clientY);
        if (!sq) return;

        const clickedPiece = pieces.find(p => p.file === sq.file && p.rank === sq.rank);

        if (clickedPiece && clickedPiece.color === 'w') {
            setSelected(sq);
            // Simple King moves
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
                    setMessage("You reached the center! In King of the Hill, this is an instant victory.");
                } else {
                    setMessage("Good move! Now keep heading for the center squares.");
                }
            } else {
                setSelected(null);
                setLegalMoves([]);
            }
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
                if (nf >= 0 && nf < 4 && nr >= 0 && nr < 4) moves.push({ file: nf, rank: nr });
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
                const isCenter = centerSquares.some(c => c.file === sq.file && c.rank === sq.rank);
                setPieces(prev => prev.map(p => p.id === 'wk' ? { ...p, file: sq.file, rank: sq.rank } : p));
                setSelected(null);
                setLegalMoves([]);
                if (isCenter) {
                    setCompleted(true);
                    setMessage("You reached the center! In King of the Hill, this is an instant victory.");
                } else {
                    setMessage("Good move! Now keep heading for the center squares.");
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
        setSelected(null);
        setLegalMoves([]);
        setMessage("King of the Hill: Race your King to the center squares!");
    };

    return (
        <div className="koth-tutorial">
            <div className="tutorial-board" ref={boardRef} onClick={handleBoardClick}>
                {[0, 1, 2, 3].map(rank => [0, 1, 2, 3].map(file => (
                    <div key={`${file}-${rank}`} className={`tutorial-square ${(rank + file) % 2 === 1 ? 'black-square' : 'white-square'}`} />
                )))}
                {centerSquares.map((c, i) => (
                    <HighlightSquare key={i} file={c.file} rank={c.rank} color="rgba(255, 215, 0, 0.3)" />
                ))}
                {selected && <HighlightSquare file={selected.file} rank={selected.rank} color="rgba(255, 255, 0, 0.5)" />}
                {legalMoves.map((m, i) => <LegalMoveDot key={i} file={m.file} rank={m.rank} />)}
                {pieces.map(p => (
                    <Piece key={p.id} piece={p.type} file={p.file} rank={p.rank} 
                           onDragStartCallback={handlePieceDragStart} onDropCallback={handlePieceDrop} />
                ))}
            </div>
            <div className="tutorial-controls">
                <p>{message}</p>
                {completed && <button onClick={reset}>Reset Tutorial</button>}
            </div>
        </div>
    );
}

function RacingKingsTutorialBoard() {
    const [pieces, setPieces] = useState([
        { id: 'wk', type: 'K', color: 'w', file: 0, rank: 3 }, // White King at a1
        { id: 'br', type: 'r', color: 'b', file: 2, rank: 0 }, // Black Rook at c4 (controls file 2)
    ]);
    const [message, setMessage] = useState("Racing Kings: Race your King to the top! Note: Checks are ILLEGAL.");
    const [completed, setCompleted] = useState(false);
    const [selected, setSelected] = useState(null);
    const [legalMoves, setLegalMoves] = useState([]);
    const boardRef = useRef(null);

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
                setPieces(prev => prev.map(p => p.id === 'wk' ? { ...p, file: sq.file, rank: sq.rank } : p));
                setSelected(null);
                setLegalMoves([]);
                if (sq.rank === 0) {
                    setCompleted(true);
                    setMessage("You reached the top rank! You win the race. Remember, checks were never allowed!");
                } else {
                    setMessage("Good progress! Keep climbing, but stay out of the Rook's line of fire.");
                }
            } else if (sq.file === 2) {
                setMessage("Illegal Move! In Racing Kings, you cannot move into check.");
                setSelected(null);
                setLegalMoves([]);
            } else {
                setSelected(null);
                setLegalMoves([]);
            }
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
                setPieces(prev => prev.map(p => p.id === 'wk' ? { ...p, file: sq.file, rank: sq.rank } : p));
                setSelected(null);
                setLegalMoves([]);
                if (sq.rank === 0) {
                    setCompleted(true);
                    setMessage("You reached the top rank! You win the race. Remember, checks were never allowed!");
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
                             className={`tutorial-square ${(rank + file) % 2 === 1 ? 'black-square' : 'white-square'} ${isTarget ? 'target-row' : ''} ${isDanger ? 'danger-line' : ''}`} 
                        />
                    );
                }))}
                {selected && <HighlightSquare file={selected.file} rank={selected.rank} color="rgba(255, 255, 0, 0.5)" />}
                {legalMoves.map((m, i) => <LegalMoveDot key={i} file={m.file} rank={m.rank} />)}
                {pieces.map(p => (
                    <Piece key={p.id} piece={p.type} file={p.file} rank={p.rank} 
                           onDragStartCallback={handlePieceDragStart} onDropCallback={handlePieceDrop} />
                ))}
            </div>
            <div className="tutorial-controls">
                <p>{message}</p>
                {completed && <button onClick={reset}>Reset Tutorial</button>}
            </div>
        </div>
    );
}

function HordeTutorialBoard() {
    const [pieces, setPieces] = useState([
        { id: 'wp1', type: 'P', color: 'w', file: 0, rank: 3 },
        { id: 'wp2', type: 'P', color: 'w', file: 1, rank: 3 },
        { id: 'wp3', type: 'P', color: 'w', file: 2, rank: 3 },
        { id: 'wp4', type: 'P', color: 'w', file: 3, rank: 3 },
        { id: 'wp5', type: 'P', color: 'w', file: 0, rank: 2 },
        { id: 'wp6', type: 'P', color: 'w', file: 1, rank: 2 },
        { id: 'wp7', type: 'P', color: 'w', file: 2, rank: 2 },
        { id: 'wp8', type: 'P', color: 'w', file: 3, rank: 2 },
        { id: 'br', type: 'r', color: 'b', file: 1, rank: 0 },
    ]);
    const [message, setMessage] = useState("Horde: Use your pawn army to overwhelm the Black pieces!");
    const [completed, setCompleted] = useState(false);
    const [selected, setSelected] = useState(null);
    const [legalMoves, setLegalMoves] = useState([]);
    const boardRef = useRef(null);

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
            // Allow 1 or 2 squares for rank 3, 1 for rank 2
            const moves = [];
            if (sq.rank === 3) {
                moves.push({ file: sq.file, rank: 2 }, { file: sq.file, rank: 1 });
            } else if (sq.rank === 2) {
                moves.push({ file: sq.file, rank: 1 });
            }
            // Add capture
            if (sq.rank === 1 && (sq.file === 0 || sq.file === 2)) {
                moves.push({ file: 1, rank: 0 });
            }
            setLegalMoves(moves);
            return;
        }

        if (selected) {
            const isLegal = legalMoves.some(m => m.file === sq.file && m.rank === sq.rank);
            if (isLegal) {
                const isCapture = sq.file === 1 && sq.rank === 0;
                setPieces(prev => prev.filter(p => !(p.file === sq.file && p.rank === sq.rank)).map(p => 
                    (p.file === selected.file && p.rank === selected.rank) ? { ...p, file: sq.file, rank: sq.rank } : p
                ));
                setSelected(null);
                setLegalMoves([]);
                if (isCapture) {
                    setCompleted(true);
                    setMessage("The Rook is captured! In Horde, White wins by capturing all Black pieces.");
                } else {
                    setMessage("The pawns advance! Keep pushing forward.");
                }
            } else {
                setSelected(null);
                setLegalMoves([]);
            }
        }
    };

    const handlePieceDragStart = ({ file, rank, piece }) => {
        if (completed) return;
        if (piece !== 'P') return;
        setSelected({ file, rank });
        const moves = [{ file, rank: rank - 1 }];
        if (rank === 3) moves.push({ file, rank: 1 });
        if (rank === 1 && (file === 0 || file === 2)) moves.push({ file: 1, rank: 0 });
        setLegalMoves(moves);
    };

    const handlePieceDrop = ({ clientX, clientY }) => {
        if (completed) return;
        const sq = getSquareFromCoords(clientX, clientY);
        if (sq && selected) {
            const isLegal = legalMoves.some(m => m.file === sq.file && m.rank === sq.rank);
            if (isLegal) {
                const isCapture = sq.file === 1 && sq.rank === 0;
                setPieces(prev => prev.filter(p => !(p.file === sq.file && p.rank === sq.rank)).map(p => 
                    (p.file === selected.file && p.rank === selected.rank) ? { ...p, file: sq.file, rank: sq.rank } : p
                ));
                setSelected(null);
                setLegalMoves([]);
                if (isCapture) {
                    setCompleted(true);
                    setMessage("The Rook is captured! In Horde, White wins by capturing all Black pieces.");
                } else {
                    setMessage("The pawns advance! Keep pushing forward.");
                }
            }
        }
    };

    const reset = () => {
        setPieces([
            { id: 'wp1', type: 'P', color: 'w', file: 0, rank: 3 },
            { id: 'wp2', type: 'P', color: 'w', file: 1, rank: 3 },
            { id: 'wp3', type: 'P', color: 'w', file: 2, rank: 3 },
            { id: 'wp4', type: 'P', color: 'w', file: 3, rank: 3 },
            { id: 'wp5', type: 'P', color: 'w', file: 0, rank: 2 },
            { id: 'wp6', type: 'P', color: 'w', file: 1, rank: 2 },
            { id: 'wp7', type: 'P', color: 'w', file: 2, rank: 2 },
            { id: 'wp8', type: 'P', color: 'w', file: 3, rank: 2 },
            { id: 'br', type: 'r', color: 'b', file: 1, rank: 0 },
        ]);
        setCompleted(false);
        setSelected(null);
        setLegalMoves([]);
        setMessage("Horde: Use your pawn army to overwhelm the Black pieces!");
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
                    <Piece key={p.id} piece={p.type} file={p.file} rank={p.rank} 
                           onDragStartCallback={handlePieceDragStart} onDropCallback={handlePieceDrop} />
                ))}
            </div>
            <div className="tutorial-controls">
                <p>{message}</p>
                {completed && <button onClick={reset}>Reset Tutorial</button>}
            </div>
        </div>
    );
}

function Rules() {
    const { variant } = useParams();
    const currentVariant = variant || 'standard';
    const variantData = VARIANT_RULES[currentVariant];

    const navigate = useNavigate();

    if (!variantData) {
        return (
            <div className="rules-container">
                <h1>Variant not found</h1>
                <Link to="/rules/standard">Back to Standard Rules</Link>
            </div>
        );
    }

    const handleVariantChange = (vId) => {
        navigate(`/rules/${vId}`);
    };

    return (
        <div className="rules-container">
            <div className="variant-select-container">
                <select 
                    value={currentVariant} 
                    onChange={(e) => handleVariantChange(e.target.value)}
                    className="variant-select-dropdown"
                >
                    {Object.keys(VARIANT_RULES).map(v => (
                        <option key={v} value={v}>
                            {VARIANT_RULES[v].title}
                        </option>
                    ))}
                </select>
            </div>
            <div className="rules-content">
                <h1>{variantData.title}</h1>
                <p className="variant-description">{variantData.description}</p>
                
                {currentVariant === 'atomic' && <AtomicTutorialBoard />}
                {currentVariant === 'antichess' && <AntichessTutorialBoard />}
                {currentVariant === 'crazyhouse' && <CrazyhouseTutorialBoard />}
                {currentVariant === 'king_of_the_hill' && <KOTHTutorialBoard />}
                {currentVariant === 'racing_kings' && <RacingKingsTutorialBoard />}
                {currentVariant === 'horde' && <HordeTutorialBoard />}

                <ul className="rules-list">
                    {variantData.rules.map((rule, index) => (
                        <li key={index}>{rule}</li>
                    ))}
                </ul>
                <div className="rules-actions">
                    <Link to={`/otb/${currentVariant}`} className="play-button">
                        Play {variantData.title}
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default Rules;
