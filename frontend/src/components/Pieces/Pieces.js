import './Pieces.css'
import Piece from './Piece'
import LegalMoveDot from '../LegalMoveDot/LegalMoveDot.js';
import PromotionDialog from '../PromotionDialog/PromotionDialog.js';
import { fenToPosition, coordsToAlgebraic, algebraicToCoords } from '../../helpers.js'
import { createGame, getLegalMoves } from '../../api.js'
import { useState, useRef, useEffect } from 'react'


export function Pieces({ onFenChange }) { // Accept onFenChange prop
    const ref = useRef()
    const [fen, setFen] = useState();
    const [gameId, setGameId] = useState(null);
    const [legalMoves, setLegalMoves] = useState([]);
    const ws = useRef(null);
    const [isPromotionDialogOpen, setPromotionDialogOpen] = useState(false);
    const [promotionMove, setPromotionMove] = useState(null);
    const lastNotifiedFen = useRef(null);

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
                    if (message.status === "checkmate") {
                        console.log("Checkmate detected!");
                    } else if (message.status === "draw") {
                        console.log("Draw detected!");
                    }
                } else if (message.type === "error") {
                    console.error("WebSocket error:", message.message);
                    // You might want to show a message to the user here
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

    // Call onFenChange whenever fen state updates
    useEffect(() => {
        if (fen && fen !== lastNotifiedFen.current) {
            onFenChange(fen);
            lastNotifiedFen.current = fen;
        }
    }, [fen, onFenChange]);

    const position = fen ? fenToPosition(fen) : [];

    const calculateSquare = e => {
        const {width,left,top} = ref.current.getBoundingClientRect()
        const size = width / 8
        const file = Math.floor((e.clientX - left) / size)
        const rank = Math.floor((e.clientY - top) / size)
        return { file, rank, algebraic: coordsToAlgebraic(file, rank) };
    }

    const onDrop = async e => {
        setLegalMoves([]); // Clear legal moves on drop
        const { rank: toRank, algebraic: toSquare } = calculateSquare(e);
        const [piece, fromFileStr, fromRankStr] = e.dataTransfer.getData("text").split(",");
        const fromFileIndex = parseInt(fromFileStr, 10);
        const fromRankIndex = parseInt(fromRankStr, 10);
        const fromSquare = coordsToAlgebraic(fromFileIndex, fromRankIndex);

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
                // You might want to show a message to the user here
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
        try {
            const response = await getLegalMoves(gameId, square);
            if (response.status === "success") {
                setLegalMoves(response.moves); // Array of UCI moves like "e2e4"
            }
        } catch (error) {
            console.error("Failed to fetch legal moves:", error);
        }
    };

    const handlePieceDragEnd = () => {
        setLegalMoves([]);
    };

    const onDragOver = e => e.preventDefault()
    const promotionColor = fen && fen.split(' ')[1] === 'w' ? 'w' : 'b';


    return (
        <div
            className="pieces"
            ref={ref}
            onDragOver={onDragOver}
            onDrop={onDrop}>

            {isPromotionDialogOpen && <PromotionDialog onPromote={handlePromotion} onCancel={handleCancelPromotion} color={promotionColor} />}

            {legalMoves.map((moveUci, index) => {
                // moveUci is like "e2e4". Target is the last 2 chars.
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
                          />
                        : null
                )
            )}
        </div>
    );
}
