import './PromotionDialog.css';

function PromotionDialog({ onPromote, onCancel, color }) {
    const promotionPieces = ['q', 'r', 'b', 'n'];

    const handleOverlayClick = (e) => {
        if (e.target === e.currentTarget) {
            onCancel();
        }
    };

    return (
        <div className="promotion-dialog-overlay" onClick={handleOverlayClick}>
            <div className="promotion-dialog">
                <div className="promotion-options">
                    {promotionPieces.map(piece => (
                        <div key={piece} className="promotion-option" onClick={() => onPromote(piece)}>
                            <img src={`/images/pieces/${color === 'w' ? piece.toUpperCase() : piece}.png`} alt={piece} />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default PromotionDialog;