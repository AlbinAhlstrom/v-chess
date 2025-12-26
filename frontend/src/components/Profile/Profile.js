import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getMe, getUserRatings, getUserProfile } from '../../api';
import SupporterBadge from '../SupporterBadge/SupporterBadge';
import './Profile.css';

function Profile() {
    const { userId: urlUserId } = useParams();
    const [user, setUser] = useState(null);
    const [ratings, setRatings] = useState([]);
    const [overall, setOverall] = useState(1500);
    const [isOwnProfile, setIsOwnProfile] = useState(false);
    
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

    if (!user) {
        return <div className='profile-container'>Loading profile...</div>;
    }

    return (
        <div className='profile-container'>
            <div className='profile-card'>
                <div className="profile-card-header">
                    <h1>{isOwnProfile ? "Your Profile" : `${user.name}'s Profile`}</h1>
                </div>
                
                <section className='profile-section'>
                    <div className="profile-header">
                        {user.picture && <img src={user.picture} alt={user.name} className="profile-picture" />}
                        <div className="profile-identity">
                            <div className='info-row'>
                                <span className='label'>Name:</span>
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
            </div>
        </div>
    );
}

export default Profile;
