import { useEffect, useRef } from 'react';
import SoundManager from '../../../helpers/soundManager';
import { getWsBase } from '../../../api';

export function useGameWebSocket({
    gameId,
    currentVariant,
    setFen,
    setFenHistory,
    setViewedIndex,
    setInCheck,
    setMoveHistory,
    setWinner,
    setIsGameOver,
    setTurn,
    setTimers,
    setRatingDiffs,
    setLastMove,
    setTakebackOffer,
    setDrawOffer,
    effects
}) {
    const ws = useRef(null);
    const connectedGameId = useRef(null);
    
    // Use refs to avoid stale closures in onmessage while keeping dependencies stable
    const refs = useRef({});
    useEffect(() => {
        refs.current = {
            currentVariant, setFen, setFenHistory, setViewedIndex,
            setInCheck, setMoveHistory, setWinner, setIsGameOver, setTurn,
            setTimers, setRatingDiffs, setLastMove, setTakebackOffer, setDrawOffer, effects
        };
    });

    useEffect(() => {
        if (!gameId) return;
        if (ws.current && connectedGameId.current === gameId) {
            console.log(`WebSocket already connected for game: ${gameId}`);
            return;
        }

        const wsBase = getWsBase();
        
        // Close existing connection if gameId has changed
        if (ws.current) {
            console.log(`Closing previous WebSocket for game: ${connectedGameId.current}`);
            ws.current.close();
        }

        console.log(`Connecting to WebSocket: ${wsBase}/${gameId}`);
        ws.current = new WebSocket(`${wsBase}/${gameId}`);
        connectedGameId.current = gameId;

        ws.current.onmessage = (event) => {
            const message = JSON.parse(event.data);
            const { 
                setFen, setFenHistory, setViewedIndex, setInCheck, setMoveHistory,
                setWinner, setIsGameOver, setTurn, setTimers, setRatingDiffs,
                setLastMove, setTakebackOffer, setDrawOffer, currentVariant, effects
            } = refs.current;

            if (message.type === "game_state") {
                setFen(message.fen);
                setFenHistory(prev => (prev[prev.length - 1] !== message.fen ? [...prev, message.fen] : prev));
                setViewedIndex(-1);
                setInCheck(message.in_check);
                setMoveHistory(message.move_history || []);
                setWinner(message.winner);
                setIsGameOver(message.is_over);
                setTurn(message.turn);
                if (message.clocks) setTimers(message.clocks);
                if (message.rating_diffs) setRatingDiffs(message.rating_diffs);
                
                const uciHistory = message.uci_history || [];
                if (uciHistory.length > 0) {
                    const last = uciHistory[uciHistory.length - 1];
                    setLastMove({ from: last.substring(0, 2), to: last.substring(2, 4) });
                }

                // Handle variant specific effects
                if (currentVariant === 'atomic' && message.explosion_square) {
                    effects.setExplosionSquare(message.explosion_square);
                    effects.setShowExplosion(true);
                    SoundManager.play('explosion');
                    setTimeout(() => effects.setShowExplosion(false), 1000);
                }
            } else if (message.type === "takeback_offered") {
                setTakebackOffer({ by_user_id: message.by_user_id });
            } else if (message.type === "draw_offered") {
                setDrawOffer({ by_user_id: message.by_user_id });
            } else if (message.type === "takeback_cleared") {
                setTakebackOffer(null);
            } else if (message.type === "draw_cleared") {
                setDrawOffer(null);
            }
        };

        return () => {
            console.log("Cleaning up WebSocket for game:", gameId);
            if (ws.current) {
                ws.current.close();
                ws.current = null;
                connectedGameId.current = null;
            }
        };
    }, [gameId]);

    return ws;
}

