import React from 'react';
import { useParams } from 'react-router-dom';
import './Profile.css';

// Subcomponents
import { ProfileInfo } from './subcomponents/ProfileInfo';
import { RatingsGrid } from './subcomponents/RatingsGrid';
import { GameHistory } from './subcomponents/GameHistory';

// Hooks
import { useUserProfile } from './hooks/useUserProfile';

function Profile() {
    const { userId: urlUserId } = useParams();
    const {
        user, ratings, overall, isOwnProfile, games,
        filterVariant, setFilterVariant,
        filterResult, setFilterResult
    } = useUserProfile(urlUserId);

    if (!user) {
        return <div className='profile-container'>Loading profile...</div>;
    }

    return (
        <div className='profile-container'>
            <div className='profile-card'>
                <div className="profile-card-header">
                    <h1>{isOwnProfile ? "Your Profile" : `${user.username || user.name}'s Profile`}</h1>
                </div>
                
                <ProfileInfo user={user} isOwnProfile={isOwnProfile} />
                <RatingsGrid ratings={ratings} overall={overall} />
                <GameHistory 
                    games={games}
                    filterResult={filterResult}
                    setFilterResult={setFilterResult}
                    filterVariant={filterVariant}
                    setFilterVariant={setFilterVariant}
                />
            </div>
        </div>
    );
}

export default Profile;