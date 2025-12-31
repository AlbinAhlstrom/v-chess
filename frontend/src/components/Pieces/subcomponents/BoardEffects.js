import React from 'react';
import { algebraicToCoords } from '../../../helpers';

export function BoardEffects({ 
    currentVariant, 
    isFlipped, 
    showExplosion, 
    explosionSquare,
    showDropWarp,
    dropSquare,
    showStrike,
    strikeSquare,
    showTurbo,
    turboSquare,
    showShatter,
    shatterSquare
}) {
    const getDisplayCoords = (square) => {
        const { file, rank } = algebraicToCoords(square);
        return {
            displayFile: isFlipped ? 7 - file : file,
            displayRank: isFlipped ? 7 - rank : rank
        };
    };

    const renderExplosion = () => {
        if (!showExplosion || !explosionSquare) return null;
        
        const { displayFile, displayRank } = getDisplayCoords(explosionSquare);
        const style = {
            left: `calc(${displayFile} * var(--square-size))`,
            top: `calc(${displayRank} * var(--square-size))`,
        };

        return (
            <div className="explosion-container" style={style}>
                <div className="explosion-ring"></div>
                <div className="explosion-ring"></div>
                <div className="explosion-ring"></div>
                {[...Array(12)].map((_, i) => {
                    const angle = (i / 12) * 2 * Math.PI;
                    const dist = 100 + Math.random() * 100;
                    const dx = Math.cos(angle) * dist;
                    const dy = Math.sin(angle) * dist;
                    return (
                        <div 
                            key={i} 
                            className="explosion-particle" 
                            style={{ 
                                '--dx': `${dx}px`, 
                                '--dy': `${dy}px`,
                                animationDelay: `${Math.random() * 0.2}s`
                            }}
                        ></div>
                    );
                })}
            </div>
        );
    };

    const renderKothAura = () => {
        if (currentVariant !== 'kingofthehill') return null;

        const centerSquares = ['d4', 'd5', 'e4', 'e5'];
        return centerSquares.map(sq => {
            const { displayFile, displayRank } = getDisplayCoords(sq);

            return (
                <div 
                    key={`koth-${sq}`}
                    className="koth-aura"
                    style={{
                        left: `calc(${displayFile} * var(--square-size))`,
                        top: `calc(${displayRank} * var(--square-size))`,
                    }}
                />
            );
        });
    };

    const renderDropWarp = () => {
        if (!showDropWarp || !dropSquare) return null;
        const { displayFile, displayRank } = getDisplayCoords(dropSquare);

        return (
            <div 
                className="drop-warp"
                style={{
                    left: `calc(${displayFile} * var(--square-size))`,
                    top: `calc(${displayRank} * var(--square-size))`,
                }}
            />
        );
    };

    const renderCheckStrike = () => {
        if (!showStrike || !strikeSquare) return null;
        const { displayFile, displayRank } = getDisplayCoords(strikeSquare);

        return (
            <div 
                className="check-strike"
                style={{
                    left: `calc(${displayFile} * var(--square-size))`,
                    top: `calc(${displayRank} * var(--square-size))`,
                }}
            >
                <div className="strike-slash"></div>
            </div>
        );
    };

    const renderTurboEffect = () => {
        if (!showTurbo || !turboSquare) return null;
        const { displayFile, displayRank } = getDisplayCoords(turboSquare);

        return (
            <div 
                className="turbo-trail"
                style={{
                    left: `calc(${displayFile} * var(--square-size))`,
                    top: `calc(${displayRank} * var(--square-size))`,
                }}
            >
                <div className="turbo-line"></div>
                <div className="turbo-line"></div>
                <div className="turbo-line"></div>
            </div>
        );
    };

    const renderShatterEffect = () => {
        if (!showShatter || !shatterSquare) return null;
        const { displayFile, displayRank } = getDisplayCoords(shatterSquare);

        return (
            <div 
                className="shatter-container"
                style={{
                    left: `calc(${displayFile} * var(--square-size))`,
                    top: `calc(${displayRank} * var(--square-size))`,
                }}
            >
                {[...Array(8)].map((_, i) => (
                    <div key={i} className="shard" style={{ '--i': i }}></div>
                ))}
            </div>
        );
    };

    return (
        <>
            {renderExplosion()}
            {renderKothAura()}
            {renderDropWarp()}
            {renderCheckStrike()}
            {renderTurboEffect()}
            {renderShatterEffect()}
        </>
    );
}
