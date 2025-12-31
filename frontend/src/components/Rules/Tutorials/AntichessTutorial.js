import React, { useState, useEffect, useRef } from 'react';
import Piece from '../../Pieces/Piece';
import LegalMoveDot from '../../LegalMoveDot/LegalMoveDot';
import HighlightSquare from '../../HighlightSquare/HighlightSquare';
import Confetti from '../Confetti';
import SoundManager from '../../../helpers/soundManager';
import '../Rules.css';

function AntichessTutorialBoard() {
    const [pieces, setPieces] = useState([
        { id: 'bq', type: 'q', color: 'b', file: 1, rank: 0 }, // Black Queen at b4
        { id: 'wp', type: 'P', color: 'w', file: 0, rank: 2 }, // White Pawn at a2
        { id: 'wk', type: 'K', color: 'w', file: 2, rank: 2 }, // White King at c2
        { id: 'wr', type: 'R', color: 'w', file: 3, rank: 3 }, // White Rook at d1
    ]);
    const [step, setStep] = useState(0); // 0: Pawn, 1: King, 2: Rook
    const [message, setMessage] = useState("Antichess: To win, you must lose all your pieces! Sacrifice your Pawn.");
    const [completed, setCompleted] = useState(false);
    const [selected, setSelected] = useState(null);
    const [legalMoves, setLegalMoves] = useState([]);
    const [shatter, setShatter] = useState(null); // { file, rank }
    const [isShaking, setIsShaking] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const boardRef = useRef(null);
    const canvasRef = useRef(null);
    const hasPlayedConfetti = useRef(false);

    useEffect(() => {
        if (completed && !hasPlayedConfetti.current) {
            hasPlayedConfetti.current = true;
        }
    }, [completed]);

    useEffect(() => {
        if (!shatter || !canvasRef.current || !boardRef.current) return;
        SoundManager.play('shatter');

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
                this.size = Math.random() * 12 + 4;
                this.s = Math.random() * 6 + 2;
                this.d = Math.random() * Math.PI * 2;
                this.rot = Math.random() * Math.PI * 2;
                this.rotS = (Math.random() - 0.5) * 0.3;
                const colors = ['#ffffff', '#e0f7fa', '#b2ebf2', '#81d4fa'];
                this.color = colors[Math.floor(Math.random() * colors.length)];
                this.opacity = 0.8;
            }
            update() {
                this.x += Math.cos(this.d) * this.s;
                this.y += Math.sin(this.d) * this.s;
                this.s *= 0.94;
                this.rot += this.rotS;
                this.opacity -= 0.015;
            }
            draw() {
                if (this.opacity <= 0) return;
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.rot);
                ctx.globalAlpha = this.opacity;
                ctx.fillStyle = this.color;
                ctx.shadowBlur = 5;
                ctx.shadowColor = 'rgba(255, 255, 255, 0.5)';
                ctx.beginPath();
                ctx.moveTo(0, -this.size / 2);
                ctx.lineTo(this.size / 2, this.size / 4);
                ctx.lineTo(-this.size / 3, this.size / 2);
                ctx.closePath();
                ctx.fill();
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 1;
                ctx.stroke();
                ctx.restore();
            }
        }

        const shards = Array.from({ length: 25 }, () => new Shard(centerX, centerY));

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

    const triggerOpponentCapture = (targetFile, targetRank, nextStep) => {
        setIsProcessing(true);
        setTimeout(() => {
            setPieces(prev => {
                const queen = prev.find(p => p.id === 'bq');
                return prev
                    .filter(p => !(p.file === targetFile && p.rank === targetRank))
                    .map(p => p.id === 'bq' ? { ...p, file: targetFile, rank: targetRank } : p);
            });
            setShatter({ file: targetFile, rank: targetRank });
            setIsShaking(true);
            setTimeout(() => setIsShaking(false), 300);
            
            const messages = [
                "Now move your King 1 step forward to sacrifice it!",
                "Last piece! Force the Queen to take your Rook by moving it 1 step forward.",
                "VICTORY! You lost everything. That's how you win Antichess!"
            ];
            setMessage(messages[nextStep - 1]);
            setStep(nextStep);
            if (nextStep === 3) setCompleted(true);
            setIsProcessing(false);
        }, 400);
    };

    const handleBoardClick = (e) => {
        if (completed || shatter || isShaking || isProcessing) return;
        const sq = getSquareFromCoords(e.clientX, e.clientY);
        if (!sq) return;

        const clickedPiece = pieces.find(p => p.file === sq.file && p.rank === sq.rank);

        const activeIds = ['wp', 'wk', 'wr'];
        const targetPositions = [{file: 0, rank: 1}, {file: 2, rank: 1}, {file: 3, rank: 2}];

        if (clickedPiece && clickedPiece.id === activeIds[step]) {
            setSelected(sq);
            setLegalMoves([targetPositions[step]]);
            return;
        }

        if (selected && sq.file === targetPositions[step].file && sq.rank === targetPositions[step].rank) {
            setPieces(prev => prev.map(p => 
                (p.file === selected.file && p.rank === selected.rank) ? { ...p, file: sq.file, rank: sq.rank } : p
            ));
            setSelected(null);
            setLegalMoves([]);
            triggerOpponentCapture(sq.file, sq.rank, step + 1);
        } else if (clickedPiece && clickedPiece.color === 'b') {
            return;
        } else {
            setSelected(null);
            setLegalMoves([]);
        }
    };

    const handlePieceDragStart = ({ file, rank, piece }) => {
        if (completed || shatter || isShaking || isProcessing) return;
        const activeTypes = ['P', 'K', 'R'];
        const targetPositions = [{file: 0, rank: 1}, {file: 2, rank: 1}, {file: 3, rank: 2}];
        if (piece !== activeTypes[step]) return;
        setSelected({ file, rank });
        setLegalMoves([targetPositions[step]]);
    };

    const handlePieceDrop = ({ clientX, clientY }) => {
        if (completed || shatter || isShaking || isProcessing) return;
        const sq = getSquareFromCoords(clientX, clientY);
        const targetPositions = [{file: 0, rank: 1}, {file: 2, rank: 1}, {file: 3, rank: 2}];
        if (sq && selected && sq.file === targetPositions[step].file && sq.rank === targetPositions[step].rank) {
            setPieces(prev => prev.map(p => 
                (p.file === selected.file && p.rank === selected.rank) ? { ...p, file: sq.file, rank: sq.rank } : p
            ));
            setSelected(null);
            setLegalMoves([]);
            triggerOpponentCapture(sq.file, sq.rank, step + 1);
        }
    };

    const reset = () => {
        setPieces([
            { id: 'bq', type: 'q', color: 'b', file: 1, rank: 0 },
            { id: 'wp', type: 'P', color: 'w', file: 0, rank: 2 },
            { id: 'wk', type: 'K', color: 'w', file: 2, rank: 2 },
            { id: 'wr', type: 'R', color: 'w', file: 3, rank: 3 },
        ]);
        setStep(0);
        setCompleted(false);
        setSelected(null);
        setLegalMoves([]);
        setShatter(null);
        setIsShaking(false);
        setMessage("Antichess: To win, you must lose all your pieces! Sacrifice your Pawn.");
    };

    return (
        <div className="antichess-tutorial">
            <div className={`tutorial-board ${isShaking ? 'shaking' : ''}`} ref={boardRef} onClick={handleBoardClick}>
                {[0, 1, 2, 3].map(rank => [0, 1, 2, 3].map(file => (
                    <div key={`${file}-${rank}`} className={`tutorial-square ${(rank + file) % 2 === 1 ? 'black-square' : 'white-square'}`} />
                )))}
                {selected && <HighlightSquare file={selected.file} rank={selected.rank} color="rgba(255, 255, 0, 0.5)" />}
                {legalMoves.map((m, i) => <LegalMoveDot key={i} file={m.file} rank={m.rank} />)}
                {pieces.map(p => {
                    const activeIds = ['wp', 'wk', 'wr'];
                    const isForced = !completed && !shatter && p.id === activeIds[step];
                    return (
                        <Piece 
                            key={p.id} 
                            piece={p.type} 
                            file={p.file} 
                            rank={p.rank} 
                            onDragStartCallback={handlePieceDragStart} 
                            onDropCallback={handlePieceDrop}
                            className={isForced ? 'forced-capture' : ''}
                        />
                    );
                })}
                {shatter && <canvas ref={canvasRef} className="explosion-canvas" />}
                <Confetti trigger={completed && !hasPlayedConfetti.current} />
            </div>
            <div className="tutorial-controls">
                <p>{message}</p>
                {completed && <button onClick={reset}>Reset Tutorial</button>}
            </div>
        </div>
    );
}

export default AntichessTutorialBoard;
