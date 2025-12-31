import React, { useState, useEffect, useRef } from 'react';
import Piece from '../../Pieces/Piece';
import LegalMoveDot from '../../LegalMoveDot/LegalMoveDot';
import HighlightSquare from '../../HighlightSquare/HighlightSquare';
import Confetti from '../Confetti';
import SoundManager from '../../../helpers/soundManager';
import FlyingKnight from './FlyingKnight';
import '../Rules.css';

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
    const hasPlayedConfetti = useRef(false);

    useEffect(() => {
        if (completed && !hasPlayedConfetti.current) {
            hasPlayedConfetti.current = true;
        }
    }, [completed]);

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

            // Rapid beep sequence
            SoundManager.play('caution');
            setTimeout(() => SoundManager.play('caution'), 200);
            setTimeout(() => SoundManager.play('caution'), 400);

            // Phase 1: Tilt in place (600ms)
            setTimeout(() => {
                setIsPreparing(false);
                setIsIgnition(false);
                setIsFlying(true);
                setAnimatingKnight({ file: targetFile, rank: targetRank }); // Set destination for CSS transition
                SoundManager.play('whoosh');
                
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
                    SoundManager.play('explosion');
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
            }, 600);
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
                <Confetti trigger={completed && !hasPlayedConfetti.current} />
            </div>
            <div className="tutorial-controls">
                <p>{message}</p>
                {completed && <button onClick={reset}>Reset Tutorial</button>}
            </div>
        </div>
    );
}

export default AtomicTutorialBoard;
