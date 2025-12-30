import React, { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import './Rules.css';

const VARIANT_RULES = {
    standard: {
        title: "Standard Chess",
        description: "The classic game of strategy.",
        rules: [
            "Checkmate the opponent's king to win.",
            "Stalemate is a draw.",
            "Standard piece movements apply."
        ]
    },
    antichess: {
        title: "Antichess",
        description: "Lose all your pieces to win.",
        rules: [
            "Capturing is mandatory.",
            "If multiple captures are available, you may choose which to make.",
            "The king has no special status (it can be captured).",
            "You win by losing all your pieces or being stalemated."
        ]
    },
    atomic: {
        title: "Atomic Chess",
        description: "Every capture is an explosion.",
        rules: [
            "When a piece is captured, an explosion occurs on the captured square.",
            "The explosion removes the capturing piece, the captured piece, and all non-pawn pieces in the surrounding 3x3 area.",
            "Pawns are only removed if they are directly involved in the capture.",
            "A player wins by exploding the opponent's king or by traditional checkmate.",
            "Kings cannot capture pieces because they would explode."
        ]
    },
    crazyhouse: {
        title: "Crazyhouse",
        description: "Captured pieces join your side.",
        rules: [
            "When you capture an opponent's piece, it is added to your reserve (in your color).",
            "On any turn, instead of moving a piece, you may 'drop' a piece from your reserve onto any empty square.",
            "Pawns cannot be dropped on the 1st or 8th ranks.",
            "A pawn dropped on the 2nd rank retains its double-move ability."
        ]
    },
    horde: {
        title: "Horde Chess",
        description: "A pawn army vs. standard pieces.",
        rules: [
            "White has 36 pawns and no other pieces.",
            "Black has a standard set of pieces.",
            "White wins by checkmating the Black king.",
            "Black wins by capturing all of White's pawns (and any promoted pieces)."
        ]
    },
    king_of_the_hill: {
        title: "King of the Hill",
        description: "Race your king to the center.",
        rules: [
            "In addition to standard checkmate, a player can win by moving their king to one of the four center squares: e4, d4, e5, or d5.",
            "The first player to reach the center wins immediately."
        ]
    },
    racing_kings: {
        title: "Racing Kings",
        description: "A race to the finish line.",
        rules: [
            "The goal is to reach the 8th rank with your king.",
            "If White reaches the 8th rank first, Black has one last turn to also reach the 8th rank, resulting in a draw.",
            "Checks are illegal. You cannot move into check, and you cannot deliver a check."
        ]
    },
    three_check: {
        title: "Three-Check",
        description: "Check the king three times to win.",
        rules: [
            "A player wins by checking the opponent's king three times.",
            "Standard checkmate also ends the game.",
            "The game status shows how many checks each player has delivered."
        ]
    },
    chess960: {
        title: "Chess960 (Fischer Random)",
        description: "Randomized starting positions.",
        rules: [
            "The starting position of the pieces is randomized on the first rank.",
            "Bishops must be on opposite colors.",
            "The king must be between the two rooks.",
            "Castling rules are the same as standard chess, but the king and rook end up on the same squares as in standard castling (c1/g1 for White, c8/g8 for Black)."
        ]
    }
};

function AtomicTutorialBoard() {
    const [pieces, setPieces] = useState([
        { id: 'wk', type: 'N', color: 'w', file: 1, rank: 3 }, // Knight at b1 (relative to 4x4)
        { id: 'bp', type: 'p', color: 'b', file: 2, rank: 1 }, // Pawn at c3 (relative to 4x4)
        { id: 'br', type: 'r', color: 'b', file: 1, rank: 0 }, // Rook at b4 - will explode
        { id: 'bq', type: 'q', color: 'b', file: 3, rank: 0 }, // Queen at d4 - will explode
        { id: 'bk', type: 'k', color: 'b', file: 0, rank: 0 }, // King at a4 - safe
    ]);
    const [explosion, setExplosion] = useState(null);
    const [message, setMessage] = useState("Move the White Knight to capture the Black Pawn!");
    const [completed, setCompleted] = useState(false);

    const handleSquareClick = (file, rank) => {
        if (completed || explosion) return;

        const knight = pieces.find(p => p.id === 'wk');
        const target = pieces.find(p => p.file === file && p.rank === rank);

        // Check for valid knight move to target
        const dx = Math.abs(file - knight.file);
        const dy = Math.abs(rank - knight.rank);
        const isKnightMove = (dx === 1 && dy === 2) || (dx === 2 && dy === 1);

        if (isKnightMove && target && target.color === 'b') {
            // Valid capture
            setMessage("BOOM! The capture caused an explosion!");
            
            // 1. Move knight visually first
            setPieces(prev => prev.map(p => p.id === 'wk' ? { ...p, file, rank } : p));

            // 2. Trigger explosion animation
            setExplosion({ file, rank });

            // 3. Remove pieces after delay
            setTimeout(() => {
                setPieces(prev => prev.filter(p => {
                    const pdx = Math.abs(p.file - file);
                    const pdy = Math.abs(p.rank - rank);
                    // Remove if in 1 square radius (King is immune to explosion normally but in atomic only pawns survive surrounding explosions? 
                    // Rules: "The explosion removes the capturing piece, the captured piece, and all non-pawn pieces in the surrounding 3x3 area."
                    // Pawns only removed if directly involved.
                    
                    if (p.id === 'wk') return false; // Capturing piece dies
                    if (p.file === file && p.rank === rank) return false; // Captured piece dies
                    
                    if (pdx <= 1 && pdy <= 1) {
                        if (p.type === 'p') return true; // Pawns survive surrounding
                        return false; // Others die
                    }
                    return true;
                }));
                setExplosion(null);
                setCompleted(true);
                setMessage("Notice: The Knight, Pawn, and surrounding pieces exploded. The King survived!");
            }, 800);
        } else if (isKnightMove) {
            setMessage("Move to capture the Black Pawn to see the explosion!");
        }
    };

    const reset = () => {
        setPieces([
            { id: 'wk', type: 'N', color: 'w', file: 1, rank: 3 },
            { id: 'bp', type: 'p', color: 'b', file: 2, rank: 1 },
            { id: 'br', type: 'r', color: 'b', file: 1, rank: 0 },
            { id: 'bq', type: 'q', color: 'b', file: 3, rank: 0 },
            { id: 'bk', type: 'k', color: 'b', file: 0, rank: 0 },
        ]);
        setExplosion(null);
        setCompleted(false);
        setMessage("Move the White Knight to capture the Black Pawn!");
    };

    return (
        <div className="atomic-tutorial">
            <div className="tutorial-board">
                {[0, 1, 2, 3].map(rank => (
                    [0, 1, 2, 3].map(file => {
                        const isBlack = (rank + file) % 2 === 1;
                        return (
                            <div 
                                key={`${file}-${rank}`}
                                className={`tutorial-square ${isBlack ? 'black-square' : 'white-square'}`}
                                onClick={() => handleSquareClick(file, rank)}
                            />
                        );
                    })
                ))}
                
                {pieces.map(p => (
                    <div
                        key={p.id}
                        className="tutorial-piece"
                        style={{
                            left: `${p.file * 25}%`,
                            top: `${p.rank * 25}%`,
                            backgroundImage: `url("/images/pieces/${p.color}${p.type}.png")`
                        }}
                        onClick={(e) => {
                            e.stopPropagation();
                            handleSquareClick(p.file, p.rank);
                        }}
                    />
                ))}

                {explosion && (
                    <div 
                        className="explosion-container"
                        style={{
                            left: `${explosion.file * 25}%`,
                            top: `${explosion.rank * 25}%`,
                            width: '25%',
                            height: '25%'
                        }}
                    >
                        <div className="explosion-ring"></div>
                        <div className="explosion-ring"></div>
                        <div className="explosion-ring"></div>
                    </div>
                )}
            </div>
            <div className="tutorial-controls">
                <p>{message}</p>
                {completed && <button onClick={reset}>Reset Tutorial</button>}
            </div>
        </div>
    );
}

function Rules() {
    const { variant } = useParams();
    const currentVariant = variant || 'standard';
    const variantData = VARIANT_RULES[currentVariant];

    const navigate = useNavigate();

    if (!variantData) {
        return (
            <div className="rules-container">
                <h1>Variant not found</h1>
                <Link to="/rules/standard">Back to Standard Rules</Link>
            </div>
        );
    }

    const handleVariantChange = (vId) => {
        navigate(`/rules/${vId}`);
    };

    return (
        <div className="rules-container">
            <div className="variant-select-container">
                <select 
                    value={currentVariant} 
                    onChange={(e) => handleVariantChange(e.target.value)}
                    className="variant-select-dropdown"
                >
                    {Object.keys(VARIANT_RULES).map(v => (
                        <option key={v} value={v}>
                            {VARIANT_RULES[v].title}
                        </option>
                    ))}
                </select>
            </div>
            <div className="rules-content">
                <h1>{variantData.title}</h1>
                <p className="variant-description">{variantData.description}</p>
                
                {currentVariant === 'atomic' && <AtomicTutorialBoard />}

                <ul className="rules-list">
                    {variantData.rules.map((rule, index) => (
                        <li key={index}>{rule}</li>
                    ))}
                </ul>
                <div className="rules-actions">
                    <Link to={`/otb/${currentVariant}`} className="play-button">
                        Play {variantData.title}
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default Rules;
