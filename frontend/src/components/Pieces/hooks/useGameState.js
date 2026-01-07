import { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { fenToPosition, algebraicToCoords, coordsToAlgebraic } from '../../../helpers';
import { getGameFens, getGame, createGame, getAllLegalMoves } from '../../../api';
import SoundManager from '../../../helpers/soundManager';

export function useGameState(urlGameId, variant, computer, navigate) {
    const [fen, setFen] = useState();
    const [fenHistory, setFenHistory] = useState([]);
    const fenHistoryRef = useRef([]);
    const [viewedIndex, setViewedIndex] = useState(-1);
    const [gameId, setGameId] = useState(null);
    const [inCheck, setInCheck] = useState(false);
    const [moveHistory, setMoveHistory] = useState([]);
    const [lastMove, setLastMove] = useState(null);
    const [winner, setWinner] = useState(null);
    const [isGameOver, setIsGameOver] = useState(false);
    const [turn, setTurn] = useState('w');
    const [currentVariant, setCurrentVariant] = useState(variant);
    const [ratingDiffs, setRatingDiffs] = useState(null);
    const [allPossibleMoves, setAllPossibleMoves] = useState([]);
    
    const [whitePlayer, setWhitePlayer] = useState({ name: "Anonymous", rating: 1500 });
    const [blackPlayer, setBlackPlayer] = useState({ name: "Anonymous", rating: 1500 });
    const [whitePlayerId, setWhitePlayerId] = useState(null);
    const [blackPlayerId, setBlackPlayerId] = useState(null);

    const [takebackOffer, setTakebackOffer] = useState(null);
    const [drawOffer, setDrawOffer] = useState(null);

    // Effects state
    const [explosionSquare, setExplosionSquare] = useState(null);
    const [showExplosion, setShowExplosion] = useState(false);
    const [dropSquare, setDropSquare] = useState(null);
    const [showDropWarp, setShowDropWarp] = useState(false);
    const [checkCounts, setCheckCounts] = useState([0, 0]);
    const [strikeSquare, setStrikeSquare] = useState(null);
    const [showStrike, setShowStrike] = useState(false);
    const [turboSquare, setTurboSquare] = useState(null);
    const [showTurbo, setShowTurbo] = useState(false);
    const [shatterSquare, setShatterSquare] = useState(null);
    const [showShatter, setShowShatter] = useState(false);
    const [shake, setShake] = useState(0);

    useEffect(() => {
        fenHistoryRef.current = fenHistory;
    }, [fenHistory]);

    const fetchLegalMoves = useCallback(async () => {
        if (!gameId) return;
        try {
            const data = await getAllLegalMoves(gameId);
            if (data.moves) {
                setAllPossibleMoves(data.moves);
                if (data.debug_rejections) {
                    console.log(`[DEBUG] Move rejections for game ${gameId}:`, data.debug_rejections);
                }
                if (data.validators) {
                    console.log(`[DEBUG] Validators being used for game ${gameId}:`, data.validators);
                }
                console.log(`[DEBUG] Legal moves for FEN ${fen}:`, data.moves);
            }
        } catch (err) {
            console.error("Error fetching legal moves:", err);
        }
    }, [gameId, fen]);

    useEffect(() => {
        if (gameId) {
            fetchLegalMoves(gameId);
        }
    }, [gameId, fen, fetchLegalMoves]);

    useEffect(() => {
        if (allPossibleMoves.length > 0) {
            console.log(`[DEBUG] Legal moves for FEN ${fen}:`, allPossibleMoves);
        }
    }, [allPossibleMoves, fen]);

    const initializeGame = useCallback(async (fenToLoad = null, variantToLoad = null, tc = null) => {
        try {
            const { game_id: newGameId, fen: initialFen } = await createGame(variantToLoad || variant, fenToLoad, tc, "white", computer);
            setFen(initialFen);
            setFenHistory([initialFen]);
            setViewedIndex(0);
            SoundManager.play('gameStart');
            const route = computer ? `/computer-game/${newGameId}` : `/game/${newGameId}`;
            navigate(route, { replace: true });
        } catch (error) {
            console.error("Failed to create new game:", error);
        }
    }, [variant, computer, navigate]);

    const loadExistingGame = useCallback(async (id) => {
        try {
            const data = await getGame(id);
            if (data.game_id) {
                setFen(data.fen);
                setGameId(data.game_id);
                setMoveHistory(data.move_history || []);
                
                getGameFens(id).then(histData => {
                    if (histData.fens) {
                        setFenHistory(histData.fens);
                        setViewedIndex(histData.fens.length - 1);
                    }
                }).catch(console.error);
                
                const uciHistory = data.uci_history || [];
                if (uciHistory.length > 0) {
                    const last = uciHistory[uciHistory.length - 1];
                    setLastMove({ from: last.substring(0, 2), to: last.substring(2, 4) });
                } else {
                    setLastMove(null);
                }

                setInCheck(data.in_check);
                setWinner(data.winner);
                setIsGameOver(data.is_over);
                setTurn(data.turn);
                if (data.variant) setCurrentVariant(data.variant.toLowerCase());
                if (data.rating_diffs) setRatingDiffs(data.rating_diffs);
                
                if (data.white_player) {
                    setWhitePlayer(data.white_player);
                    setWhitePlayerId(data.white_player.id);
                }
                if (data.black_player) {
                    setBlackPlayer(data.black_player);
                    setBlackPlayerId(data.black_player.id);
                }
            }
        } catch (error) {
            console.error("Failed to load game:", error);
            navigate('/', { replace: true });
        }
    }, [navigate]);

    const position = useMemo(() => {
        const sourceFen = viewedIndex >= 0 ? fenHistory[viewedIndex] : fen;
        if (!sourceFen) return [];
        return fenToPosition(sourceFen);
    }, [fen, fenHistory, viewedIndex]);

    const memoizedEffects = useMemo(() => ({
        explosionSquare, setExplosionSquare,
        showExplosion, setShowExplosion,
        dropSquare, setDropSquare,
        showDropWarp, setShowDropWarp,
        checkCounts, setCheckCounts,
        strikeSquare, setStrikeSquare,
        showStrike, setShowStrike,
        turboSquare, setTurboSquare,
        showTurbo, setShowTurbo,
        shatterSquare, setShatterSquare,
        showShatter, setShowShatter,
        shake, setShake
    }), [
        explosionSquare, showExplosion, dropSquare, showDropWarp, 
        checkCounts, strikeSquare, showStrike, turboSquare, 
        showTurbo, shatterSquare, showShatter, shake
    ]);

    return {
        fen, setFen,
        fenHistory, setFenHistory,
        fenHistoryRef,
        viewedIndex, setViewedIndex,
        gameId, setGameId,
        inCheck, setInCheck,
        moveHistory, setMoveHistory,
        lastMove, setLastMove,
        winner, setWinner,
        isGameOver, setIsGameOver,
        turn, setTurn,
        currentVariant, setCurrentVariant,
        ratingDiffs, setRatingDiffs,
        allPossibleMoves, setAllPossibleMoves,
        whitePlayer, setWhitePlayer,
        blackPlayer, setBlackPlayer,
        whitePlayerId, setWhitePlayerId,
        blackPlayerId, setBlackPlayerId,
        takebackOffer, setTakebackOffer,
        drawOffer, setDrawOffer,
        fetchLegalMoves,
        initializeGame,
        loadExistingGame,
        position,
        effects: memoizedEffects
    };
}
