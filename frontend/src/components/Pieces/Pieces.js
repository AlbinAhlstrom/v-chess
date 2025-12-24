import './Pieces.css'
import Piece from './Piece'
import LegalMoveDot from '../LegalMoveDot/LegalMoveDot.js';
import HighlightSquare from '../HighlightSquare/HighlightSquare.js';
import PromotionDialog from '../PromotionDialog/PromotionDialog.js';
import ImportDialog from '../ImportDialog/ImportDialog.js';
import { fenToPosition, coordsToAlgebraic, algebraicToCoords } from '../../helpers.js'
import { createGame, getLegalMoves, getAllLegalMoves, getGame, getMe, login, logout, getWsBase } from '../../api.js'
import { useState, useRef, useEffect, useCallback } from 'react'
import { useNavigate, useParams } from 'react-router-dom';

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

const DRAW_ICON = (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
        <path d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM369 209L241 337c-9.4 9.4-24.6 9.4-33.9 0l-64-64c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0l47 47L335 175c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9z" opacity="0.2"/>
        <text x="50%" y="55%" dominantBaseline="middle" textAnchor="middle" fontSize="280" fontWeight="900" fontFamily="system-ui" fill="currentColor">½</text>
    </svg>
);

const RESIGN_ICON = (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
        <path d="M48 24C48 10.7 37.3 0 24 0S0 10.7 0 24V64 350.5 400v88c0 13.3 10.7 24 24 24s24-10.7 24-24V400h80 8 24 80c21.7 0 40.6-14.6 46.2-35.3l12.3-45.2c6-22.1 26-37.5 48.9-37.5H424c13.3 0 24-10.7 24-24V72c0-13.3-10.7-24-24-24H338.6c-22.9 0-43 15.4-48.9 37.5l-12.3 45.2c-5.6 20.7-24.5 35.3-46.2 35.3H152V120 64H48V24z"/>
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
    0.25, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 
    25, 30, 35, 40, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180
];

const INCREMENT_VALUES = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    25, 30, 35, 40, 45, 60, 90, 120, 150, 180
];

export function Pieces({ onFenChange, variant = "standard", matchmaking = false, setFlipped }) {
    const { gameId: urlGameId } = useParams();
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

    const [user, setUser] = useState(null);
    const [isFlipped, setIsFlippedLocal] = useState(false);

    const setFlippedCombined = (val) => {
        setIsFlippedLocal(val);
        if (setFlipped) setFlipped(val);
    };

    // Time Control State
    const [isTimeControlEnabled, setIsTimeControlEnabled] = useState(true);
    const [startingTime, setStartingTime] = useState(10);
    const [increment, setIncrement] = useState(2);

    // Player Names State
    const [playerName, setPlayerName] = useState("Anonymous");
    const [opponentName, setOpponentName] = useState("Anonymous Opponent");
    const [whitePlayerId, setWhitePlayerId] = useState(null);
    const [blackPlayerId, setBlackPlayerId] = useState(null);
    const [takebackOffer, setTakebackOffer] = useState(null); // { by_user_id: number }

    // Effect to handle board flipping and player names once both user and game data are available
    useEffect(() => {
        if (matchmaking && user && (whitePlayerId || blackPlayerId)) {
            console.log(`Setting up matchmaking game. UserID: ${user.id}, White: ${whitePlayerId}, Black: ${blackPlayerId}`);
            if (user.id === blackPlayerId) {
                setFlippedCombined(true);
                setPlayerName(user.name);
            } else if (user.id === whitePlayerId) {
                setFlippedCombined(false);
                setPlayerName(user.name);
            }
        }
    }, [user, matchmaking, whitePlayerId, blackPlayerId]);

    // Game Clocks State
    const [timers, setTimers] = useState(null); // {w: seconds, b: seconds}
    const [turn, setTurn] = useState('w');
    
    // Sounds
    const moveSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/move-self.mp3"));
    const captureSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/capture.mp3"));
    const castleSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/castle.mp3"));
    const checkSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/move-check.mp3"));
    const gameEndSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_WEBM_/default/game-end.webm"));
    const gameStartSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/game-start.mp3"));
    const promotionSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/promote.mp3"));
    const illegalSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/illegal.mp3"));
    
    // Timer formatting helper
    const formatTime = (seconds) => {
        if (seconds === null || seconds === undefined) return "";
        const s = Math.max(0, Math.floor(seconds));
        const mins = Math.floor(s / 60);
        const secs = s % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    // Live countdown effect
    useEffect(() => {
        if (!timers || isGameOver || moveHistory.length === 0) return;

        const interval = setInterval(() => {
            setTimers(prev => {
                if (!prev) return prev;
                return {
                    ...prev,
                    [turn]: Math.max(0, prev[turn] - 0.1)
                };
            });
        }, 100);

        return () => clearInterval(interval);
    }, [timers, turn, isGameOver, moveHistory.length]);

    const connectWebSocket = (id) => {
        if (ws.current) {
            ws.current.close();
        }

        const wsBase = getWsBase();
        ws.current = new WebSocket(`${wsBase}/${id}`);

        ws.current.onmessage = (event) => {
            const message = JSON.parse(event.data);
            if (message.type === "game_state") {
                if (message.debug_players) {
                    console.log("DEBUG PLAYERS:", message.debug_players);
                }
                setFen(message.fen);
                setInCheck(message.in_check);
                setMoveHistory(message.move_history || []);
                setWinner(message.winner);
                setIsGameOver(message.is_over);
                setTurn(message.turn);
                if (message.clocks) setTimers(message.clocks);
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
                } else if (message.status === "timeout") {
                    console.log("Timeout detected!");
                    gameEndSound.current.play().catch(e => console.error("Error playing game end sound:", e));
                }
                if (message.status === "timeout") {
                    console.log("Timeout detected!");
                    gameEndSound.current.play().catch(e => console.error("Error playing game end sound:", e));
                }
            } else if (message.type === "takeback_offered") {
                console.log("Received takeback_offered:", message);
                console.log(`My User ID: ${user?.id}, Offered by: ${message.by_user_id}`);
                setTakebackOffer({ by_user_id: message.by_user_id });
            } else if (message.type === "takeback_cleared") {
                console.log("Received takeback_cleared");
                setTakebackOffer(null);
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

    const initializeGame = async (fenToLoad = null, variantToLoad = null, tc = null) => {
        const timeControl = tc || (isTimeControlEnabled ? { starting_time: startingTime, increment: increment } : null);
        try {
            const { game_id: newGameId } = await createGame(variantToLoad || variant, fenToLoad, timeControl);
            gameStartSound.current.play().catch(e => console.error("Error playing game start sound:", e));
            navigate(`/game/${newGameId}`, { replace: true });
        } catch (error) {
            console.error("Failed to create new game:", error);
        }
    };

    const loadExistingGame = async (id) => {
        try {
            const data = await getGame(id);
            if (data.game_id) {
                setFen(data.fen);
                setGameId(data.game_id);
                setMoveHistory(data.move_history || []);
                setInCheck(data.in_check);
                setWinner(data.winner);
                setIsGameOver(data.is_over);
                setTurn(data.turn);
                
                if (data.white_player_id) setWhitePlayerId(data.white_player_id);
                if (data.black_player_id) setBlackPlayerId(data.black_player_id);

                connectWebSocket(id);
            }
        } catch (error) {
            console.error("Failed to load game:", error);
            // Fallback to new game if loading fails
            navigate('/', { replace: true });
        }
    };

    useEffect(() => {
        getMe().then(data => {
            if (data.user) {
                setUser(data.user);
                setPlayerName(data.user.name);
            }
        }).catch(e => console.error("Failed to fetch user:", e));
    }, []);

    useEffect(() => {
        if (urlGameId) {
            if (gameId !== urlGameId) {
                loadExistingGame(urlGameId);
            }
        } else {
            initializeGame();
        }
        return () => {
            if (ws.current) {
                ws.current.close();
            }
        };
    }, [variant, urlGameId]);

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
        let file = Math.floor((e.clientX - left) / size)
        let rank = Math.floor((e.clientY - top) / size)
        
        if (isFlipped) {
            file = 7 - file;
            rank = 7 - rank;
        }
        
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
            
            let displayFile = isFlipped ? 7 - file : file;
            let displayRank = isFlipped ? 7 - rank : rank;

            highlightRef.current.style.left = `calc(${displayFile} * var(--square-size))`;
            highlightRef.current.style.top = `calc(${displayRank} * var(--square-size))`;
            
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

    const canMovePiece = (pieceColor) => {
        if (!matchmaking) return true; // Over the board: anyone can move
        if (!user) return false; // Matchmaking requires login
        
        if (pieceColor === 'w') {
            return user.id === whitePlayerId;
        } else {
            return user.id === blackPlayerId;
        }
    };

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
        
        const pieceColor = piece === piece.toUpperCase() ? 'w' : 'b';
        if (!canMovePiece(pieceColor)) return;

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
                    const piece = position[rank][file];
                    const pieceColor = piece === piece.toUpperCase() ? 'w' : 'b';
                    
                    if (canMovePiece(pieceColor)) {
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
                } else {
                    setSelectedSquare(null);
                    setLegalMoves([]);
                }
            }
        } else {
            if (isPiece(file, rank)) {
                const piece = position[rank][file];
                const pieceColor = piece === piece.toUpperCase() ? 'w' : 'b';

                if (canMovePiece(pieceColor)) {
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
        console.log("handleUndo triggered. Matchmaking:", matchmaking);
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            const type = matchmaking ? "takeback_offer" : "undo";
            console.log(`Sending WebSocket message: type=${type}`);
            ws.current.send(JSON.stringify({ type }));
        } else {
            console.error("WebSocket not open. ReadyState:", ws.current?.readyState);
        }
        setIsMenuOpen(false);
    };

    const handleResign = (e) => {
        e.stopPropagation();
        if (window.confirm("Are you sure you want to surrender?")) {
            if (ws.current && ws.current.readyState === WebSocket.OPEN) {
                ws.current.send(JSON.stringify({ type: "resign" }));
            }
        }
    };

    const handleOfferDraw = (e) => {
        e.stopPropagation();
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ type: "draw_offer" }));
        }
    };

    const handleAcceptTakeback = (e) => {
        e.stopPropagation();
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ type: "takeback_accept" }));
        }
    };

    const handleDeclineTakeback = (e) => {
        e.stopPropagation();
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ type: "takeback_decline" }));
        }
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
                <span className="name-text">{isFlipped ? playerName : opponentName}</span>
                {takebackOffer && user && takebackOffer.by_user_id !== user.id && (
                    <span className="takeback-prompt">Accept takeback?</span>
                )}
                {timers && <span className={`clock-display ${turn === (isFlipped ? 'w' : 'b') ? 'active' : ''}`}>{formatTime(timers[isFlipped ? 'w' : 'b'])}</span>}
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
                    {matchmaking ? (
                        <>
                            {takebackOffer && user && takebackOffer.by_user_id !== user.id ? (
                                <div className="takeback-actions">
                                    <button 
                                        onClick={handleAcceptTakeback}
                                        title="Accept Takeback"
                                        className="control-button accept-btn"
                                    >
                                        <svg viewBox="0 0 448 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
                                            <path d="M438.6 105.4c12.5 12.5 12.5 32.8 0 45.3l-256 256c-12.5 12.5-32.8 12.5-45.3 0l-128-128c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0L160 338.7 393.4 105.4c12.5-12.5 32.8-12.5 45.3 0z"/>
                                        </svg>
                                    </button>
                                    <button 
                                        onClick={handleDeclineTakeback}
                                        title="Decline Takeback"
                                        className="control-button decline-btn"
                                    >
                                        <svg viewBox="0 0 384 512" fill="currentColor" style={{ width: 'var(--button-icon-size)', height: 'var(--button-icon-size)' }}>
                                            <path d="M342.6 150.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 210.7 86.6 105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L146.7 256 41.4 361.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192 301.3 297.4 406.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.3 256 342.6 150.6z"/>
                                        </svg>
                                    </button>
                                </div>
                            ) : (
                                <button 
                                    onClick={handleUndo}
                                    title={takebackOffer ? "Takeback Offered..." : "Offer Takeback"}
                                    className={`control-button ${takebackOffer ? 'waiting' : ''}`}
                                    disabled={!!takebackOffer}
                                >
                                    {UNDO_ICON}
                                </button>
                            )}
                            <button 
                                onClick={handleOfferDraw}
                                title="Offer Draw"
                                className="control-button"
                            >
                                {DRAW_ICON}
                            </button>
                            <button 
                                onClick={handleResign}
                                title="Surrender"
                                className="control-button"
                            >
                                {RESIGN_ICON}
                            </button>
                        </>
                    ) : (
                        <>
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
                        </>
                    )}
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
                                                {startingTime === 0.25 ? '1/4' : 
                                                 startingTime === 0.5 ? '1/2' : 
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
                let displayFile = isFlipped ? 7 - file : file;
                let displayRank = isFlipped ? 7 - rank : rank;
                const isDark = (file + rank) % 2 !== 0; // Chessboard pattern
                return <HighlightSquare
                    file={displayFile}
                    rank={displayRank}
                    isDark={isDark}
                />;
            })()}

            {position.map((rankArray, rankIndex) =>
                rankArray.map((pieceType, fileIndex) => {
                    if (!pieceType) return null;
                    
                    let displayFile = isFlipped ? 7 - fileIndex : fileIndex;
                    let displayRank = isFlipped ? 7 - rankIndex : rankIndex;

                    return <Piece
                            key={`p-${rankIndex}-${fileIndex}`}
                            rank={displayRank}
                            file={displayFile}
                            actualFile={fileIndex}
                            actualRank={rankIndex}
                            piece={pieceType}
                            onDragStartCallback={handlePieceDragStart}
                            onDragEndCallback={handlePieceDragEnd}
                            onDropCallback={handleManualDrop}
                            onDragHoverCallback={handlePieceDragHover}
                            isCapture={isCaptureMove(fileIndex, rankIndex)}
                          />;
                })
            )}

            {legalMoves.map((moveUci, index) => {
                const targetSquare = moveUci.slice(2, 4);
                const { file, rank } = algebraicToCoords(targetSquare);
                let displayFile = isFlipped ? 7 - file : file;
                let displayRank = isFlipped ? 7 - rank : rank;
                return <LegalMoveDot key={index} file={displayFile} rank={displayRank} />;
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

                const renderIndicator = (sq, color) => {
                    let displayFile = isFlipped ? 7 - sq.file : sq.file;
                    let displayRank = isFlipped ? 7 - sq.rank : sq.rank;
                    return (
                        <div style={{
                            position: 'absolute',
                            left: `calc(${displayFile} * var(--square-size) + var(--square-size) / 2 - 15px)`,
                            top: `calc(${displayRank} * var(--square-size) + var(--square-size) / 2 - 15px)`,
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
                };

                return (
                    <>
                        {renderIndicator(whiteKingSq, 'w')}
                        {renderIndicator(blackKingSq, 'b')}
                    </>
                );
            })()}

            <div className="player-name-display player-name">
                <span className="name-text">{isFlipped ? opponentName : playerName}</span>
                {timers && <span className={`clock-display ${turn === (isFlipped ? 'b' : 'w') ? 'active' : ''}`}>{formatTime(timers[isFlipped ? 'b' : 'w'])}</span>}
            </div>
        </div>
    );
}