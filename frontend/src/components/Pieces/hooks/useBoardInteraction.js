import { useState, useCallback, useRef, useEffect } from 'react';
import { coordsToAlgebraic, algebraicToCoords } from '../../../helpers';

export function useBoardInteraction(isFlipped, position, allPossibleMoves, canMovePiece, onMoveAttempt) {
    const [selectedSquare, setSelectedSquare] = useState(null);
    const [legalMoves, setLegalMoves] = useState([]);
    const [flashKingSquare, setFlashKingSquare] = useState(null);
    const dragStartSelectionState = useRef(false);
    const ref = useRef(null);
    const highlightRef = useRef(null);

    // Clear selection when position changes (move made)
    useEffect(() => {
        setSelectedSquare(null);
        setLegalMoves([]);
    }, [position]);

    const calculateSquare = useCallback(e => {
        if (!ref.current) return null;
        const { width, left, top } = ref.current.getBoundingClientRect();
        
        const clientX = e.clientX ?? (e.touches?.[0]?.clientX) ?? (e.changedTouches?.[0]?.clientX);
        const clientY = e.clientY ?? (e.touches?.[0]?.clientY) ?? (e.changedTouches?.[0]?.clientY);

        if (clientX === undefined || clientY === undefined) return null;

        const size = width / 8;
        let file = Math.floor((clientX - left) / size);
        let rank = Math.floor((clientY - top) / size);
        
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
        const squareData = calculateSquare({ clientX, clientY });
        if (!squareData) return;
        const { file, rank } = squareData;
        
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

    const handlePieceDragStart = useCallback(async ({ file, rank, piece }) => {
        const pieceColor = piece === piece.toUpperCase() ? 'w' : 'b';
        if (!canMovePiece(pieceColor)) return;

        const square = coordsToAlgebraic(file, rank);
        dragStartSelectionState.current = (selectedSquare === square);
        setSelectedSquare(square);
        
        const moves = allPossibleMoves.filter(m => m.startsWith(square));
        setLegalMoves(moves);
    }, [canMovePiece, selectedSquare, allPossibleMoves]);

    const handleSquareClick = useCallback(async (e) => {
        const squareData = calculateSquare(e);
        if (!squareData) return;
        const { file, rank, algebraic: clickedSquare } = squareData;

        const isPiece = (f, r) => {
            if (r < 0 || r > 7 || f < 0 || f > 7) return false;
            return !!position[r][f];
        };

        if (selectedSquare) {
            const movesToTarget = legalMoves.filter(m => m.slice(2, 4) === clickedSquare);

            if (movesToTarget.length > 0) {
                onMoveAttempt(selectedSquare, clickedSquare, movesToTarget);
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
    }, [calculateSquare, position, selectedSquare, legalMoves, canMovePiece, allPossibleMoves, onMoveAttempt]);

    const handleManualDrop = useCallback(({ clientX, clientY, file, rank }) => {
        if (highlightRef.current) highlightRef.current.style.display = 'none';
        
        const squareData = calculateSquare({ clientX, clientY });
        if (!squareData) return;
        const { algebraic: toSquare } = squareData;
        const fromSquare = coordsToAlgebraic(file, rank);

        if (fromSquare === toSquare) {
            if (dragStartSelectionState.current) {
                setSelectedSquare(null);
                setLegalMoves([]);
            }
            return;
        }

        const movesToTarget = allPossibleMoves.filter(m => m.startsWith(fromSquare) && m.slice(2, 4) === toSquare);
        if (movesToTarget.length > 0) {
            onMoveAttempt(fromSquare, toSquare, movesToTarget);
        }
    }, [calculateSquare, allPossibleMoves, onMoveAttempt]);

    return {
        selectedSquare, setSelectedSquare,
        legalMoves, setLegalMoves,
        flashKingSquare, setFlashKingSquare,
        ref, highlightRef,
        handleSquareClick,
        handlePieceDragStart,
        handlePieceDragHover,
        handleManualDrop
    };
}
