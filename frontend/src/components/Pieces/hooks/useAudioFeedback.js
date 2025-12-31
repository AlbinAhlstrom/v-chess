import { useRef, useEffect } from 'react';
import SoundManager from '../../../helpers/soundManager';
import { fenToPosition } from '../../../helpers';

export function useAudioFeedback(viewedFen, inCheck, isGameOver, gameId, onFenChange) {
    const lastNotifiedFen = useRef(null);
    const isPromoting = useRef(false);

    useEffect(() => {
        if (viewedFen && viewedFen !== lastNotifiedFen.current) {
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
                const currKingCol = findKingCol(viewedFen, isWhiteTurn);
                const isCastling = prevKingCol !== -1 && currKingCol !== -1 && Math.abs(prevKingCol - currKingCol) > 1;

                const prevCount = countPieces(lastNotifiedFen.current);
                const currentCount = countPieces(viewedFen);

                if (inCheck) {
                    SoundManager.play('check');
                } else if (isPromoting.current) {
                    SoundManager.play('promote');
                    isPromoting.current = false;
                } else if (isCastling) {
                    SoundManager.play('castle');
                } else if (currentCount < prevCount) {
                     SoundManager.play('capture');
                } else {
                     SoundManager.play('move');
                }
            }
            onFenChange(viewedFen);
            lastNotifiedFen.current = viewedFen;
        }
    }, [viewedFen, onFenChange, inCheck]);

    return { isPromoting, lastNotifiedFen };
}
