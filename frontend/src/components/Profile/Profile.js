import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getMe, getUserRatings, getUserProfile, getUserGames } from '../../api';
import SupporterBadge from '../SupporterBadge/SupporterBadge';
import './Profile.css';

function Profile() {
    const { userId: urlUserId } = useParams();
    const [user, setUser] = useState(null);
    const [ratings, setRatings] = useState([]);
    const [overall, setOverall] = useState(1500);
    const [isOwnProfile, setIsOwnProfile] = useState(false);
    
    // History state
    const [games, setGames] = useState([]);
    const [filterVariant, setFilterVariant] = useState('all');
    const [filterResult, setFilterResult] = useState('all');
    
    useEffect(() => {
        if (urlUserId) {
            // Viewing a public profile
            getUserProfile(urlUserId).then(data => {
                console.log("Profile data received:", data);
                setUser(data.user);
                setRatings(data.ratings);
                setOverall(data.overall);
                
                // Check if this is the logged-in user's profile
                getMe().then(meData => {
                    if (meData.user && String(meData.user.id) === String(urlUserId)) {
                        setIsOwnProfile(true);
                    } else {
                        setIsOwnProfile(false);
                    }
                }).catch(() => setIsOwnProfile(false));
            }).catch(console.error);
        } else {
            // Viewing own profile
            getMe().then(data => {
                if (data.user) {
                    setUser(data.user);
                    setIsOwnProfile(true);
                    getUserRatings(data.user.id).then(rData => {
                        setRatings(rData.ratings || []);
                        setOverall(rData.overall || 1500);
                    });
                }
            }).catch(console.error);
        }
    }, [urlUserId]);

    // Fetch games when user or filters change
    useEffect(() => {
        if (user && user.id) {
            const filters = {};
            if (filterVariant !== 'all') filters.variant = filterVariant;
            if (filterResult !== 'all') filters.result = filterResult;
            
            getUserGames(user.id, filters).then(data => {
                if (data && data.games) {
                    setGames(data.games);
                }
            }).catch(console.error);
        }
    }, [user, filterVariant, filterResult]);

    if (!user) {
        return <div className='profile-container'>Loading profile...</div>;
    }

    const VARIANTS = [
        "standard", "antichess", "atomic", "chess960", "crazyhouse", 
        "horde", "kingofthehill", "racingkings", "threecheck"
    ];

    return (
        <div className='profile-container'>
            <div className='profile-card'>
                <div className="profile-card-header">
                    <h1>{isOwnProfile ? "Your Profile" : `${user.username || user.name}'s Profile`}</h1>
                </div>
                
                <section className='profile-section'>
                    <div className="profile-header">
                        {user.picture && <img src={user.picture} alt={user.name} className="profile-picture" />}
                        <div className="profile-identity">
                            {user.username && (
                                <div className='info-row'>
                                    <span className='label'>Username:</span>
                                    <span className='value' style={{ fontWeight: 'bold', color: '#95bb4a' }}>
                                        @{user.username}
                                    </span>
                                </div>
                            )}
                            <div className='info-row'>
                                <span className='label'>Display Name:</span>
                                <span className='value' style={{ display: 'flex', alignItems: 'center' }}>
                                    {user.name}
                                    <SupporterBadge badgeType={user.supporter_badge} />
                                </span>
                            </div>
                            {isOwnProfile && (
                                <div className='info-row'>
                                    <span className='label'>Email:</span>
                                    <span className='value'>{user.email}</span>
                                </div>
                            )}
                        </div>
                    </div>
                </section>

                <section className='profile-section'>
                    <h2>Elo Ratings</h2>
                    <div className='overall-rating'>
                        <span className='label'>Overall Ranking:</span>
                        <span className='value'>{Math.round(overall)}</span>
                    </div>
                    <div className='ratings-grid'>
                        {ratings.length > 0 ? ratings.map(r => (
                            <div key={r.variant} className='rating-item'>
                                <span className='variant-name'>{r.variant.charAt(0).toUpperCase() + r.variant.slice(1)}</span>
                                <span className='variant-rating'>{Math.round(r.rating)}</span>
                                <span className='variant-rd'>±{Math.round(r.rd)}</span>
                            </div>
                        )) : <p>No games played yet.</p>}
                    </div>
                </section>

                <section className='profile-section'>
                    <h2>Game History</h2>
                    <div className='history-filters'>
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
                        <select 
                            value={filterResult} 
                            onChange={e => setFilterResult(e.target.value)}
                            className='filter-select'
                        >
                             <option value="all">All Results</option>
                             <option value="win">Win</option>
                             <option value="loss">Loss</option>
                             <option value="draw">Draw</option>
                        </select>
                    </div>
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
                </section>
            </div>
        </div>
    );
}

export default Profile;
