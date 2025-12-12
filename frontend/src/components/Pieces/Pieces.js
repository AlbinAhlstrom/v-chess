import './Pieces.css'
import Piece from './Piece'
import LegalMoveDot from '../LegalMoveDot/LegalMoveDot.js';
import HighlightSquare from '../HighlightSquare/HighlightSquare.js';
import PromotionDialog from '../PromotionDialog/PromotionDialog.js';
import { fenToPosition, coordsToAlgebraic, algebraicToCoords } from '../../helpers.js'
import { createGame, getLegalMoves } from '../../api.js'
import { useState, useRef, useEffect } from 'react'

const UNDO_ICON = (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
        <path d="M9.4 233.4c-12.5 12.5-12.5 32.8 0 45.3l160 160c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L109.2 288 416 288c17.7 0 32-14.3 32-32s-14.3-32-32-32l-306.7 0L214.6 118.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0l-160 160z"/>
    </svg>
);

const EXPORT_ICON = (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
        <path d="M307 34.8c-11.5 5.1-19 16.6-19 29.2v64H176C78.8 128 0 206.8 0 304C0 417.3 81.5 467.9 100.2 478.1c2.5 1.4 5.3 1.9 7.8 1.9c10.9 0 19.7-8.9 19.7-19.7c0-7.5-4.3-14.4-9.8-19.5C108.8 431.9 96 414.4 96 384c0-53 43-96 96-96h96v64c0 12.6 7.4 24.1 19 29.2s25 3 34.4-5.4l160-144c6.7-6.1 10.6-14.7 10.6-24s-3.9-17.9-10.6-24l-160-144c-9.4-8.5-22.9-10.6-34.4-5.4z"/>
    </svg>
);

const RESET_ICON = (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
        <path d="M463.5 224H472c13.3 0 24-10.7 24-24V72c0-9.7-5.8-18.5-14.8-22.2s-19.3-1.7-26.2 5.2L413.4 96.6c-87.6-86.5-228.7-86.2-315.8 1c-87.5 87.5-87.5 229.3 0 316.8s229.3 87.5 316.8 0c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0c-62.5 62.5-163.8 62.5-226.3 0s-62.5-163.8 0-226.3c62.2-62.2 162.7-62.5 225.3-1L327 183c-6.9 6.9-8.9 17.2-5.2 26.2s12.5 14.8 22.2 14.8H463.5z"/>
    </svg>
);

export function Pieces({ onFenChange }) {
    const ref = useRef()
    const highlightRef = useRef(null);
    const [fen, setFen] = useState();
    const [gameId, setGameId] = useState(null);
    const [legalMoves, setLegalMoves] = useState([]);
    const [selectedSquare, setSelectedSquare] = useState(null);
    const [inCheck, setInCheck] = useState(false);
    const [flashKingSquare, setFlashKingSquare] = useState(null);
    const [moveHistory, setMoveHistory] = useState([]);
    const ws = useRef(null);
    const [isPromotionDialogOpen, setPromotionDialogOpen] = useState(false);
    const [promotionMove, setPromotionMove] = useState(null);
    const lastNotifiedFen = useRef(null);
    const dragStartSelectionState = useRef(false);
    const isPromoting = useRef(false);
    
    // Sounds
    const moveSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/move-self.mp3"));
    const captureSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/capture.mp3"));
    const castleSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/castle.mp3"));
    const checkSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/move-check.mp3"));
    const gameEndSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_WEBM_/default/game-end.webm"));
    const gameStartSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/game-start.mp3"));
    const promotionSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/promote.mp3"));
    const illegalSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/illegal.mp3"));

    const initializeGame = async () => {
        if (ws.current) {
            ws.current.close();
        }

        const { game_id: newGameId, fen: initialFen } = await createGame();
        setFen(initialFen);
        setGameId(newGameId);
        setMoveHistory([]);
        setLegalMoves([]);
        setSelectedSquare(null);
        setInCheck(false);
        setFlashKingSquare(null);
        if (highlightRef.current) highlightRef.current.style.display = 'none';
        
        gameStartSound.current.play().catch(e => console.error("Error playing game start sound:", e));

        ws.current = new WebSocket(`ws://127.0.0.1:8000/ws/${newGameId}`);

        ws.current.onmessage = (event) => {
            const message = JSON.parse(event.data);
            if (message.type === "game_state") {
                setFen(message.fen);
                setInCheck(message.in_check);
                setMoveHistory(message.move_history || []);
                setSelectedSquare(null);
                setLegalMoves([]);
                if (highlightRef.current) highlightRef.current.style.display = 'none';

                if (message.status === "checkmate") {
                    console.log("Checkmate detected!");
                    gameEndSound.current.play().catch(e => console.error("Error playing game end sound:", e));
                } else if (message.status === "draw") {
                    console.log("Draw detected!");
                    gameEndSound.current.play().catch(e => console.error("Error playing game end sound:", e));
                }
            } else if (message.type === "error") {
                console.error("WebSocket error:", message.message);
                if (message.message.toLowerCase().includes("check") && lastNotifiedFen.current) {
                    illegalSound.current.play().catch(e => console.error("Error playing illegal move sound:", e));
                    const currentFen = lastNotifiedFen.current;
                    const isWhite = currentFen.split(' ')[1] === 'w';
                    const grid = fenToPosition(currentFen);
                    const kingChar = isWhite ? 'K' : 'k';
                    let kingCoords = null;
                    
                    for (let r = 0; r < 8; r++) {
                        for (let c = 0; c < 8; c++) {
                            if (grid[r][c] === kingChar) {
                                kingCoords = { file: c, rank: r };
                                break;
                            }
                        }
                        if (kingCoords) break;
                    }
                    
                    if (kingCoords) {
                        setFlashKingSquare(kingCoords);
                        setTimeout(() => setFlashKingSquare(null), 500);
                    }
                }
            }
        };

        ws.current.onclose = () => console.log("WebSocket disconnected");
        ws.current.onerror = (error) => console.error("WebSocket error:", error);
    };

    useEffect(() => {
        initializeGame();
        return () => {
            if (ws.current) {
                ws.current.close();
            }
        };
    }, []);

    useEffect(() => {
        if (fen && fen !== lastNotifiedFen.current) {
            if (lastNotifiedFen.current) {
                const countPieces = (fenString) => {
                    return fenString.split(' ')[0].split('').filter(c => /[pnbrqkPNBRQK]/.test(c)).length;
                };

                const findKingCol = (fenString, isWhite) => {
                    const grid = fenToPosition(fenString);
                    const kingChar = isWhite ? 'K' : 'k';
                    for (let r = 0; r < 8; r++) {
                        for (let c = 0; c < 8; c++) {
                            if (grid[r][c] === kingChar) return c;
                        }
                    }
                    return -1;
                };

                const prevTurn = lastNotifiedFen.current.split(' ')[1];
                const isWhiteTurn = prevTurn === 'w';
                
                const prevKingCol = findKingCol(lastNotifiedFen.current, isWhiteTurn);
                const currKingCol = findKingCol(fen, isWhiteTurn);
                const isCastling = prevKingCol !== -1 && currKingCol !== -1 && Math.abs(prevKingCol - currKingCol) > 1;

                const prevCount = countPieces(lastNotifiedFen.current);
                const currentCount = countPieces(fen);

                if (inCheck) {
                    checkSound.current.play().catch(e => console.error("Error playing check sound:", e));
                } else if (isPromoting.current) {
                    promotionSound.current.play().catch(e => console.error("Error playing promotion sound:", e));
                    isPromoting.current = false;
                } else if (isCastling) {
                    castleSound.current.play().catch(e => console.error("Error playing castle sound:", e));
                } else if (currentCount < prevCount) {
                     captureSound.current.play().catch(e => console.error("Error playing capture sound:", e));
                } else {
                     moveSound.current.play().catch(e => console.error("Error playing move sound:", e));
                }
            }
            onFenChange(fen);
            lastNotifiedFen.current = fen;
        }
    }, [fen, onFenChange, inCheck]);

    const position = fen ? fenToPosition(fen) : [];

    const calculateSquare = e => {
        const {width,left,top} = ref.current.getBoundingClientRect()
        const size = width / 8
        const file = Math.floor((e.clientX - left) / size)
        const rank = Math.floor((e.clientY - top) / size)
        return { file, rank, algebraic: coordsToAlgebraic(file, rank) };
    }

    const handlePieceDragHover = (clientX, clientY) => {
        if (!highlightRef.current) return;
        
        if (!clientX || !clientY) {
            highlightRef.current.style.display = 'none';
            return;
        }
        const { file, rank } = calculateSquare({ clientX, clientY });
        
        if (file >= 0 && file <= 7 && rank >= 0 && rank <= 7) {
            highlightRef.current.style.display = 'block';
            highlightRef.current.style.left = `calc(${file} * var(--square-size))`;
            highlightRef.current.style.top = `calc(${rank} * var(--square-size))`;
            
            const isDark = (file + rank) % 2 !== 0;
            highlightRef.current.style.border = isDark 
                ? '5px solid var(--drag-hover-dark-border)' 
                : '5px solid var(--drag-hover-light-border)';
        } else {
            highlightRef.current.style.display = 'none';
        }
    }

    const handleManualDrop = ({ clientX, clientY, piece, file, rank }) => {
        if (highlightRef.current) highlightRef.current.style.display = 'none';
        
        // Mock event object for calculateSquare
        const mockEvent = { clientX, clientY };
        const { rank: toRank, algebraic: toSquare } = calculateSquare(mockEvent);
        
        const fromSquare = coordsToAlgebraic(file, rank);

        if (fromSquare === toSquare) {
            if (dragStartSelectionState.current) {
                setSelectedSquare(null);
                setLegalMoves([]);
            }
            return;
        }

        const isPawn = piece.toLowerCase() === 'p';
        const isPromotion = isPawn && (toRank === 0 || toRank === 7);

        if (isPromotion) {
            setPromotionMove({ from: fromSquare, to: toSquare });
            setPromotionDialogOpen(true);
        } else {
            try {
                const moveUci = `${fromSquare}${toSquare}`;
                if (ws.current && ws.current.readyState === WebSocket.OPEN) {
                    ws.current.send(JSON.stringify({ type: "move", uci: moveUci }));
                }
            } catch (error) {
                console.error("Failed to make move:", error);
            }
        }
    }

    const handlePromotion = (promotionPiece) => {
        if (promotionMove) {
            isPromoting.current = true;
            const moveUci = `${promotionMove.from}${promotionMove.to}${promotionPiece}`;
            if (ws.current && ws.current.readyState === WebSocket.OPEN) {
                ws.current.send(JSON.stringify({ type: "move", uci: moveUci }));
            }
        }
        setPromotionDialogOpen(false);
        setPromotionMove(null);
    };

    const handleCancelPromotion = () => {
        setPromotionDialogOpen(false);
        setPromotionMove(null);
    };

    const handlePieceDragStart = async ({ file, rank, piece, isCapture }) => {
        if (!gameId) return;
        const square = coordsToAlgebraic(file, rank);

        if (isCapture && selectedSquare) {
             const moveUci = `${selectedSquare}${square}`;
             if (ws.current && ws.current.readyState === WebSocket.OPEN) {
                 ws.current.send(JSON.stringify({ type: "move", uci: moveUci }));
             }
             setSelectedSquare(null);
             setLegalMoves([]);
             return;
        }
        
        dragStartSelectionState.current = (selectedSquare === square);
        setSelectedSquare(square);
        
        try {
            const response = await getLegalMoves(gameId, square);
            if (response.status === "success") {
                setLegalMoves(response.moves);
            }
        } catch (error) {
            console.error("Failed to fetch legal moves:", error);
        }
    };

    const handlePieceDragEnd = () => {
        
    };

    const handleSquareClick = async (e) => {
        if (!gameId || !fen) return;

        const { file, rank, algebraic: clickedSquare } = calculateSquare(e);


        const isPiece = (f, r) => {
            const piece = position[r][f];
            return !!piece;
        };

        if (selectedSquare) {
            const movesToTarget = legalMoves.filter(m => m.slice(2, 4) === clickedSquare);

            if (movesToTarget.length > 0) {
                if (movesToTarget.length > 1 || movesToTarget[0].length === 5) {
                    setPromotionMove({ from: selectedSquare, to: clickedSquare });
                    setPromotionDialogOpen(true);
                } else {
                    const moveUci = movesToTarget[0];
                    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
                        ws.current.send(JSON.stringify({ type: "move", uci: moveUci }));
                    }
                }
            } else {
                if (clickedSquare === selectedSquare) {
                    setSelectedSquare(null);
                    setLegalMoves([]);
                } else if (isPiece(file, rank)) {
                    setSelectedSquare(clickedSquare);
                    try {
                        const response = await getLegalMoves(gameId, clickedSquare);
                        if (response.status === "success") {
                            setLegalMoves(response.moves);
                        }
                    } catch (error) {
                        console.error("Failed to fetch legal moves:", error);
                    }
                } else {
                    setSelectedSquare(null);
                    setLegalMoves([]);
                }
            }
        } else {
            if (isPiece(file, rank)) {
                setSelectedSquare(clickedSquare);
                try {
                    const response = await getLegalMoves(gameId, clickedSquare);
                    if (response.status === "success") {
                        setLegalMoves(response.moves);
                    }
                } catch (error) {
                    console.error("Failed to fetch legal moves:", error);
                }
            }
        }
    };

    const handleReset = (e) => {
        e.stopPropagation();
        initializeGame();
    };

    const handleUndo = (e) => {
        e.stopPropagation();
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ type: "undo" }));
        }
    };

    const isCaptureMove = (file, rank) => {
        if (!selectedSquare) return false;
        const targetSquare = coordsToAlgebraic(file, rank);
        return legalMoves.some(m => m.slice(2, 4) === targetSquare);
    };

    const copyFenToClipboard = async () => {
        if (!fen) return;
        try {
            await navigator.clipboard.writeText(fen);
        } catch (err) {
            console.error('Failed to copy FEN: ', err);
        }
    };

    const promotionColor = fen && fen.split(' ')[1] === 'w' ? 'w' : 'b';

    return (
        <div
            className="pieces"
            ref={ref}
            onClick={handleSquareClick}
            >

            <div style={{
                position: 'absolute',
                left: '100%',
                top: '50%',
                transform: 'translateY(-50%)',
                marginLeft: '20px',
                display: 'flex',
                flexDirection: 'column',
                gap: '10px',
                fontFamily: 'var(--main-font-family)',
                width: 'var(--history-width)'
            }}>
                <div style={{ 
                    height: 'calc(4 * var(--square-size))',
                    overflowY: 'auto', 
                    color: 'var(--history-text-color)', 
                    width: '100%',
                    backgroundColor: 'var(--history-bg-color)',
                    borderRadius: '4px',
                    padding: '10px',
                    boxSizing: 'border-box',
                    display: 'flex',
                    flexDirection: 'column',
                    fontWeight: '600'
                }}>
                    <div style={{ 
                        position: 'sticky', 
                        top: 0, 
                        backgroundColor: 'var(--history-bg-color)', 
                        paddingBottom: '5px', 
                        marginBottom: '5px', 
                        borderBottom: '1px solid #444',
                        fontWeight: '700',
                        zIndex: 1
                    }}>
                        Moves
                    </div>
                    {moveHistory.reduce((rows, move, index) => {
                        if (index % 2 === 0) rows.push([move]);
                        else rows[rows.length - 1].push(move);
                        return rows;
                    }, []).map((row, i) => (
                        <div key={i} style={{ 
                            marginBottom: '5px', 
                            display: 'grid', 
                            gridTemplateColumns: '30px 1fr 1fr', 
                            gap: '10px',
                            alignItems: 'center'
                        }}>
                            <span style={{ color: '#888' }}>{i + 1}.</span>
                            <span>{row[0]}</span>
                            <span>{row[1] || ''}</span>
                        </div>
                    ))}
                </div>

                <div style={{ display: 'flex', gap: '10px' }}>
                    <button 
                        onClick={handleUndo}
                        title="Undo"
                        style={{
                            padding: '0',
                            fontSize: '16px',
                            cursor: 'pointer',
                            whiteSpace: 'nowrap',
                            fontFamily: 'inherit',
                            backgroundColor: 'var(--button-bg-color)',
                            color: 'var(--button-text-color)',
                            border: 'none',
                            borderRadius: '4px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            width: 'var(--button-size)',
                            height: 'var(--button-height)'
                        }}
                    >
                        {UNDO_ICON}
                    </button>
                    <button 
                        onClick={copyFenToClipboard}
                        title="Export Game"
                        style={{
                            padding: '0',
                            fontSize: '16px',
                            cursor: 'pointer',
                            whiteSpace: 'nowrap',
                            fontFamily: 'inherit',
                            backgroundColor: 'var(--button-bg-color)',
                            color: 'var(--button-text-color)',
                            border: 'none',
                            borderRadius: '4px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            width: 'var(--button-size)',
                            height: 'var(--button-height)'
                        }}
                    >
                        {EXPORT_ICON}
                    </button>
                    <button 
                        onClick={handleReset}
                        title="Reset Game"
                        style={{
                            padding: '0',
                            fontSize: '16px',
                            cursor: 'pointer',
                            whiteSpace: 'nowrap',
                            fontFamily: 'inherit',
                            backgroundColor: 'var(--button-bg-color)',
                            color: 'var(--button-text-color)',
                            border: 'none',
                            borderRadius: '4px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            width: 'var(--button-size)',
                            height: 'var(--button-height)'
                        }}
                    >
                        {RESET_ICON}
                    </button>
                </div>
            </div>

            {isPromotionDialogOpen && <PromotionDialog onPromote={handlePromotion} onCancel={handleCancelPromotion} color={promotionColor} />}

            {flashKingSquare && (
                <div 
                    className="king-flash"
                    style={{
                        left: `calc(${flashKingSquare.file} * var(--square-size))`,
                        top: `calc(${flashKingSquare.rank} * var(--square-size))`
                    }}
                />
            )}

            <div 
                ref={highlightRef}
                style={{
                    position: 'absolute',
                    width: 'var(--square-size)',
                    height: 'var(--square-size)',
                    boxSizing: 'border-box',
                    zIndex: 6, 
                    pointerEvents: 'none',
                    display: 'none'
                }}
            />

            {selectedSquare && (() => {
                const { file, rank } = algebraicToCoords(selectedSquare);
                const isDark = (file + rank) % 2 !== 0; // Chessboard pattern
                return <HighlightSquare
                    file={file}
                    rank={rank}
                    isDark={isDark}
                />;
            })()}

            {legalMoves.map((moveUci, index) => {
                const targetSquare = moveUci.slice(2, 4);
                const { file, rank } = algebraicToCoords(targetSquare);
                return <LegalMoveDot key={index} file={file} rank={rank} />;
            })}

            {position.map((rankArray, rankIndex) =>
                rankArray.map((pieceType, fileIndex) =>
                    pieceType
                        ? <Piece
                            key={`p-${rankIndex}-${fileIndex}`}
                            rank={rankIndex}
                            file={fileIndex}
                            piece={pieceType}
                            onDragStartCallback={handlePieceDragStart}
                            onDragEndCallback={handlePieceDragEnd}
                            onDropCallback={handleManualDrop}
                            onDragHoverCallback={handlePieceDragHover}
                            isCapture={isCaptureMove(fileIndex, rankIndex)}
                          />
                        : null
                )
            )}
        </div>
    );
}