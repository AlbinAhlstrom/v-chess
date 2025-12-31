import { useRef } from 'react';

export function usePieceDrag({
    piece,
    realFile,
    realRank,
    pieceStyle,
    onDragStartCallback,
    onDragEndCallback,
    onDropCallback,
    onDragHoverCallback
}) {
    const ghostRef = useRef(null);

    const startDrag = (e) => {
        const clientX = e.type.startsWith('touch') ? e.touches[0].clientX : e.clientX;
        const clientY = e.type.startsWith('touch') ? e.touches[0].clientY : e.clientY;
        const startX = clientX;
        const startY = clientY;

        const rect = e.target.getBoundingClientRect();
        const offsetX = rect.width / 2;
        const offsetY = rect.height / 2;

        let dragStarted = false;

        const handleMove = (moveEvent) => {
            const mClientX = moveEvent.type.startsWith('touch') ? moveEvent.touches[0].clientX : moveEvent.clientX;
            const mClientY = moveEvent.type.startsWith('touch') ? moveEvent.touches[0].clientY : moveEvent.clientY;

            if (!dragStarted) {
                const dist = Math.sqrt(Math.pow(mClientX - startX, 2) + Math.pow(mClientY - startY, 2));
                if (dist > 8) {
                    dragStarted = true;
                    if (moveEvent.cancelable) moveEvent.preventDefault();

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
                    e.target.style.opacity = "0";
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
            if (onDragHoverCallback) onDragHoverCallback(mClientX, mClientY);
        };

        const handleEnd = (endEvent) => {
            const endX = endEvent.type.startsWith('touch') ? (endEvent.changedTouches ? endEvent.changedTouches[0].clientX : clientX) : endEvent.clientX;
            const endY = endEvent.type.startsWith('touch') ? (endEvent.changedTouches ? endEvent.changedTouches[0].clientY : clientY) : endEvent.clientY;

            document.removeEventListener('mousemove', handleMove);
            document.removeEventListener('mouseup', handleEnd);
            document.removeEventListener('touchmove', handleMove);
            document.removeEventListener('touchend', handleEnd);

            if (dragStarted) {
                if (endEvent.cancelable) endEvent.preventDefault();
                if (ghostRef.current) {
                    ghostRef.current.remove();
                    ghostRef.current = null;
                }
                e.target.style.opacity = "1";
                document.body.style.cursor = "default";

                if (onDropCallback) {
                    onDropCallback({ clientX: endX, clientY: endY, piece, file: realFile, rank: realRank });
                }
                if (onDragHoverCallback) onDragHoverCallback(null);
                if (onDragEndCallback) onDragEndCallback();
            }
        };

        document.addEventListener('mousemove', handleMove);
        document.addEventListener('mouseup', handleEnd);
        document.addEventListener('touchmove', handleMove, { passive: false });
        document.addEventListener('touchend', handleEnd);
    };

    return { startDrag };
}
