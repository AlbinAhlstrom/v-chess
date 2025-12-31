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

function FlyingKnight({ file, rank, isPreparing, isFlying }) {
    const style = {
        left: `calc(${file} * 25%)`,
        top: `calc(${rank} * 25%)`,
        width: '25%',
        height: '25%',
        position: 'absolute',
        pointerEvents: 'none',
        zIndex: 1000,
        backgroundImage: 'url("/images/pieces/N.png")',
        backgroundSize: '100%'
    };

    let className = 'visceral-knight';
    if (isPreparing) className += ' preparing';
    if (isFlying) className += ' flying';

    return (
        <div className={className} style={style}>
            <div className="vk-inner">
                <div className="vk-front" style={{ backgroundImage: 'var(--piece-image)' }}></div>
                <div className="vk-back" style={{ backgroundImage: 'var(--piece-image)' }}></div>
            </div>
        </div>
    );
}

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
    const [isPreparing, setIsPreparing] = useState(false);
    const [isShaking, setIsShaking] = useState(false);
    const [isFlashing, setIsFlashing] = useState(false);
    const [isIgnition, setIsIgnition] = useState(false);
    const [scorchMark, setScorchMark] = useState(null); // { file, rank }
    const [animatingKnight, setAnimatingKnight] = useState(null); // { file, rank }
    const [launchPuff, setLaunchPuff] = useState(null); // { file, rank }
    const boardRef = useRef(null);
    const canvasRef = useRef(null);
    const explosionSound = useRef(new Audio("/sounds/atomic_explosion.mp3"));
    const launchSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/castle.mp3"));
    const lockSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/move-check.mp3"));

    // Particle System based on requested snippet
    useEffect(() => {
        if ((!explosion && !isIgnition) || !canvasRef.current || !boardRef.current) return;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        const rect = boardRef.current.getBoundingClientRect();
        
        // Match canvas resolution to board size
        canvas.width = rect.width;
        canvas.height = rect.height;

        const squareSize = rect.width / 4;
        
        // Setup for either explosion or ignition
        const originX = explosion 
            ? (explosion.file + 0.5) * squareSize 
            : (animatingKnight ? (animatingKnight.file + 0.5) * squareSize : 0);
        const originY = explosion 
            ? (explosion.rank + 0.5) * squareSize 
            : (animatingKnight ? (animatingKnight.rank + 0.5) * squareSize : 0);

        const config = explosion ? {
            particleNumber: 300,
            maxParticleSize: 5, // Reduced from 6 (-20%)
            maxSpeed: 10, // Reduced from 12 (-20%)
            colorVariation: 50
        } : {
            particleNumber: 100,
            maxParticleSize: 3,
            maxSpeed: 8,
            colorVariation: 30
        };

        const colorPalette = {
            matter: explosion ? [
                {r:36,g:18,b:42},   // darkPRPL
                {r:78,g:36,b:42},   // rockDust
                {r:252,g:178,b:96}, // solarFlare
                {r:253,g:238,b:152} // totesASun
            ] : [
                {r:255,g:200,b:0},  // fire
                {r:255,g:100,b:0},  // orange
                {r:255,g:255,b:255} // white spark
            ]
        };

        const getColor = (color) => {
            const r = Math.round(((Math.random() * config.colorVariation) - (config.colorVariation/2)) + color.r);
            const g = Math.round(((Math.random() * config.colorVariation) - (config.colorVariation/2)) + color.g);
            const b = Math.round(((Math.random() * config.colorVariation) - (config.colorVariation/2)) + color.b);
            return { r, g, b };
        };

        class Particle {
            constructor(x, y) {
                // Add vibration to origin for ignition
                this.x = explosion ? x : x + (Math.random() - 0.5) * 10;
                this.y = explosion ? y : y + (Math.random() - 0.5) * 10;
                this.r = Math.ceil(Math.random() * config.maxParticleSize);
                const baseColor = getColor(colorPalette.matter[Math.floor(Math.random() * colorPalette.matter.length)]);
                this.colorBase = `${baseColor.r},${baseColor.g},${baseColor.b}`;
                this.s = Math.pow(Math.ceil(Math.random() * config.maxSpeed), 0.7);
                this.d = Math.random() * Math.PI * 2;
                this.alpha = Math.random() * 0.5 + 0.5;
            }
            update() {
                this.x += Math.cos(this.d) * this.s;
                this.y += Math.sin(this.d) * this.s;
                this.s *= explosion ? 0.96 : 0.92;
                this.alpha -= explosion ? 0.015 : 0.04;
            }
            draw() {
                if (this.alpha <= 0) return;
                ctx.beginPath();
                ctx.fillStyle = `rgba(${this.colorBase},${this.alpha})`;
                ctx.arc(this.x, this.y, this.r, 0, 2 * Math.PI, false);
                ctx.fill();
                ctx.closePath();
            }
        }

        class Debris {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.size = Math.random() * 12 + 4; // Reduced from 15+5 (-20%)
                this.s = Math.random() * 2.4 + 0.8; // Reduced from 3+1 (-20%)
                this.d = Math.random() * Math.PI * 2;
                this.alpha = 0.6;
            }
            update() {
                this.x += Math.cos(this.d) * this.s;
                this.y += Math.sin(this.d) * this.s;
                this.s *= 0.98;
                this.alpha -= 0.008;
                this.size += 0.16;
            }
            draw() {
                if (this.alpha <= 0) return;
                ctx.beginPath();
                ctx.fillStyle = `rgba(60, 60, 60, ${this.alpha})`;
                ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI, false);
                ctx.fill();
                ctx.closePath();
            }
        }

        const particles = Array.from({ length: config.particleNumber }, () => new Particle(originX, originY));
        const smoke = explosion ? Array.from({ length: 40 }, () => new Debris(originX, originY)) : [];

        let animationFrame;
        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            smoke.forEach(s => {
                s.update();
                s.draw();
            });
            particles.forEach(p => {
                p.update();
                p.draw();
            });
            animationFrame = requestAnimationFrame(animate);
        };

        animate();
        return () => cancelAnimationFrame(animationFrame);
    }, [explosion, isIgnition, animatingKnight]);

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
            setMessage("Preparing for launch...");
            
            // Start sequence
            setAnimatingKnight({ file: knight.file, rank: knight.rank });
            setPieces(prev => prev.filter(p => p.id !== 'wk')); // Remove original knight immediately
            setIsPreparing(true);
            setIsIgnition(true);
            setIsFlashing(true); // Start fade immediately at very start of anim sequence
            setSelected(null);
            setLegalMoves([]);

            // Phase 1: Tilt in place (250ms)
            setTimeout(() => {
                setIsPreparing(false);
                setIsIgnition(false);
                setIsFlying(true);
                setAnimatingKnight({ file: targetFile, rank: targetRank }); // Set destination for CSS transition
                launchSound.current.play().catch(() => {});
                
                // Triple beep sequence
                const playBeep = () => {
                    lockSound.current.currentTime = 0;
                    lockSound.current.play().catch(() => {});
                };
                
                setTimeout(playBeep, 50);
                setTimeout(playBeep, 150);
                setTimeout(playBeep, 250);

                setMessage("Incoming atom bomb!");
                
                // Clear puff after 1s
                setTimeout(() => setLaunchPuff(null), 1000);
                setLaunchPuff({ file: knight.file, rank: knight.rank }); // <-- This line is added in replace

                // Wait for flight animation to finish (0.4s)
                setTimeout(() => {
                    setIsFlying(false);
                    setIsFlashing(false); // Stop flashing on impact
                    setAnimatingKnight(null); // Clear animating knight
                    setIsShaking(true);
                    explosionSound.current.play().catch(() => {});
                    setExplosion({ file: targetFile, rank: targetRank });
                    setScorchMark({ file: targetFile, rank: targetRank });

                    setPieces(prev => prev.filter(p => {
                        const pdx = Math.abs(p.file - targetFile);
                        const pdy = Math.abs(p.rank - targetRank);
                        
                        if (p.file === targetFile && p.rank === targetRank) return false;
                        
                        if (pdx <= 1 && pdy <= 1) {
                            if (p.type === 'p') return true; 
                            return false; 
                        }
                        return true;
                    }));

                    setTimeout(() => setIsShaking(false), 300);

                    setTimeout(() => {
                        setExplosion(null);
                        setCompleted(true);
                        setMessage("Notice: The Knight, King, and other pieces exploded. The side Pawns survived!");
                    }, 800);
                }, 400);
            }, 250);
         } else {
             setMessage("Move to capture the middle Black Pawn to see the explosion!");
             setPieces(prev => prev.map(p => p.id === 'wk' ? { ...p, file: targetFile, rank: targetRank } : p));
             setSelected(null);
             setLegalMoves([]);
         }
    };

    const handleBoardClick = (e) => {
        if (completed || explosion || isFlying || isShaking || isPreparing) return;
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
        } else if (clickedPiece && clickedPiece.color === 'b') {
            // Ignore clicks on black pieces if nothing is selected to avoid resetting instructions
            return;
        } else {
            setSelected(null);
            setLegalMoves([]);
        }
    };

    const handlePieceDragStart = ({ file, rank, piece }) => {
        if (completed || explosion || isFlying || isShaking || isPreparing) return;
        // piece is "N" (White Knight type)
        if (piece !== 'N') return; 

        setSelected({ file, rank });
        setLegalMoves(calculateLegalMoves(file, rank));
    };

    const handlePieceDrop = ({ clientX, clientY }) => {
        if (completed || explosion || isFlying || isShaking || isPreparing) return;
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
        setIsPreparing(false);
        setIsShaking(false);
        setIsFlashing(false);
        setAnimatingKnight(null);
        setScorchMark(null);
        setLaunchPuff(null);
        setMessage("Drag or click the White Knight to capture the middle Black Pawn!");
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
                        const isTarget = file === 2 && rank === 1;
                        return (
                            <div 
                                key={`${file}-${rank}`}
                                className={`tutorial-square ${isBlack ? 'black-square' : 'white-square'} ${isTarget && isFlashing ? 'target-flash' : ''}`}
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

                {/* Scorch Mark */}
                {scorchMark && (
                    <div 
                        className="scorch-mark"
                        style={{
                            left: `${scorchMark.file * 25}%`,
                            top: `${scorchMark.rank * 25}%`,
                        }}
                    />
                )}

                {/* Launch Puff */}
                {launchPuff && (
                    <div 
                        className="launch-puff"
                        style={{
                            left: `${launchPuff.file * 25}%`,
                            top: `${launchPuff.rank * 25}%`,
                        }}
                    />
                )}

                {/* Static Pieces */}
                {pieces.map(p => (
                    <Piece
                        key={p.id}
                        piece={p.type}
                        file={p.file}
                        rank={p.rank}
                        onDragStartCallback={handlePieceDragStart}
                        onDropCallback={handlePieceDrop}
                    />
                ))}

                {/* Animated Flying Knight */}
                {animatingKnight && (
                    <FlyingKnight 
                        file={animatingKnight.file} 
                        rank={animatingKnight.rank} 
                        isPreparing={isPreparing} 
                        isFlying={isFlying} 
                    />
                )}

                {/* Combined Explosion Effects */}
                {explosion && (
                    <>
                        <div 
                            className="mushroom-cloud-container"
                            style={{
                                left: `${explosion.file * 25}%`,
                                top: `${explosion.rank * 25}%`,
                            }}
                        >
                            <div className="mushroom-cloud cloud-1"></div>
                            <div className="mushroom-cloud cloud-2"></div>
                            <div className="explosion-flash"></div>
                        </div>
                        <canvas ref={canvasRef} className="explosion-canvas" />
                    </>
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
    const [shatter, setShatter] = useState(null); // { file, rank }
    const [isShaking, setIsShaking] = useState(false);
    const boardRef = useRef(null);
    const canvasRef = useRef(null);
    const shatterSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/capture.mp3"));

    useEffect(() => {
        if (!shatter || !canvasRef.current || !boardRef.current) return;
        shatterSound.current.play().catch(() => {});

        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        const rect = boardRef.current.getBoundingClientRect();
        canvas.width = rect.width;
        canvas.height = rect.height;

        const squareSize = rect.width / 4;
        const centerX = (shatter.file + 0.5) * squareSize;
        const centerY = (shatter.rank + 0.5) * squareSize;

        class Shard {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.size = Math.random() * 8 + 4;
                this.s = Math.random() * 5 + 2;
                this.d = Math.random() * Math.PI * 2;
                this.rot = Math.random() * Math.PI * 2;
                this.rotS = (Math.random() - 0.5) * 0.2;
                this.color = Math.random() > 0.5 ? '#fff' : '#ccc';
                this.opacity = 1;
            }
            update() {
                this.x += Math.cos(this.d) * this.s;
                this.y += Math.sin(this.d) * this.s;
                this.s *= 0.95;
                this.rot += this.rotS;
                this.opacity -= 0.02;
            }
            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.rot);
                ctx.globalAlpha = Math.max(0, this.opacity);
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.moveTo(0, -this.size / 2);
                ctx.lineTo(this.size / 2, this.size / 2);
                ctx.lineTo(-this.size / 2, this.size / 2);
                ctx.closePath();
                ctx.fill();
                ctx.restore();
            }
        }

        const shards = Array.from({ length: 20 }, () => new Shard(centerX, centerY));

        let animationFrame;
        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            shards.forEach(s => {
                s.update();
                s.draw();
            });
            if (shards.some(s => s.opacity > 0)) {
                animationFrame = requestAnimationFrame(animate);
            } else {
                setShatter(null);
            }
        };

        animate();
        return () => cancelAnimationFrame(animationFrame);
    }, [shatter]);

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
        if (completed || shatter || isShaking) return;
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
            setPieces([{ id: 'wp', type: 'P', color: 'w', file: 2, rank: 1 }]);
            setShatter({ file: 2, rank: 1 });
            setIsShaking(true);
            setTimeout(() => setIsShaking(false), 300);
            setSelected(null);
            setLegalMoves([]);
            setCompleted(true);
            setMessage("Great! You made the mandatory capture. Lose all your pieces to win!");
        } else if (clickedPiece && clickedPiece.color === 'b') {
            return;
        } else {
            setSelected(null);
            setLegalMoves([]);
        }
    };

    const handlePieceDragStart = ({ file, rank, piece }) => {
        if (completed || shatter || isShaking) return;
        if (piece !== 'P') return;
        setSelected({ file, rank });
        setLegalMoves([{ file: 2, rank: 1 }]);
    };

    const handlePieceDrop = ({ clientX, clientY }) => {
        if (completed || shatter || isShaking) return;
        const sq = getSquareFromCoords(clientX, clientY);
        if (sq && sq.file === 2 && sq.rank === 1) {
            setPieces([{ id: 'wp', type: 'P', color: 'w', file: 2, rank: 1 }]);
            setShatter({ file: 2, rank: 1 });
            setIsShaking(true);
            setTimeout(() => setIsShaking(false), 300);
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
        setShatter(null);
        setIsShaking(false);
        setMessage("In Antichess, captures are mandatory! Try to move or capture.");
    };

    return (
        <div className="antichess-tutorial">
            <div className={`tutorial-board ${isShaking ? 'shaking' : ''}`} ref={boardRef} onClick={handleBoardClick}>
                {[0, 1, 2, 3].map(rank => [0, 1, 2, 3].map(file => (
                    <div key={`${file}-${rank}`} className={`tutorial-square ${(rank + file) % 2 === 1 ? 'black-square' : 'white-square'}`} />
                )))}
                {selected && <HighlightSquare file={selected.file} rank={selected.rank} color="rgba(255, 255, 0, 0.5)" />}
                {legalMoves.map((m, i) => <LegalMoveDot key={i} file={m.file} rank={m.rank} />)}
                {pieces.map(p => (
                    <Piece key={p.id} piece={p.type} file={p.file} rank={p.rank} 
                           onDragStartCallback={handlePieceDragStart} onDropCallback={handlePieceDrop} />
                ))}
                {shatter && <canvas ref={canvasRef} className="explosion-canvas" />}
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
    const [warpPieceId, setWarpPieceId] = useState(null); // ID of piece to animate drop
    const boardRef = useRef(null);
    const captureSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/capture.mp3"));
    const dropSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/premove.mp3"));

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
                const dropId = `drop-${Date.now()}`;
                const newPiece = { id: dropId, type, color: 'w', file: sq.file, rank: sq.rank };
                setPieces(prev => [...prev, newPiece]);
                setReserve(prev => prev.filter((_, i) => i !== selectedReserve));
                setSelectedReserve(null);
                setWarpPieceId(dropId);
                setCompleted(true);
                dropSound.current.play().catch(() => {});
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
            setPieces(prev => prev.filter(p => p.id !== 'bb').map(p => 
                p.id === 'wr' ? { ...p, file: 2, rank: 1 } : p
            ));
            setReserve(['B']);
            setSelected(null);
            setLegalMoves([]);
            captureSound.current.play().catch(() => {});
            setMessage("Bishop captured! It's now in your reserve. Click it in the tray, then click an empty square to drop it!");
        } else if (clickedPiece && clickedPiece.color === 'b') {
            return;
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
            captureSound.current.play().catch(() => {});
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
                           onDragStartCallback={handlePieceDragStart} onDropCallback={handlePieceDrop}
                           className={p.id === warpPieceId ? 'drop-warp' : ''} />
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
    const [victoryAura, setVictoryAura] = useState(false);
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
                    if (nf >= 0 && nf < 4 && nr >= 0 && nr < 4) moves.push({ file: nf, nr });
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
                    setMessage("You reached the center! In King of the Hill, this is an instant victory.");
                } else {
                    setMessage("Good move! Now keep heading for the center squares.");
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
                    setVictoryAura(true);
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
        setVictoryAura(false);
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
                           onDragStartCallback={handlePieceDragStart} onDropCallback={handlePieceDrop}
                           className={p.id === 'wk' && victoryAura ? 'koth-aura' : ''} />
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
    const [turboTrail, setTurboTrail] = useState(null); // { file, rank }
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
                const oldPos = { file: selected.file, rank: selected.rank };
                setPieces(prev => prev.map(p => p.id === 'wk' ? { ...p, file: sq.file, rank: sq.rank } : p));
                setTurboTrail(oldPos);
                setSelected(null);
                setLegalMoves([]);
                
                setTimeout(() => setTurboTrail(null), 500);

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
                
                setTimeout(() => setTurboTrail(null), 500);

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
                             className={`tutorial-square ${(rank + file) % 2 === 1 ? 'black-square' : 'white-square'} ${isTarget ? 'target-row' : ''} ${isDanger ? 'danger-line' : ''}`} 
                        />
                    );
                }))}
                {turboTrail && (
                    <div className="turbo-effect" 
                         style={{ 
                             left: `${turboTrail.file * 25}%`, 
                             top: `${turboTrail.rank * 25}%`,
                             width: '25%', height: '25%' 
                         }} />
                )}
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
        { id: 'wp1', type: 'P', color: 'w', file: 0, rank: 1 }, // White Pawn at a3
        { id: 'wp2', type: 'P', color: 'w', file: 1, rank: 1 }, // White Pawn at b3
        { id: 'bk', type: 'k', color: 'b', file: 0, rank: 0 }, // Black King at a4
    ]);
    const [message, setMessage] = useState("Horde: As White, your goal is to checkmate the Black King!");
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
            if (sq.file === 1 && sq.rank === 1) {
                moves.push({ file: 1, rank: 0 }); // Key move for mate
            }
            setLegalMoves(moves);
            return;
        }

        if (selected && selected.file === 1 && selected.rank === 1 && sq.file === 1 && sq.rank === 0) {
            setPieces(prev => prev.map(p => 
                (p.file === 1 && p.rank === 1) ? { ...p, file: 1, rank: 0 } : p
            ));
            setSelected(null);
            setLegalMoves([]);
            setCompleted(true);
            setMessage("CHECKMATE! The King has no escape. White wins!");
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
            setMessage("CHECKMATE! The King has no escape. White wins!");
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
                    setTimeout(() => setCheckFlash(false), 600);

                    if (nextChecks >= 3) {
                        setCompleted(true);
                        setMessage("3 Checks delivered! You win by Three-Check rules.");
                    } else {
                        setMessage(`CHECK! That's ${nextChecks}/3 checks. Keep going!`);
                    }
                } else {
                    setMessage("Move delivered, but it wasn't a check. Try again!");
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
                    setTimeout(() => setCheckFlash(false), 600);

                    if (nextChecks >= 3) {
                        setCompleted(true);
                        setMessage("3 Checks delivered! You win by Three-Check rules.");
                    } else {
                        setMessage(`CHECK! That's ${nextChecks}/3 checks. Keep going!`);
                    }
                } else {
                    setMessage("Move delivered, but it wasn't a check. Try again!");
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
        setMessage("Three-Check: Deliver 3 checks to the Black King to win!");
    };

    return (
        <div className="three-check-tutorial">
            <div className="check-counter">Checks: {checks} / 3</div>
            <div className="tutorial-board" ref={boardRef} onClick={handleBoardClick}>
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
            </div>
            <div className="tutorial-controls">
                <p>{message}</p>
                {completed && <button onClick={reset}>Reset Tutorial</button>}
            </div>
        </div>
    );
}

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
                    setMessage("CHECKMATE! The Rook cuts off the escape. You win!");
                } else {
                    setMessage("Good move, keep pushing the King into the corner!");
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
                    setMessage("CHECKMATE! The Rook cuts off the escape. You win!");
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

function Chess960TutorialBoard() {
    const [pieces, setPieces] = useState([
        { id: 'wr', type: 'R', color: 'w', file: 0, rank: 3 },
        { id: 'wn', type: 'N', color: 'w', file: 1, rank: 3 },
        { id: 'wb', type: 'B', color: 'w', file: 2, rank: 3 },
        { id: 'wk', type: 'K', color: 'w', file: 3, rank: 3 },
    ]);
    const [message, setMessage] = useState("Chess960: The starting positions of pieces are randomized!");
    
    const randomize = () => {
        const types = ['R', 'N', 'B', 'K'];
        for (let i = types.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [types[i], types[j]] = [types[j], types[i]];
        }
        setPieces(prev => prev.map((p, i) => ({ ...p, type: types[i] })));
        setMessage("The board has been randomized! In a full game, there are 960 possible starting positions.");
    };

    return (
        <div className="chess960-tutorial">
            <div className="tutorial-board">
                {[0, 1, 2, 3].map(rank => [0, 1, 2, 3].map(file => (
                    <div key={`${file}-${rank}`} className={`tutorial-square ${(rank + file) % 2 === 1 ? 'black-square' : 'white-square'}`} />
                )))}
                {pieces.map(p => (
                    <Piece key={p.id} piece={p.type} file={p.file} rank={p.rank} />
                ))}
            </div>
            <div className="tutorial-controls">
                <p>{message}</p>
                <button onClick={randomize}>Randomize Position</button>
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
                
                {currentVariant === 'standard' && <StandardTutorialBoard />}
                {currentVariant === 'atomic' && <AtomicTutorialBoard />}
                {currentVariant === 'antichess' && <AntichessTutorialBoard />}
                {currentVariant === 'crazyhouse' && <CrazyhouseTutorialBoard />}
                {currentVariant === 'king_of_the_hill' && <KOTHTutorialBoard />}
                {currentVariant === 'racing_kings' && <RacingKingsTutorialBoard />}
                {currentVariant === 'horde' && <HordeTutorialBoard />}
                {currentVariant === 'three_check' && <ThreeCheckTutorialBoard />}
                {currentVariant === 'chess960' && <Chess960TutorialBoard />}

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