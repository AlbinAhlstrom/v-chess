import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import './Rules.css';

import StandardTutorialBoard from './Tutorials/StandardTutorial';
import AtomicTutorialBoard from './Tutorials/AtomicTutorial';
import AntichessTutorialBoard from './Tutorials/AntichessTutorial';
import CrazyhouseTutorialBoard from './Tutorials/CrazyhouseTutorial';
import KOTHTutorialBoard from './Tutorials/KOTHTutorial';
import RacingKingsTutorialBoard from './Tutorials/RacingKingsTutorial';
import HordeTutorialBoard from './Tutorials/HordeTutorial';
import ThreeCheckTutorialBoard from './Tutorials/ThreeCheckTutorial';
import Chess960TutorialBoard from './Tutorials/Chess960Tutorial';

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
                
                {currentVariant === 'standard' && <StandardTutorialBoard />}
                {currentVariant === 'atomic' && <AtomicTutorialBoard />}
                {currentVariant === 'antichess' && <AntichessTutorialBoard />}
                {currentVariant === 'crazyhouse' && <CrazyhouseTutorialBoard />}
                {currentVariant === 'king_of_the_hill' && <KOTHTutorialBoard />}
                {currentVariant === 'racing_kings' && <RacingKingsTutorialBoard />}
                {currentVariant === 'horde' && <HordeTutorialBoard />}
                {currentVariant === 'three_check' && <ThreeCheckTutorialBoard />}
                {currentVariant === 'chess960' && <Chess960TutorialBoard />}

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