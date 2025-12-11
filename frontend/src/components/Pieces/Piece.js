import React, { useRef } from 'react';
import './Pieces.css';

function Piece({ piece, file, rank, onDragStartCallback, onDragEndCallback, onDropCallback, onDragHoverCallback }) {
    const ghostRef = useRef(null);

    const pieceStyle = {
        left: `calc(${file} * var(--square-size))`,
        top: `calc(${rank} * var(--square-size))`,
        '--piece-image': `url("/images/pieces/${piece}.png")`
    };

    const handleMouseDown = (e) => {
        // Prevent default to avoid native drag or text selection
        e.preventDefault();

        // 1. Notify start
        if (onDragStartCallback) {
            onDragStartCallback({ file, rank, piece });
        }

        // 2. Create custom ghost (fully opaque)
        const rect = e.target.getBoundingClientRect();
        const offsetX = e.clientX - rect.left;
        const offsetY = e.clientY - rect.top;

        const ghost = document.createElement("div");
        ghost.classList.add("piece");
        ghost.style.position = "fixed";
        ghost.style.pointerEvents = "none";
        ghost.style.zIndex = "9999";
        ghost.style.width = `${rect.width}px`;
        ghost.style.height = `${rect.height}px`;
        ghost.style.backgroundImage = pieceStyle['--piece-image'];
        ghost.style.left = `${e.clientX - offsetX}px`;
        ghost.style.top = `${e.clientY - offsetY}px`;
        
        document.body.appendChild(ghost);
        ghostRef.current = ghost;

        // 3. Hide original
        e.target.style.display = "none";

        // 4. Set global cursor
        document.body.style.cursor = "grabbing";

        // 5. Define handlers
        const handleMouseMove = (moveEvent) => {
            if (ghostRef.current) {
                ghostRef.current.style.left = `${moveEvent.clientX - offsetX}px`;
                ghostRef.current.style.top = `${moveEvent.clientY - offsetY}px`;
            }
            if (onDragHoverCallback) {
                onDragHoverCallback(moveEvent.clientX, moveEvent.clientY);
            }
        };

        const handleMouseUp = (upEvent) => {
            // Cleanup listeners
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);

            // Cleanup ghost
            if (ghostRef.current) {
                ghostRef.current.remove();
                ghostRef.current = null;
            }

            // Restore original visibility
            e.target.style.display = "block";

            // Restore cursor
            document.body.style.cursor = "default";

            // Notify drop
            if (onDropCallback) {
                onDropCallback({
                    clientX: upEvent.clientX,
                    clientY: upEvent.clientY,
                    piece,
                    file,
                    rank
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
        };

        // Attach global listeners
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
    };

    return (
        <div
            className="piece"
            style={pieceStyle}
            onMouseDown={handleMouseDown}
        />
    );
}

export default Piece;