import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { getLeaderboard } from '../../api';
import SupporterBadge from '../SupporterBadge/SupporterBadge';
import './Leaderboard.css';

const VARIANTS = [
    { id: 'standard', title: 'Standard' },
    { id: 'antichess', title: 'Antichess' },
    { id: 'atomic', title: 'Atomic' },
    { id: 'chess960', title: 'Chess960' },
    { id: 'crazyhouse', title: 'Crazyhouse' },
    { id: 'horde', title: 'Horde' },
    { id: 'kingofthehill', title: 'King of the Hill' },
    { id: 'racingkings', title: 'Racing Kings' },
    { id: 'threecheck', title: 'Three Check' },
];

function Leaderboard() {
    const { variant: urlVariant } = useParams();
    const navigate = useNavigate();
    const [variant, setVariant] = useState(urlVariant || 'standard');
    const [leaders, setLeaders] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const v = urlVariant || 'standard';
        setVariant(v);
        setLoading(true);
        getLeaderboard(v).then(data => {
            setLeaders(data.leaderboard || []);
            setLoading(false);
        }).catch(err => {
            console.error("Failed to fetch leaderboard:", err);
            setLoading(false);
        });
    }, [urlVariant]);

    const handleVariantChange = (vId) => {
        navigate(`/leaderboards/${vId}`);
    };

    return (
        <div className="leaderboard-container">
            <div className="leaderboard-card">
                <h1>Global Leaderboards</h1>
                
                <div className="variant-tabs">
                    {VARIANTS.map(v => (
                        <button 
                            key={v.id} 
                            className={`variant-tab ${variant === v.id ? 'active' : ''}`}
                            onClick={() => handleVariantChange(v.id)}
                        >
                            {v.title}
                        </button>
                    ))}
                </div>

                {loading ? (
                    <div className="loading-state">Loading rankings...</div>
                ) : (
                    <div className="leaderboard-table-container">
                        <table className="leaderboard-table">
                            <thead>
                                <tr>
                                    <th className="rank-col">#</th>
                                    <th className="player-col">Player</th>
                                    <th className="rating-col">Elo</th>
                                </tr>
                            </thead>
                            <tbody>
                                {leaders.length === 0 ? (
                                    <tr>
                                        <td colSpan="3" className="no-data">No ranked players yet for this variant.</td>
                                    </tr>
                                ) : (
                                    leaders.map((player, index) => (
                                        <tr key={player.user_id} className="leader-row">
                                            <td className="rank-col">{index + 1}</td>
                                            <td className="player-col">
                                                <Link to={`/profile/${player.user_id}`} className="player-link">
                                                    {player.picture && <img src={player.picture} alt="" className="mini-avatar" />}
                                                    <span className="player-name">{player.name}</span>
                                                </Link>
                                                <SupporterBadge badgeType={player.supporter_badge} />
                                            </td>
                                            <td className="rating-col">
                                                <span className="rating-value">{player.rating}</span>
                                                <span className="rd-value">±{player.rd}</span>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Leaderboard;
