import { useRef } from 'react';

export function usePieceDrag({
    piece,
    realFile,
    realRank,
    pieceStyle,
    onDragStartCallback,
    onDragEndCallback,
    onDropCallback,
    onDragHoverCallback,
    onPieceClick
}) {
    const ghostRef = useRef(null);
    const startData = useRef(null);
    const isDragging = useRef(false);

    const handlePointerDown = (e) => {
        // Prevent default to ensure pointer capture works reliably and scrolling is prevented
        e.preventDefault();
        e.stopPropagation();

        const node = e.target;
        node.setPointerCapture(e.pointerId);

        const rect = node.getBoundingClientRect();
        
        startData.current = {
            x: e.clientX,
            y: e.clientY,
            pointerId: e.pointerId,
            rect,
            offsetX: rect.width / 2,
            offsetY: rect.height / 2
        };
        isDragging.current = false;
    };

    const handlePointerMove = (e) => {
        if (!startData.current || e.pointerId !== startData.current.pointerId) return;

        const { x: startX, y: startY, offsetX, offsetY } = startData.current;
        const dist = Math.hypot(e.clientX - startX, e.clientY - startY);

        if (!isDragging.current) {
            // Threshold for Drag vs Tap
            if (dist > 8) {
                isDragging.current = true;
                
                if (onDragStartCallback) {
                    onDragStartCallback({ file: realFile, rank: realRank, piece });
                }

                // Create Ghost
                const ghost = document.createElement("div");
                ghost.classList.add("piece");
                ghost.style.position = "fixed";
                ghost.style.pointerEvents = "none";
                ghost.style.zIndex = "9999";
                ghost.style.width = `${startData.current.rect.width}px`;
                ghost.style.height = `${startData.current.rect.height}px`;
                ghost.style.backgroundImage = pieceStyle['--piece-image'];
                ghost.style.backgroundSize = '100%';
                ghost.style.left = `${e.clientX - offsetX}px`;
                ghost.style.top = `${e.clientY - offsetY}px`;
                
                document.body.appendChild(ghost);
                ghostRef.current = ghost;
                
                // Hide original
                e.target.style.opacity = "0";
                document.body.style.cursor = "grabbing";
            }
        }

        if (isDragging.current && ghostRef.current) {
            ghostRef.current.style.left = `${e.clientX - offsetX}px`;
            ghostRef.current.style.top = `${e.clientY - offsetY}px`;
            
            if (onDragHoverCallback) onDragHoverCallback(e.clientX, e.clientY);
        }
    };

    const handlePointerUp = (e) => {
        if (!startData.current || e.pointerId !== startData.current.pointerId) return;

        const node = e.target;
        node.releasePointerCapture(e.pointerId);

        if (isDragging.current) {
            // Drop Logic
            node.style.opacity = "1";
            document.body.style.cursor = "default";
            
            if (ghostRef.current) {
                ghostRef.current.remove();
                ghostRef.current = null;
            }

            if (onDropCallback) {
                onDropCallback({ clientX: e.clientX, clientY: e.clientY, piece, file: realFile, rank: realRank });
            }
            if (onDragHoverCallback) onDragHoverCallback(null);
            if (onDragEndCallback) onDragEndCallback();
        } else {
            // Tap Logic
            if (onPieceClick) {
                onPieceClick({ clientX: e.clientX, clientY: e.clientY });
            }
        }

        startData.current = null;
        isDragging.current = false;
    };

    return {
        handlePointerDown,
        handlePointerMove,
        handlePointerUp
    };
}