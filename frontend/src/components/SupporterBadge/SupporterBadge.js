import React from 'react';
import './SupporterBadge.css';

const BADGES = {
    'kickstarter': {
        icon: '💎',
        label: 'Kickstarter Backer',
        className: 'badge-kickstarter'
    },
    'patreon': {
        icon: '🌟',
        label: 'Patreon Supporter',
        className: 'badge-patreon'
    }
};

function SupporterBadge({ badgeType }) {
    if (!badgeType || !BADGES[badgeType]) return null;

    const badge = BADGES[badgeType];

    return (
        <span className={`supporter-badge ${badge.className}`} title={badge.label}>
            {badge.icon}
        </span>
    );
}

export default SupporterBadge;
