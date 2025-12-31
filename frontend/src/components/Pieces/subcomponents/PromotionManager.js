import React from 'react';
import PromotionDialog from '../../PromotionDialog/PromotionDialog';

export function PromotionManager({ 
    isPromotionDialogOpen, 
    promotionColor, 
    handlePromotion, 
    handleCancelPromotion 
}) {
    if (!isPromotionDialogOpen) return null;

    return (
        <PromotionDialog 
            onPromote={handlePromotion} 
            onCancel={handleCancelPromotion} 
            color={promotionColor} 
        />
    );
}
