import React from 'react';
import SupporterBadge from '../../SupporterBadge/SupporterBadge';

export function ProfileInfo({ user, isOwnProfile }) {
    return (
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
    );
}
