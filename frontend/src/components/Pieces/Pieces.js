import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './Pieces.css';

// Components & Helpers
import Piece from './Piece';
import LegalMoveDot from '../LegalMoveDot/LegalMoveDot.js';
import HighlightSquare from '../HighlightSquare/HighlightSquare.js';
import ImportDialog from '../ImportDialog/ImportDialog.js';
import Confetti from '../Rules/Confetti';
import { algebraicToCoords } from '../../helpers.js';

// Subcomponents
import GameSidebar from './subcomponents/GameSidebar';
import PlayerNameDisplay from './subcomponents/PlayerNameDisplay';
import GameOverIndicator from './subcomponents/GameOverIndicator';
import { BoardEffects } from './subcomponents/BoardEffects';
import { PromotionManager } from './subcomponents/PromotionManager';

// Hooks
import { useUserSession } from './hooks/useUserSession';
import { useGameState } from './hooks/useGameState';
import { useGameClock } from './hooks/useGameClock';
import { useAudioFeedback } from './hooks/useAudioFeedback';
import { useBoardInteraction } from './hooks/useBoardInteraction';
import { useGameWebSocket } from './hooks/useGameWebSocket';

const getAutoPromotePreference = () => {
    const saved = localStorage.getItem('autoPromoteToQueen');
    return saved !== null ? JSON.parse(saved) : true;
};

export function Pieces({ onFenChange, variant = "standard", matchmaking = false, computer = false, setFlipped, setIsLatest }) {
    const { gameId: urlGameId } = useParams();
    const navigate = useNavigate();
    const [isFlipped, setIsFlippedLocal] = useState(false);
    
    const {
        user,
        startingTime,
        setStartingTime,
        increment,
        setIncrement,
        isTimeControlEnabled,
        setIsTimeControlEnabled
    } = useUserSession();

    const {
        fen, setFen,
        fenHistory, setFenHistory,
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
        allPossibleMoves,
        whitePlayer, setWhitePlayer,
        blackPlayer, setBlackPlayer,
        whitePlayerId, setWhitePlayerId,
        blackPlayerId, setBlackPlayerId,
        takebackOffer, setTakebackOffer,
        drawOffer, setDrawOffer,
        initializeGame,
        loadExistingGame,
        position,
        effects
    } = useGameState(urlGameId, variant, computer, navigate);

    const { timers, setTimers, formatTime } = useGameClock(isGameOver, moveHistory.length, turn);
    const { isPromoting } = useAudioFeedback(
        viewedIndex >= 0 ? fenHistory[viewedIndex] : fen, 
        inCheck, isGameOver, gameId, onFenChange
    );

    const ws = useGameWebSocket({
        gameId, currentVariant, setFen, setFenHistory, setViewedIndex,
        setInCheck, setMoveHistory, setWinner, setIsGameOver, setTurn,
        setTimers, setRatingDiffs, setLastMove, setTakebackOffer, setDrawOffer, effects
    });

    const [isPromotionDialogOpen, setPromotionDialogOpen] = useState(false);
    const [isImportDialogOpen, setImportDialogOpen] = useState(false);
    const [promotionMove, setPromotionMove] = useState(null);
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    const setFlippedCombined = useCallback((val) => {
        setIsFlippedLocal(val);
        if (setFlipped) setFlipped(val);
    }, [setFlipped]);

    const canMovePiece = useCallback((pieceColor) => {
        if (!matchmaking || computer || whitePlayerId === "computer" || blackPlayerId === "computer") return true;
        if (!user || !user.id) return false;
        return pieceColor === 'w' ? String(user.id) === String(whitePlayerId) : String(user.id) === String(blackPlayerId);
    }, [matchmaking, computer, user, whitePlayerId, blackPlayerId]);

    const onMoveAttempt = useCallback((from, to, movesToTarget) => {
        let shouldShowDialog = false;
        const { rank: fromRank, file: fromFile } = algebraicToCoords(from);
        const actualPiece = position[fromRank][fromFile];
        const isPawn = actualPiece?.toLowerCase() === 'p';
        const isWhite = actualPiece === 'P';
        const { rank: toRank } = algebraicToCoords(to);
        const isPromotionRow = isWhite ? toRank === 0 : toRank === 7;

        if (isPawn && isPromotionRow) {
            if (!getAutoPromotePreference() || movesToTarget.length > 1 || movesToTarget[0].length === 5) {
                shouldShowDialog = true;
            } else {
                const moveUci = `${from}${to}q`;
                ws.current?.send(JSON.stringify({ type: "move", uci: moveUci }));
                return;
            }
        }

        if (shouldShowDialog) {
            setPromotionMove({ from, to });
            setPromotionDialogOpen(true);
        } else {
            const moveUci = movesToTarget[0];
            ws.current?.send(JSON.stringify({ type: "move", uci: moveUci }));
        }
    }, [position, ws]);

    const {
        selectedSquare, setSelectedSquare,
        legalMoves, setLegalMoves,
        ref, highlightRef,
        handleSquareClick,
        handlePieceDragStart,
        handlePieceDragHover,
        handleManualDrop
    } = useBoardInteraction(isFlipped, position, allPossibleMoves, canMovePiece, onMoveAttempt);

    const initializingRef = useRef(false);

    useEffect(() => {
        if (urlGameId) {
            if (gameId !== urlGameId) loadExistingGame(urlGameId);
        } else if (!gameId && !initializingRef.current) {
            initializingRef.current = true;
            initializeGame();
        }
    }, [urlGameId, gameId, loadExistingGame, initializeGame]);

    useEffect(() => {
        if (matchmaking && (whitePlayerId || blackPlayerId)) {
            if (user?.id === blackPlayerId || whitePlayerId === "computer") setFlippedCombined(user?.id === blackPlayerId);
            else if (user?.id === whitePlayerId || blackPlayerId === "computer") setFlippedCombined(user?.id === blackPlayerId);
        }
    }, [user, matchmaking, whitePlayerId, blackPlayerId, setFlippedCombined]);

    const handlePromotion = (piece) => {
        if (promotionMove) {
            isPromoting.current = true;
            ws.current?.send(JSON.stringify({ type: "move", uci: `${promotionMove.from}${promotionMove.to}${piece}` }));
        }
        setPromotionDialogOpen(false);
        setPromotionMove(null);
    };

    const renderHighlight = (square, color, keyPrefix) => {
        const { file, rank } = algebraicToCoords(square);
        const displayFile = isFlipped ? 7 - file : file;
        const displayRank = isFlipped ? 7 - rank : rank;
        return <HighlightSquare key={`${keyPrefix}-${square}`} file={displayFile} rank={displayRank} isDark={(file + rank) % 2 !== 0} color={color} />;
    };

    const isLatest = viewedIndex === -1 || viewedIndex === fenHistory.length - 1;
    useEffect(() => { if (setIsLatest) setIsLatest(isLatest); }, [isLatest, setIsLatest]);

    const topPlayer = isFlipped ? whitePlayer : blackPlayer;
    const bottomPlayer = isFlipped ? blackPlayer : whitePlayer;
    const topDiff = isFlipped ? (ratingDiffs?.white_diff) : (ratingDiffs?.black_diff);
    const bottomDiff = isFlipped ? (ratingDiffs?.black_diff) : (ratingDiffs?.white_diff);

    return (
        <>
            <PlayerNameDisplay isOpponent={true} isFlipped={isFlipped} player={topPlayer} ratingDiff={topDiff} takebackOffer={takebackOffer} user={user} timers={timers} turn={turn} formatTime={formatTime} matchmaking={matchmaking} />

            <div className="pieces" ref={ref} onClick={(e) => { handleSquareClick(e); if (isMenuOpen) setIsMenuOpen(false); }}>
                <PromotionManager isPromotionDialogOpen={isPromotionDialogOpen} promotionColor={fen?.split(' ')[1] === 'w' ? 'w' : 'b'} handlePromotion={handlePromotion} handleCancelPromotion={() => setPromotionDialogOpen(false)} />
                {isImportDialogOpen && <ImportDialog onImport={(f, v) => { setImportDialogOpen(false); initializeGame(f, v); }} onCancel={() => setImportDialogOpen(false)} />}

                {selectedSquare && renderHighlight(selectedSquare, 'var(--selection-highlight)', 'selected')}
                {lastMove && renderHighlight(lastMove.from, 'var(--last-move-highlight)', 'last-from')}
                {lastMove && renderHighlight(lastMove.to, 'var(--last-move-highlight)', 'last-to')}

                <BoardEffects currentVariant={currentVariant} isFlipped={isFlipped} {...effects} />

                <div ref={highlightRef} className="drag-hover-highlight" style={{ display: 'none', position: 'absolute', width: 'var(--square-size)', height: 'var(--square-size)', pointerEvents: 'none', zIndex: 5 }} />

                {position.map((rankArray, rankIndex) => rankArray.map((pieceType, fileIndex) => pieceType ? (
                    <Piece key={`p-${rankIndex}-${fileIndex}`} rank={isFlipped ? 7 - rankIndex : rankIndex} file={isFlipped ? 7 - fileIndex : fileIndex} actualRank={rankIndex} actualFile={fileIndex} piece={pieceType} onDragStartCallback={handlePieceDragStart} onDropCallback={handleManualDrop} onDragHoverCallback={handlePieceDragHover} />
                ) : null))}

                {!isGameOver && legalMoves.map((moveUci, index) => {
                    const { file, rank } = algebraicToCoords(moveUci.slice(2, 4));
                    return <LegalMoveDot key={index} file={isFlipped ? 7 - file : file} rank={isFlipped ? 7 - rank : rank} />;
                })}

                <GameOverIndicator isGameOver={isGameOver} position={position} winner={winner} isFlipped={isFlipped} />
                <Confetti trigger={isGameOver && !!winner} />
            </div>

            <PlayerNameDisplay isOpponent={false} isFlipped={isFlipped} player={bottomPlayer} ratingDiff={bottomDiff} takebackOffer={takebackOffer} user={user} timers={timers} turn={turn} formatTime={formatTime} matchmaking={matchmaking} />
            
            <GameSidebar
                gameId={gameId}
                fenHistory={fenHistory}
                viewedIndex={viewedIndex}
                onJumpToMove={setViewedIndex}
                onStepBackward={() => setViewedIndex(prev => Math.max(0, prev === -1 ? fenHistory.length - 2 : prev - 1))}
                onStepForward={() => setViewedIndex(prev => prev === -1 ? -1 : Math.min(fenHistory.length - 1, prev + 1))}
                moveHistory={moveHistory}
                isGameOver={isGameOver}
                winner={winner}
                onNewGame={() => navigate('/create-game')}
                onReset={initializeGame}
                onUndo={() => ws.current?.send(JSON.stringify({ type: "undo" }))}
                onTakeback={() => ws.current?.send(JSON.stringify({ type: "takeback_offer" }))}
                onResign={() => ws.current?.send(JSON.stringify({ type: "resign" }))}
                onDraw={() => ws.current?.send(JSON.stringify({ type: "draw_offer" }))}
                onImport={() => setImportDialogOpen(true)}
                onCopyFen={() => navigator.clipboard.writeText(fen)}
                drawOffer={drawOffer}
                takebackOffer={takebackOffer}
                user={user}
                whitePlayerId={whitePlayerId}
                blackPlayerId={blackPlayerId}
            />
        </>
    );
}
