import React from 'react';

function FlyingKnight({ file, rank, isPreparing, isFlying }) {
    const style = {
        left: `calc(${file} * 25%)`,
        top: `calc(${rank} * 25%)`,
        width: '25%',
        height: '25%',
        position: 'absolute',
        pointerEvents: 'none',
        zIndex: 1000,
        backgroundImage: 'url("/images/pieces/N.png")',
        backgroundSize: '100%'
    };

    let className = 'visceral-knight';
    if (isPreparing) className += ' preparing';
    if (isFlying) className += ' flying';

    return (
        <div className={className} style={style}>
            <div className="vk-inner">
                <div className="vk-front" style={{ backgroundImage: 'var(--piece-image)' }}></div>
                <div className="vk-back" style={{ backgroundImage: 'var(--piece-image)' }}></div>
            </div>
        </div>
    );
}

export default FlyingKnight;
