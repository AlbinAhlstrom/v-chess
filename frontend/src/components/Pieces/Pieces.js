import './Pieces.css'
import Piece from './Piece'
import LegalMoveDot from '../LegalMoveDot/LegalMoveDot.js';
import HighlightSquare from '../HighlightSquare/HighlightSquare.js';
import PromotionDialog from '../PromotionDialog/PromotionDialog.js';
import ImportDialog from '../ImportDialog/ImportDialog.js';
import { fenToPosition, coordsToAlgebraic, algebraicToCoords } from '../../helpers.js'
import { createGame, getAllLegalMoves, getGame, getMe, login, logout, getWsBase } from '../../api.js'
import { useState, useRef, useEffect, useCallback, useMemo } from 'react'
import { useNavigate, useParams } from 'react-router-dom';

// Subcomponents
import GameSidebar from './subcomponents/GameSidebar';
import NewGameDialog from './subcomponents/NewGameDialog';
import PlayerNameDisplay from './subcomponents/PlayerNameDisplay';
import GameOverIndicator from './subcomponents/GameOverIndicator';

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

const getAutoPromotePreference = () => {
    const saved = localStorage.getItem('autoPromoteToQueen');
    return saved !== null ? JSON.parse(saved) : true;
};

export function Pieces({ onFenChange, variant = "standard", matchmaking = false, computer = false, setFlipped }) {
    const { gameId: urlGameId } = useParams();
    const ref = useRef()
    const highlightRef = useRef(null);
    // ... rest of state stays same ...
    // Note: I'll actually just find the function below to change it correctly.

    const [fen, setFen] = useState();
    const [gameId, setGameId] = useState(null);
    const [legalMoves, setLegalMoves] = useState([]);
    const [allPossibleMoves, setAllPossibleMoves] = useState([]);
    const [selectedSquare, setSelectedSquare] = useState(null);
    const [inCheck, setInCheck] = useState(false);
    const [flashKingSquare, setFlashKingSquare] = useState(null);
    const [moveHistory, setMoveHistory] = useState([]);
    const [lastMove, setLastMove] = useState(null); // { from: 'e2', to: 'e4' }
    const [winner, setWinner] = useState(null);
    const [isGameOver, setIsGameOver] = useState(false);
    const [ratingDiffs, setRatingDiffs] = useState(null);
    const ws = useRef(null);
    const [isPromotionDialogOpen, setPromotionDialogOpen] = useState(false);
    const [isImportDialogOpen, setImportDialogOpen] = useState(false);
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
    const [whitePlayer, setWhitePlayer] = useState({ name: "Anonymous", rating: 1500 });
    const [blackPlayer, setBlackPlayer] = useState({ name: "Anonymous", rating: 1500 });
    const [whitePlayerId, setWhitePlayerId] = useState(null);
    const [blackPlayerId, setBlackPlayerId] = useState(null);
    const [takebackOffer, setTakebackOffer] = useState(null); // { by_user_id: number }

    const fetchLegalMoves = useCallback((id) => {
        if (!id) return;
        getAllLegalMoves(id).then(response => {
            if (response.status === "success") {
                setAllPossibleMoves(response.moves);
            }
        }).catch(error => {
            console.error("Failed to fetch all legal moves:", error);
        });
    }, []);

    // Effect to handle board flipping and player names once both user and game data are available
    useEffect(() => {
        if (matchmaking && (whitePlayerId || blackPlayerId)) {
            if (user && user.id === blackPlayerId) {
                setFlippedCombined(true);
            } else if (user && user.id === whitePlayerId) {
                setFlippedCombined(false);
            } else if (whitePlayerId === "computer") {
                // If I'm playing against computer as black (computer is white)
                setFlippedCombined(true);
            } else if (blackPlayerId === "computer") {
                // If I'm playing against computer as white (computer is black)
                setFlippedCombined(false);
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
                setFen(message.fen);
                setInCheck(message.in_check);
                const history = message.move_history || [];
                setMoveHistory(history);
                
                if (history.length > 0) {
                    const last = history[history.length - 1];
                    // UCI moves are typically 4 chars (e2e4) or 5 for promotions (e7e8q)
                    const from = last.substring(0, 2);
                    const to = last.substring(2, 4);
                    console.log(`DEBUG: Last move detected: ${last} (from: ${from}, to: ${to})`);
                    setLastMove({ from, to });
                } else {
                    setLastMove(null);
                }

                setWinner(message.winner);
                setIsGameOver(message.is_over);
                setTurn(message.turn);
                if (message.clocks) setTimers(message.clocks);
                if (message.rating_diffs) setRatingDiffs(message.rating_diffs);
                setSelectedSquare(null);
                setLegalMoves([]);
                if (highlightRef.current) highlightRef.current.style.display = 'none';

                if (message.status === "checkmate" || message.status === "draw" || message.status === "game_over" || message.status === "timeout") {
                    gameEndSound.current.play().catch(e => console.error("Error playing game end sound:", e));
                }
            } else if (message.type === "takeback_offered") {
                setTakebackOffer({ by_user_id: message.by_user_id });
            } else if (message.type === "takeback_cleared") {
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

        ws.current.onclose = () => {};
        ws.current.onerror = (error) => console.error("WebSocket error:", error);
    };

    const initializeGame = async (fenToLoad = null, variantToLoad = null, tc = null) => {
        const timeControl = tc || (isTimeControlEnabled ? { starting_time: startingTime, increment: increment } : null);
        console.log("Initializing game with TC:", timeControl);
        try {
            const { game_id: newGameId } = await createGame(variantToLoad || variant, fenToLoad, timeControl, "white", computer);
            gameStartSound.current.play().catch(e => console.error("Error playing game start sound:", e));
            const route = computer ? `/computer-game/${newGameId}` : `/game/${newGameId}`;
            navigate(route, { replace: true });
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
                const history = data.move_history || [];
                setMoveHistory(history);
                
                if (history.length > 0) {
                    const last = history[history.length - 1];
                    const from = last.substring(0, 2);
                    const to = last.substring(2, 4);
                    setLastMove({ from, to });
                } else {
                    setLastMove(null);
                }

                setInCheck(data.in_check);
                setWinner(data.winner);
                setIsGameOver(data.is_over);
                setTurn(data.turn);
                if (data.rating_diffs) setRatingDiffs(data.rating_diffs);
                
                if (data.white_player) {
                    setWhitePlayer(data.white_player);
                    setWhitePlayerId(data.white_player.id);
                }
                if (data.black_player) {
                    setBlackPlayer(data.black_player);
                    setBlackPlayerId(data.black_player.id);
                }

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
            fetchLegalMoves(gameId);
        }
    }, [fen, onFenChange, inCheck, gameId, fetchLegalMoves]);

    const position = useMemo(() => fen ? fenToPosition(fen) : [], [fen]);

    const calculateSquare = useCallback(e => {
        const {width,left,top} = ref.current.getBoundingClientRect()
        const size = width / 8
        let file = Math.floor((e.clientX - left) / size)
        let rank = Math.floor((e.clientY - top) / size)
        
        if (isFlipped) {
            file = 7 - file;
            rank = 7 - rank;
        }
        
        return { file, rank, algebraic: coordsToAlgebraic(file, rank) };
    }, [isFlipped]);

    const handlePieceDragHover = useCallback((clientX, clientY) => {
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
    }, [calculateSquare, isFlipped]);

    const renderPiece = (pieceType, fileIndex, rankIndex) => {
        let displayFile = isFlipped ? 7 - fileIndex : fileIndex;
        let displayRank = isFlipped ? 7 - rankIndex : rankIndex;

        return (
            <Piece
                key={`p-${rankIndex}-${fileIndex}`}
                rank={displayRank}
                file={displayFile}
                actualRank={rankIndex}
                actualFile={fileIndex}
                piece={pieceType}
                onDragStartCallback={handlePieceDragStart}
                onDragEndCallback={handlePieceDragEnd}
                onDropCallback={handleManualDrop}
                onDragHoverCallback={handlePieceDragHover}
              />
        );
    };

    const renderLegalMove = (moveUci, index) => {
        const targetSquare = moveUci.slice(2, 4);
        const { file, rank } = algebraicToCoords(targetSquare);
        let displayFile = isFlipped ? 7 - file : file;
        let displayRank = isFlipped ? 7 - rank : rank;
        return <LegalMoveDot key={index} file={displayFile} rank={displayRank} />;
    };

    const renderHighlight = (square, color, keyPrefix = 'highlight') => {
        const { file, rank } = algebraicToCoords(square);
        let displayFile = isFlipped ? 7 - file : file;
        let displayRank = isFlipped ? 7 - rank : rank;
        const isDark = (file + rank) % 2 !== 0;
        return <HighlightSquare
            key={`${keyPrefix}-${square}`}
            file={displayFile}
            rank={displayRank}
            isDark={isDark}
            color={color}
        />;
    };

    const handleManualDrop = useCallback(({ clientX, clientY, piece, file, rank }) => {
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

        // If auto-promote is OFF, check for promotion to show dialog
        if (!getAutoPromotePreference()) {
            const actualPiece = position[rank][file];
            const isPawn = actualPiece?.toLowerCase() === 'p';
            const isWhite = actualPiece === 'P';
            const isPromotionRow = isWhite ? toRank === 0 : toRank === 7;
            
            if (isPawn && isPromotionRow) {
                setPromotionMove({ from: fromSquare, to: toSquare });
                setPromotionDialogOpen(true);
                return;
            }
        } else {
            // Auto-promote check for drag-drop
            const actualPiece = position[rank][file];
            const isPawn = actualPiece?.toLowerCase() === 'p';
            const isWhite = actualPiece === 'P';
            const isPromotionRow = isWhite ? toRank === 0 : toRank === 7;
            
            if (isPawn && isPromotionRow) {
                const moveUci = `${fromSquare}${toSquare}q`;
                if (ws.current && ws.current.readyState === WebSocket.OPEN) {
                    ws.current.send(JSON.stringify({ type: "move", uci: moveUci }));
                }
                return;
            }
        }

        try {
            const moveUci = `${fromSquare}${toSquare}`;
            if (ws.current && ws.current.readyState === WebSocket.OPEN) {
                ws.current.send(JSON.stringify({ type: "move", uci: moveUci }));
            }
        } catch (error) {
            console.error("Failed to make move:", error);
        }
    }, [calculateSquare, position]);

    const canMovePiece = useCallback((pieceColor) => {
        // In OTB or against Computer, allow all selections (backend enforces actual move legality)
        if (!matchmaking || computer || whitePlayerId === "computer" || blackPlayerId === "computer") return true;
        
        if (!user || !user.id) return false; // Matchmaking requires login
        
        if (pieceColor === 'w') {
            return String(user.id) === String(whitePlayerId);
        } else {
            return String(user.id) === String(blackPlayerId);
        }
    }, [matchmaking, computer, user, whitePlayerId, blackPlayerId]);

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

    useEffect(() => {
        // Fetch moves immediately when gameId is set (for initial load)
        if (gameId) {
            fetchLegalMoves(gameId);
        }
    }, [gameId, fetchLegalMoves]);

    const handlePieceDragStart = useCallback(async ({ file, rank, piece }) => {
        if (!gameId || isGameOver) return;
        
        const pieceColor = piece === piece.toUpperCase() ? 'w' : 'b';
        if (!canMovePiece(pieceColor)) return;

        const square = coordsToAlgebraic(file, rank);
        
        dragStartSelectionState.current = (selectedSquare === square);
        setSelectedSquare(square);
        
        const moves = allPossibleMoves.filter(m => m.startsWith(square));
        setLegalMoves(moves);
    }, [gameId, isGameOver, canMovePiece, selectedSquare, allPossibleMoves]);

    const handlePieceDragEnd = useCallback(() => {
        
    }, []);

    const handleSquareClick = useCallback(async (e) => {
        if (!gameId || !fen || isGameOver) return;

        const { file, rank, algebraic: clickedSquare } = calculateSquare(e);


        const isPiece = (f, r) => {
            if (r < 0 || r > 7 || f < 0 || f > 7) return false;
            const piece = position[r][f];
            return !!piece;
        };

        if (selectedSquare) {
            const movesToTarget = legalMoves.filter(m => m.slice(2, 4) === clickedSquare);

            if (movesToTarget.length > 0) {
                // Check if we should show promotion dialog
                let shouldShowDialog = false;
                
                if (!getAutoPromotePreference()) {
                    const { file: fromFile, rank: fromRank } = algebraicToCoords(selectedSquare);
                    const startPiece = position[fromRank][fromFile];
                    const isPawn = startPiece?.toLowerCase() === 'p';
                    const isWhite = startPiece === 'P';
                    const isPromotionRow = isWhite ? rank === 0 : rank === 7;
                    if (isPawn && isPromotionRow) shouldShowDialog = true;
                }

                if (shouldShowDialog || movesToTarget.length > 1 || movesToTarget[0].length === 5) {
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
                        const moves = allPossibleMoves.filter(m => m.startsWith(clickedSquare));
                        setLegalMoves(moves);
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
                    const moves = allPossibleMoves.filter(m => m.startsWith(clickedSquare));
                    setLegalMoves(moves);
                }
            }
        }
    }, [gameId, fen, isGameOver, calculateSquare, position, selectedSquare, legalMoves, canMovePiece, allPossibleMoves]);

    const handleNewGameClick = (e) => {
        e.stopPropagation();
        navigate('/create-game');
        setIsMenuOpen(false);
    };

    const handleReset = (e) => {
        e.stopPropagation();
        initializeGame();
        setIsMenuOpen(false);
    };

    const handleUndo = (e) => {
        e.stopPropagation();
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            const isComputerGame = computer || whitePlayerId === "computer" || blackPlayerId === "computer";
            const type = (matchmaking && !isComputerGame) ? "takeback_offer" : "undo";
            ws.current.send(JSON.stringify({ type }));
        } else {
            console.error("WebSocket not open. ReadyState:", ws.current?.readyState);
        }
        setIsMenuOpen(false);
    };

    const handleResign = (e) => {
        e.stopPropagation();
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ type: "resign" }));
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

    const topPlayer = isFlipped ? whitePlayer : blackPlayer;
    const bottomPlayer = isFlipped ? blackPlayer : whitePlayer;

    const whiteDiff = ratingDiffs ? ratingDiffs.white_diff : null;
    const blackDiff = ratingDiffs ? ratingDiffs.black_diff : null;
    
    const topDiff = isFlipped ? whiteDiff : blackDiff;
    const bottomDiff = isFlipped ? blackDiff : whiteDiff;

        return (

            <div

                className="pieces"

                ref={ref}

                onClick={(e) => {

                    handleSquareClick(e);

                    if (isMenuOpen) setIsMenuOpen(false);

                }}

                >

                

                <PlayerNameDisplay 
                    isOpponent={true}
                    isFlipped={isFlipped}
                    player={topPlayer}
                    ratingDiff={topDiff}
                    takebackOffer={takebackOffer}
                    user={user}
                    timers={timers}
                    turn={turn}
                    formatTime={formatTime}
                    matchmaking={matchmaking}
                />

    

                <GameSidebar 
                    matchmaking={matchmaking}
                    moveHistory={moveHistory}
                    handleUndo={handleUndo}
                    handleReset={handleReset}
                    handleNewGameClick={handleNewGameClick}
                    handleMenuToggle={handleMenuToggle}
                    handleResign={handleResign}
                    handleOfferDraw={handleOfferDraw}
                    handleAcceptTakeback={handleAcceptTakeback}
                    handleDeclineTakeback={handleDeclineTakeback}
                    isMenuOpen={isMenuOpen}
                    copyFenToClipboard={copyFenToClipboard}
                    handleImportClick={handleImportClick}
                    takebackOffer={takebackOffer}
                    user={user}
                    isGameOver={isGameOver}
                />

                {isPromotionDialogOpen && <PromotionDialog onPromote={handlePromotion} onCancel={handleCancelPromotion} color={promotionColor} />}

                {isImportDialogOpen && <ImportDialog onImport={handleImport} onCancel={handleCancelImport} />}

    

                {selectedSquare && renderHighlight(selectedSquare, null, 'selected')}
                {lastMove && renderHighlight(lastMove.from, 'var(--last-move-highlight)', 'last-from')}
                {lastMove && renderHighlight(lastMove.to, 'var(--last-move-highlight)', 'last-to')}

    

                {position.map((rankArray, rankIndex) =>

                    rankArray.map((pieceType, fileIndex) => 

                        pieceType ? renderPiece(pieceType, fileIndex, rankIndex) : null

                    )

                )}

    

                {!isGameOver && legalMoves.map((moveUci, index) => renderLegalMove(moveUci, index))}

    

                <GameOverIndicator 

                    isGameOver={isGameOver}

                    position={position}

                    winner={winner}

                    isFlipped={isFlipped}

                />

    

                <PlayerNameDisplay 
                    isOpponent={false}
                    isFlipped={isFlipped}
                    player={bottomPlayer}
                    ratingDiff={bottomDiff}
                    takebackOffer={takebackOffer}
                    user={user}
                    timers={timers}
                    turn={turn}
                    formatTime={formatTime}
                    matchmaking={matchmaking}
                />

            </div>

        );

    }

    