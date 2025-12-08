import './Pieces.css'
import Piece from './Piece'
import { fenToPosition, coordsToAlgebraic } from '../../helpers.js'
import { createGame } from '../../api.js'
import { useState, useRef, useEffect } from 'react'


function Pieces() {
    const ref = useRef()
    const [fen, setFen] = useState();
    const ws = useRef(null);

    useEffect(() => {
        const newGame = async () => {
            const { game_id: newGameId, fen: initialFen } = await createGame();
            setFen(initialFen);

            ws.current = new WebSocket(`ws://127.0.0.1:8000/ws/${newGameId}`);

            ws.current.onmessage = (event) => {
                const message = JSON.parse(event.data);
                if (message.type === "game_state") {
                    setFen(message.fen);
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

    const position = fen ? fenToPosition(fen) : [];

    const calculateSquare = e => {
        const {width,left,top} = ref.current.getBoundingClientRect()
        const size = width / 8
        const file = Math.floor((e.clientX - left) / size)
        const rank = Math.floor((e.clientY - top) / size)
        return coordsToAlgebraic(file, rank)
    }

    const onDrop = async e => {
        const toSquare = calculateSquare(e)
        const [, fromFileStr, fromRankStr] = e.dataTransfer.getData("text").split(",")
        const fromFileIndex = parseInt(fromFileStr, 10);
        const fromRankIndex = parseInt(fromRankStr, 10);
        const fromSquare = coordsToAlgebraic(fromFileIndex, fromRankIndex)

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
    const onDragOver = e => e.preventDefault()

    return (
        <div
            className="pieces"
            ref={ref}
            onDragOver={onDragOver}
            onDrop={onDrop}>

            {position.map((rankArray, rankIndex) =>
                rankArray.map((pieceType, fileIndex) =>
                    pieceType
                        ? <Piece
                            key={`p-${rankIndex}-${fileIndex}`}
                            rank={rankIndex}
                            file={fileIndex}
                            piece={pieceType}
                          />
                        : null
                )
            )}
        </div>
    );
}

export default Pieces;
