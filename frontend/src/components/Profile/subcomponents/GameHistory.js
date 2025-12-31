import React from 'react';
import { Link } from 'react-router-dom';

const VARIANTS = [
    "standard", "antichess", "atomic", "chess960", "crazyhouse", 
    "horde", "kingofthehill", "racingkings", "threecheck"
];

export function GameHistory({ 
    games, 
    filterResult, 
    setFilterResult, 
    filterVariant, 
    setFilterVariant 
}) {
    return (
        <section className='profile-section'>
            <h2>Game History</h2>
            <div className='history-controls'>
                <div className='result-tabs'>
                    {['all', 'win', 'draw', 'loss'].map(type => (
                        <button 
                            key={type}
                            className={`tab-btn ${type !== 'all' ? type : ''} ${filterResult === type ? 'active' : ''}`}
                            onClick={() => setFilterResult(type)}
                        >
                            {type === 'all' ? 'Games' : type.charAt(0).toUpperCase() + type.slice(1) + 's'}
                        </button>
                    ))}
                </div>
                <select 
                    value={filterVariant} 
                    onChange={e => setFilterVariant(e.target.value)}
                    className='filter-select'
                >
                     <option value="all">All Variants</option>
                     {VARIANTS.map(v => (
                         <option key={v} value={v}>{v.charAt(0).toUpperCase() + v.slice(1)}</option>
                     ))}
                </select>
            </div>
            <div className='games-list-container'>
                <div className='games-list'>
                    {games.length > 0 ? games.map(game => (
                        <Link to={`/game/${game.id}`} key={game.id} className={`game-item ${game.result}`}>
                            <div className='game-item-left'>
                                <div className='game-variant'>{game.variant}</div>
                                <div className='game-date'>{new Date(game.created_at).toLocaleDateString()}</div>
                            </div>
                            <div className='game-item-center'>
                                <div className='game-vs'>
                                    <span className={`result-indicator ${game.result}`}>{game.result.toUpperCase()}</span>
                                    <span className='vs-text'>vs</span>
                                    <span className='opponent-name'>{game.opponent.name}</span>
                                </div>
                            </div>
                            <div className='game-item-right'>
                                {game.rating_diff !== null && (
                                    <span className={`rating-diff ${game.rating_diff >= 0 ? 'positive' : 'negative'}`}>
                                        {game.rating_diff > 0 ? '+' : ''}{Math.round(game.rating_diff)}
                                    </span>
                                )}
                            </div>
                        </Link>
                    )) : <div className='no-games'>No games found matching criteria.</div>}
                </div>
            </div>
        </section>
    );
}
