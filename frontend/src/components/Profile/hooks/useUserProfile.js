import { useState, useEffect } from 'react';
import { getMe, getUserRatings, getUserProfile, getUserGames } from '../../../api';

export function useUserProfile(urlUserId) {
    const [user, setUser] = useState(null);
    const [ratings, setRatings] = useState([]);
    const [overall, setOverall] = useState(1500);
    const [isOwnProfile, setIsOwnProfile] = useState(false);
    const [games, setGames] = useState([]);
    const [filterVariant, setFilterVariant] = useState('all');
    const [filterResult, setFilterResult] = useState('all');

    useEffect(() => {
        if (urlUserId) {
            getUserProfile(urlUserId).then(data => {
                setUser(data.user);
                setRatings(data.ratings);
                setOverall(data.overall);
                getMe().then(meData => {
                    setIsOwnProfile(meData.user && String(meData.user.id) === String(urlUserId));
                }).catch(() => setIsOwnProfile(false));
            }).catch(console.error);
        } else {
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

    useEffect(() => {
        if (user?.id) {
            const filters = {};
            if (filterVariant !== 'all') filters.variant = filterVariant;
            if (filterResult !== 'all') filters.result = filterResult;
            
            getUserGames(user.id, filters).then(data => {
                if (data?.games) setGames(data.games);
            }).catch(console.error);
        }
    }, [user, filterVariant, filterResult]);

    return {
        user, ratings, overall, isOwnProfile, games,
        filterVariant, setFilterVariant,
        filterResult, setFilterResult
    };
}
