import './Pieces.css'
import Piece from './Piece'
import LegalMoveDot from '../LegalMoveDot/LegalMoveDot.js';
import HighlightSquare from '../HighlightSquare/HighlightSquare.js';
import PromotionDialog from '../PromotionDialog/PromotionDialog.js';
import { fenToPosition, coordsToAlgebraic, algebraicToCoords } from '../../helpers.js'
import { createGame, getLegalMoves } from '../../api.js'
import { useState, useRef, useEffect } from 'react'


export function Pieces({ onFenChange }) {
    const ref = useRef()
    const [fen, setFen] = useState();
    const [gameId, setGameId] = useState(null);
    const [legalMoves, setLegalMoves] = useState([]);
    const [selectedSquare, setSelectedSquare] = useState(null);
    const [hoveredSquare, setHoveredSquare] = useState(null);
    const [inCheck, setInCheck] = useState(false);
    const ws = useRef(null);
    const [isPromotionDialogOpen, setPromotionDialogOpen] = useState(false);
    const [promotionMove, setPromotionMove] = useState(null);
    const lastNotifiedFen = useRef(null);
    const moveSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/move-self.mp3"));
    const captureSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/capture.mp3"));
    const castleSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/castle.mp3"));
    const checkSound = useRef(new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/move-check.mp3"));

    useEffect(() => {
        const newGame = async () => {
            const { game_id: newGameId, fen: initialFen } = await createGame();
            setFen(initialFen);
            setGameId(newGameId);

            ws.current = new WebSocket(`ws://127.0.0.1:8000/ws/${newGameId}`);

            ws.current.onmessage = (event) => {
                const message = JSON.parse(event.data);
                if (message.type === "game_state") {
                    setFen(message.fen);
                    setInCheck(message.in_check);
                    setSelectedSquare(null);
                    setLegalMoves([]);
                    setHoveredSquare(null);

                    if (message.status === "checkmate") {
                        console.log("Checkmate detected!");
                    } else if (message.status === "draw") {
                        console.log("Draw detected!");
                    }
                } else if (message.type === "error") {
                    console.error("WebSocket error:", message.message);
                }
            };

            ws.current.onclose = () => console.log("WebSocket disconnected");
            ws.current.onerror = (error) => console.error("WebSocket error:", error);
        };
        newGame();

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
        if (!clientX || !clientY) {
            setHoveredSquare(null);
            return;
        }
        const { file, rank } = calculateSquare({ clientX, clientY });
        if (file >= 0 && file <= 7 && rank >= 0 && rank <= 7) {
             setHoveredSquare({ file, rank });
        } else {
             setHoveredSquare(null);
        }
    }

    const handleManualDrop = ({ clientX, clientY, piece, file, rank }) => {
        setHoveredSquare(null);
        // Mock event object for calculateSquare
        const mockEvent = { clientX, clientY };
        const { rank: toRank, algebraic: toSquare } = calculateSquare(mockEvent);
        
        const fromSquare = coordsToAlgebraic(file, rank);

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

    const handlePieceDragStart = async ({ file, rank, piece }) => {
        if (!gameId) return;
        const square = coordsToAlgebraic(file, rank);
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

    const promotionColor = fen && fen.split(' ')[1] === 'w' ? 'w' : 'b';


    return (
        <div
            className="pieces"
            ref={ref}
            onClick={handleSquareClick}
            >

            {isPromotionDialogOpen && <PromotionDialog onPromote={handlePromotion} onCancel={handleCancelPromotion} color={promotionColor} />}

            {hoveredSquare && (
                <div style={{
                    position: 'absolute',
                    left: `calc(${hoveredSquare.file} * var(--square-size))`,
                    top: `calc(${hoveredSquare.rank} * var(--square-size))`,
                    width: 'var(--square-size)',
                    height: 'var(--square-size)',
                    border: (hoveredSquare.file + hoveredSquare.rank) % 2 !== 0 
                        ? '5px solid rgba(100, 100, 100, 0.5)' // Darker border for dark squares
                        : '5px solid rgba(255, 255, 255, 0.8)', // Very light grey (white-ish) for light squares
                    boxSizing: 'border-box',
                    zIndex: 5, 
                    pointerEvents: 'none'
                }}/>
            )}

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
                          />
                        : null
                )
            )}
        </div>
    );
}
