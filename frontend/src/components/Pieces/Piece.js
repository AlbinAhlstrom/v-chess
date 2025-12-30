import React, { useRef } from 'react';
import './Pieces.css';

function Piece({ piece, file, rank, actualFile, actualRank, onDragStartCallback, onDragEndCallback, onDropCallback, onDragHoverCallback, className = '' }) {
    const ghostRef = useRef(null);
    
    // Fallback to display coords if actual coords not provided
    const realFile = actualFile !== undefined ? actualFile : file;
    const realRank = actualRank !== undefined ? actualRank : rank;

    const fileChar = String.fromCharCode(97 + realFile);
    const rankChar = 8 - realRank;
    const squareStr = `${fileChar}${rankChar}`;

    const pieceStyle = {
        left: `calc(${file} * var(--square-size))`,
        top: `calc(${rank} * var(--square-size))`,
        '--piece-image': `url("/images/pieces/${piece}.png")`
    };

    const startDrag = (e) => {
        // Get initial coordinates (handle both mouse and touch)
        const clientX = e.type.startsWith('touch') ? e.touches[0].clientX : e.clientX;
        const clientY = e.type.startsWith('touch') ? e.touches[0].clientY : e.clientY;
        const startX = clientX;
        const startY = clientY;

        // 2. Capture layout data
        const rect = e.target.getBoundingClientRect();
        const offsetX = rect.width / 2;
        const offsetY = rect.height / 2;

        let dragStarted = false;

        // 5. Define handlers
        const handleMove = (moveEvent) => {
            const mClientX = moveEvent.type.startsWith('touch') ? moveEvent.touches[0].clientX : moveEvent.clientX;
            const mClientY = moveEvent.type.startsWith('touch') ? moveEvent.touches[0].clientY : moveEvent.clientY;

            if (!dragStarted) {
                const dist = Math.sqrt(Math.pow(mClientX - startX, 2) + Math.pow(mClientY - startY, 2));
                if (dist > 8) { // 8px threshold to distinguish tap from drag
                    dragStarted = true;
                    
                    // Prevent default to avoid native drag, text selection, or scrolling on touch
                    if (moveEvent.cancelable) moveEvent.preventDefault();

                    // 1. Notify start
                    if (onDragStartCallback) {
                        onDragStartCallback({ file: realFile, rank: realRank, piece });
                    }

                    const ghost = document.createElement("div");
                    ghost.classList.add("piece");
                    ghost.style.position = "fixed";
                    ghost.style.pointerEvents = "none";
                    ghost.style.zIndex = "9999";
                    ghost.style.width = `${rect.width}px`;
                    ghost.style.height = `${rect.height}px`;
                    ghost.style.backgroundImage = pieceStyle['--piece-image'];
                    ghost.style.backgroundSize = '100%';
                    ghost.style.left = `${mClientX - offsetX}px`;
                    ghost.style.top = `${mClientY - offsetY}px`;
                    
                    document.body.appendChild(ghost);
                    ghostRef.current = ghost;

                    // 3. Hide original
                    e.target.style.opacity = "0";

                    // 4. Set global cursor
                    document.body.style.cursor = "grabbing";
                } else {
                    return;
                }
            }

            if (moveEvent.cancelable) moveEvent.preventDefault();
            if (ghostRef.current) {
                ghostRef.current.style.left = `${mClientX - offsetX}px`;
                ghostRef.current.style.top = `${mClientY - offsetY}px`;
            }
            if (onDragHoverCallback) {
                onDragHoverCallback(mClientX, mClientY);
            }
        };

        const handleEnd = (endEvent) => {
            // Get last known coordinates from touch/mouse
            const endX = endEvent.type.startsWith('touch') ? (endEvent.changedTouches ? endEvent.changedTouches[0].clientX : clientX) : endEvent.clientX;
            const endY = endEvent.type.startsWith('touch') ? (endEvent.changedTouches ? endEvent.changedTouches[0].clientY : clientY) : endEvent.clientY;

            // Cleanup listeners
            document.removeEventListener('mousemove', handleMove);
            document.removeEventListener('mouseup', handleEnd);
            document.removeEventListener('touchmove', handleMove);
            document.removeEventListener('touchend', handleEnd);

            if (dragStarted) {
                // Prevent the following click event if we actually dragged
                if (endEvent.cancelable) endEvent.preventDefault();

                // Cleanup ghost
                if (ghostRef.current) {
                    ghostRef.current.remove();
                    ghostRef.current = null;
                }

                // Restore original visibility
                e.target.style.opacity = "1";

                // Restore cursor
                document.body.style.cursor = "default";

                // Notify drop
                if (onDropCallback) {
                    onDropCallback({
                        clientX: endX,
                        clientY: endY,
                        piece,
                        file: realFile,
                        rank: realRank
                    });
                }

                // Clear hover
                if (onDragHoverCallback) {
                    onDragHoverCallback(null);
                }

                // Notify end
                if (onDragEndCallback) {
                    onDragEndCallback();
                }
            }
        };

        // Attach global listeners
        document.addEventListener('mousemove', handleMove);
        document.addEventListener('mouseup', handleEnd);
        document.addEventListener('touchmove', handleMove, { passive: false });
        document.addEventListener('touchend', handleEnd);
    };

    return (
        <div
            className={`piece ${className}`}
            style={{...pieceStyle, touchAction: 'none'}}
            onMouseDown={startDrag}
            onTouchStart={startDrag}
            data-piece={piece}
            data-square={squareStr}
        />
    );
}

export default React.memo(Piece);
