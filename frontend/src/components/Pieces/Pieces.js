import './Pieces.css'
import Piece from './Piece'
import LegalMoveDot from '../LegalMoveDot/LegalMoveDot.js';
import HighlightSquare from '../HighlightSquare/HighlightSquare.js';
import PromotionDialog from '../PromotionDialog/PromotionDialog.js';
import ImportDialog from '../ImportDialog/ImportDialog.js';
import { fenToPosition, coordsToAlgebraic, algebraicToCoords } from '../../helpers.js'
import { createGame, getLegalMoves, getAllLegalMoves } from '../../api.js'
import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom';

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

const NEW_GAME_ICON = (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
        <path d="M256 80c0-17.7-14.3-32-32-32s-32 14.3-32 32V224H48c-17.7 0-32 14.3-32 32s14.3 32 32 32H192V432c0 17.7 14.3 32 32 32s32-14.3 32-32V288H400c17.7 0 32-14.3 32-32s-14.3-32-32-32H256V80z"/>
    </svg>
);

const IMPORT_ICON = (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
        <path d="M128 64c0-35.3 28.7-64 64-64H352V128c0 17.7 14.3 32 32 32H512V448c0 35.3-28.7 64-64 64H192c-35.3 0-64-28.7-64-64V336H302.1l-39 39c-9.4 9.4-9.4 24.6 0 33.9s24.6 9.4 33.9 0l80-80c9.4-9.4 9.4-24.6 0-33.9l-80-80c-9.4-9.4-24.6-9.4-33.9 0s-9.4 24.6 0 33.9l39 39H128V64zm0 224v48H24c-13.3 0-24-10.7-24-24s10.7-24 24-24H128zM512 128H384c-17.7 0-32-14.3-32-32V0L512 128z"/>
    </svg>
);

const RESET_ICON = (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
        <path d="M463.5 224H472c13.3 0 24-10.7 24-24V72c0-9.7-5.8-18.5-14.8-22.2s-19.3-1.7-26.2 5.2L413.4 96.6c-87.6-86.5-228.7-86.2-315.8 1c-87.5 87.5-87.5 229.3 0 316.8s229.3 87.5 316.8 0c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0c-62.5 62.5-163.8 62.5-226.3 0s-62.5-163.8 0-226.3c62.2-62.2 162.7-62.5 225.3-1L327 183c-6.9 6.9-8.9 17.2-5.2 26.2s12.5 14.8 22.2 14.8H463.5z"/>
    </svg>
);

const MORE_ICON = (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
        <path d="M64 360a56 56 0 1 0 0 112 56 56 0 1 0 0-112zm0-160a56 56 0 1 0 0 112 56 56 0 1 0 0-112zM120 96A56 56 0 1 0 8 96a56 56 0 1 0 112 0z"/>
    </svg>
);

const VARIANTS = [
    { id: 'standard', title: 'Standard', icon: '♟️' },
    { id: 'antichess', title: 'Antichess', icon: '🚫' },
    { id: 'atomic', title: 'Atomic', icon: '⚛️' },
    { id: 'chess960', title: 'Chess960', icon: '🎲' },
    { id: 'crazyhouse', title: 'Crazyhouse', icon: '🏰' },
    { id: 'horde', title: 'Horde', icon: '🧟' },
    { id: 'kingofthehill', title: 'King of the Hill', icon: '⛰️' },
    { id: 'racingkings', title: 'Racing Kings', icon: '🏎️' },
    { id: 'threecheck', title: 'Three Check', icon: '3️⃣' },
];

const STARTING_TIME_VALUES = [
    0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 
    25, 30, 35, 40, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180
];

const INCREMENT_VALUES = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    25, 30, 35, 40, 45, 60, 90, 120, 150, 180
];

export function Pieces({ onFenChange, variant = "standard" }) {
    const ref = useRef()
    const highlightRef = useRef(null);
    const [fen, setFen] = useState();
    const [gameId, setGameId] = useState(null);
    const [legalMoves, setLegalMoves] = useState([]);
    const [selectedSquare, setSelectedSquare] = useState(null);
    const [inCheck, setInCheck] = useState(false);
    const [flashKingSquare, setFlashKingSquare] = useState(null);
    const [moveHistory, setMoveHistory] = useState([]);
    const [winner, setWinner] = useState(null);
    const [isGameOver, setIsGameOver] = useState(false);
    const ws = useRef(null);
    const [isPromotionDialogOpen, setPromotionDialogOpen] = useState(false);
    const [isImportDialogOpen, setImportDialogOpen] = useState(false);
    const [isNewGameDialogOpen, setNewGameDialogOpen] = useState(false);
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [promotionMove, setPromotionMove] = useState(null);
    const lastNotifiedFen = useRef(null);
    const dragStartSelectionState = useRef(false);
    const isPromoting = useRef(false);
    const navigate = useNavigate();

    // Time Control State
    const [isTimeControlEnabled, setIsTimeControlEnabled] = useState(false);
    const [startingTime, setStartingTime] = useState(10);
    const [increment, setIncrement] = useState(5);

    // Player Names State
    const [playerName, setPlayerName] = useState("Anonymous");
    const [opponentName, setOpponentName] = useState("Anonymous Opponent");
    
    // Sounds
    const moveSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/move-self.mp3"));
    const captureSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/capture.mp3"));
    const castleSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/castle.mp3"));
    const checkSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/move-check.mp3"));
    const gameEndSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_WEBM_/default/game-end.webm"));
    const gameStartSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/game-start.mp3"));
    const promotionSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/promote.mp3"));
    const illegalSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/illegal.mp3"));

    const initializeGame = async (fenToLoad = null, variantToLoad = null, tc = null) => {
        if (ws.current) {
            ws.current.close();
        }

        const timeControl = tc || (isTimeControlEnabled ? { starting_time: startingTime, increment: increment } : null);
        const { game_id: newGameId, fen: initialFen } = await createGame(variantToLoad || variant, fenToLoad, timeControl);
        setFen(initialFen);
        setGameId(newGameId);
        setMoveHistory([]);
        setLegalMoves([]);
        setSelectedSquare(null);
        setInCheck(false);
        setFlashKingSquare(null);
        if (highlightRef.current) highlightRef.current.style.display = 'none';
        
        gameStartSound.current.play().catch(e => console.error("Error playing game start sound:", e));

        const wsBase = process.env.REACT_APP_WS_URL || "ws://127.0.0.1:8000/ws";
        ws.current = new WebSocket(`${wsBase}/${newGameId}`);

        ws.current.onmessage = (event) => {
            const message = JSON.parse(event.data);
            if (message.type === "game_state") {
                setFen(message.fen);
                setInCheck(message.in_check);
                setMoveHistory(message.move_history || []);
                setWinner(message.winner);
                setIsGameOver(message.is_over);
                setSelectedSquare(null);
                setLegalMoves([]);
                if (highlightRef.current) highlightRef.current.style.display = 'none';

                if (message.status === "checkmate") {
                    console.log("Checkmate detected!");
                    gameEndSound.current.play().catch(e => console.error("Error playing game end sound:", e));
                } else if (message.status === "draw") {
                    console.log("Draw detected!");
                    gameEndSound.current.play().catch(e => console.error("Error playing game end sound:", e));
                } else if (message.status === "game_over") {
                    console.log("Game over detected!");
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
    }, [variant]);

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
            
            // Log all legal moves when turn switches
            if (gameId) {
                getAllLegalMoves(gameId).then(response => {
                    if (response.status === "success") {
                        console.log("All Legal Moves for current turn:", response.moves);
                    }
                }).catch(error => {
                    console.error("Failed to fetch all legal moves:", error);
                });
            }
        }
    }, [fen, onFenChange, inCheck, gameId]);

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
            if (r < 0 || r > 7 || f < 0 || f > 7) return false;
            const piece = position[r][f];
            return !!piece;
        };

        if (selectedSquare) {
            const movesToTarget = legalMoves.filter(m => {
                const targetSquareFromUci = m.length === 5 ? m.slice(2, 4) : m.slice(2, 4);
                return targetSquareFromUci === clickedSquare;
            });

            if (movesToTarget.length > 0) {
                // If there are multiple moves to the target square (e.g., different promotion pieces)
                // or if the move is a promotion (length 5 for UCI), open the promotion dialog.
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

    const handleNewGameClick = (e) => {
        e.stopPropagation();
        setNewGameDialogOpen(true);
        setIsMenuOpen(false);
    };

    const handleVariantSelect = (variantId) => {
        setNewGameDialogOpen(false);
        if (variantId === variant) {
            initializeGame();
        } else {
            navigate(variantId === 'standard' ? '/' : `/${variantId}`);
        }
    };

    const handleReset = (e) => {
        e.stopPropagation();
        initializeGame();
        setIsMenuOpen(false);
    };

    const handleUndo = (e) => {
        e.stopPropagation();
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ type: "undo" }));
        }
        setIsMenuOpen(false);
    };

    const handleImportClick = (e) => {
        e.stopPropagation();
        setImportDialogOpen(true);
        setIsMenuOpen(false);
    };

    const handleImport = (fenString, selectedVariant) => {
        setImportDialogOpen(false);
        if (fenString) {
            initializeGame(fenString, selectedVariant);
        }
    };

    const handleCancelImport = () => {
        setImportDialogOpen(false);
    };
    
    const handleMenuToggle = (e) => {
        e.stopPropagation();
        setIsMenuOpen(!isMenuOpen);
    }

    const isCaptureMove = (file, rank) => {
        if (!selectedSquare) return false;
        const targetSquare = coordsToAlgebraic(file, rank);
        return legalMoves.some(m => m.slice(2, 4) === targetSquare);
    };

    const copyFenToClipboard = async (e) => {
        if (e) e.stopPropagation();
        if (!fen) return;
        try {
            await navigator.clipboard.writeText(fen);
        } catch (err) {
            console.error('Failed to copy FEN: ', err);
        }
        setIsMenuOpen(false);
    };

    const promotionColor = fen && fen.split(' ')[1] === 'w' ? 'w' : 'b';

    return (
        <div
            className="pieces"
            ref={ref}
            onClick={(e) => {
                handleSquareClick(e);
                if (isMenuOpen) setIsMenuOpen(false);
            }}
            >
            
            <div className="player-name-display opponent-name">
                {opponentName}
            </div>

            <div className="game-sidebar" onClick={e => e.stopPropagation()}>
                <div className="move-history">
                    <div className="history-header">
                        Moves
                    </div>
                    {moveHistory.reduce((rows, move, index) => {
                        if (index % 2 === 0) rows.push([move]);
                        else rows[rows.length - 1].push(move);
                        return rows;
                    }, []).map((row, i) => (
                        <div key={i} className="history-row">
                            <span style={{ color: '#888' }}>{i + 1}.</span>
                            <span>{row[0]}</span>
                            <span>{row[1] || ''}</span>
                        </div>
                    ))}
                </div>

                <div className="game-controls">
                    <button 
                        onClick={handleUndo}
                        title="Undo"
                        className="control-button"
                    >
                        {UNDO_ICON}
                    </button>
                    <button 
                        onClick={handleReset}
                        title="Reset Game"
                        className="control-button"
                    >
                        {RESET_ICON}
                    </button>
                    <button 
                        onClick={handleNewGameClick}
                        title="New Game"
                        className="control-button"
                    >
                        {NEW_GAME_ICON}
                    </button>
                    <button 
                        onClick={handleMenuToggle}
                        title="More"
                        className="control-button"
                    >
                        {MORE_ICON}
                    </button>

                    {isMenuOpen && (
                        <div className="more-menu-dropdown">
                             <button className="menu-item" onClick={copyFenToClipboard}>
                                {EXPORT_ICON} Export Game
                             </button>
                             <button className="menu-item" onClick={handleImportClick}>
                                {IMPORT_ICON} Import Game
                             </button>
                        </div>
                    )}
                </div>
            </div>

            {isNewGameDialogOpen && (
                <div className="new-game-dialog-overlay" onClick={() => setNewGameDialogOpen(false)}>
                    <div className="new-game-dialog" onClick={e => e.stopPropagation()}>
                        <h2>New Game</h2>
                        
                        <div className="player-names-input">
                            <div className="setting-row">
                                <label>Your Name</label>
                                <input 
                                    type="text" 
                                    value={playerName} 
                                    onChange={(e) => setPlayerName(e.target.value)}
                                    placeholder="Anonymous"
                                />
                            </div>
                            <div className="setting-row">
                                <label>Opponent Name</label>
                                <input 
                                    type="text" 
                                    value={opponentName} 
                                    onChange={(e) => setOpponentName(e.target.value)}
                                    placeholder="Anonymous Opponent"
                                />
                            </div>
                        </div>

                        <div className="variants-grid">
                            {VARIANTS.map(v => (
                                <button
                                    key={v.id}
                                    className={`variant-select-btn ${variant === v.id ? 'active' : ''}`}
                                    onClick={() => handleVariantSelect(v.id)}
                                >
                                    <span className="variant-icon">{v.icon}</span>
                                    <span>{v.title}</span>
                                </button>
                            ))}
                        </div>

                        <div className="time-control-settings">
                            <div className="setting-row">
                                <label className="switch-container">
                                    <span>Time Control</span>
                                    <input 
                                        type="checkbox" 
                                        checked={isTimeControlEnabled} 
                                        onChange={(e) => setIsTimeControlEnabled(e.target.checked)} 
                                    />
                                    <span className="slider round"></span>
                                </label>
                            </div>
                            
                            {isTimeControlEnabled && (
                                <>
                                    <div className="setting-row slider-setting">
                                        <div className="slider-label">
                                            <span>Starting Time</span>
                                            <span>
                                                {startingTime === 0.5 ? '1/2' : 
                                                 startingTime === 1.5 ? '1 1/2' : 
                                                 startingTime} min
                                            </span>
                                        </div>
                                        <input 
                                            type="range" 
                                            min="0" 
                                            max={STARTING_TIME_VALUES.length - 1} 
                                            value={STARTING_TIME_VALUES.indexOf(startingTime)} 
                                            onChange={(e) => setStartingTime(STARTING_TIME_VALUES[parseInt(e.target.value)])} 
                                        />
                                    </div>
                                    <div className="setting-row slider-setting">
                                        <div className="slider-label">
                                            <span>Increment</span>
                                            <span>{increment} sec</span>
                                        </div>
                                        <input 
                                            type="range" 
                                            min="0" 
                                            max={INCREMENT_VALUES.length - 1} 
                                            value={INCREMENT_VALUES.indexOf(increment)} 
                                            onChange={(e) => setIncrement(INCREMENT_VALUES[parseInt(e.target.value)])} 
                                        />
                                    </div>
                                </>
                            )}
                        </div>

                        <div className="dialog-actions">
                            <button className="cancel-btn" onClick={() => setNewGameDialogOpen(false)}>Cancel</button>
                        </div>
                    </div>
                </div>
            )}

            {isPromotionDialogOpen && <PromotionDialog onPromote={handlePromotion} onCancel={handleCancelPromotion} color={promotionColor} />}
            {isImportDialogOpen && <ImportDialog onImport={handleImport} onCancel={handleCancelImport} />}

            {selectedSquare && (() => {
                const { file, rank } = algebraicToCoords(selectedSquare);
                const isDark = (file + rank) % 2 !== 0; // Chessboard pattern
                return <HighlightSquare
                    file={file}
                    rank={rank}
                    isDark={isDark}
                />;
            })()}

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

            {legalMoves.map((moveUci, index) => {
                const targetSquare = moveUci.slice(2, 4);
                const { file, rank } = algebraicToCoords(targetSquare);
                return <LegalMoveDot key={index} file={file} rank={rank} />;
            })}

            {isGameOver && (() => {
                const getKingSquare = (color) => {
                    const kingChar = color === 'w' ? 'K' : 'k';
                    for (let r = 0; r < 8; r++) {
                        for (let f = 0; f < 8; f++) {
                            if (position[r] && position[r][f] === kingChar) {
                                return { file: f, rank: r };
                            }
                        }
                    }
                    return color === 'w' ? { file: 4, rank: 7 } : { file: 4, rank: 0 };
                };

                const whiteKingSq = getKingSquare('w');
                const blackKingSq = getKingSquare('b');

                const getStatusColor = (color) => {
                    if (!winner) return 'grey'; // Draw
                    return winner === color ? '#4CAF50' : '#F44336';
                };

                const renderIndicator = (sq, color) => (
                    <div style={{
                        position: 'absolute',
                        left: `calc(${sq.file} * var(--square-size) + var(--square-size) / 2 - 15px)`,
                        top: `calc(${sq.rank} * var(--square-size) + var(--square-size) / 2 - 15px)`,
                        width: '30px',
                        height: '30px',
                        borderRadius: '50%',
                        backgroundColor: getStatusColor(color),
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        zIndex: 1000,
                        boxShadow: '0 2px 5px rgba(0,0,0,0.5)'
                    }}>
                        <img 
                            src={`/images/pieces/${color === 'w' ? 'K' : 'k'}.png`} 
                            style={{ width: '20px', height: '20px', filter: 'brightness(0) invert(1)' }} 
                            alt="" 
                        />
                    </div>
                );

                return (
                    <>
                        {renderIndicator(whiteKingSq, 'w')}
                        {renderIndicator(blackKingSq, 'b')}
                    </>
                );
            })()}

            <div className="player-name-display player-name">
                {playerName}
            </div>
        </div>
    );
}