import { useState, useEffect } from 'react';
import { getMe } from '../../../api';

export function useUserSession() {
    const [user, setUser] = useState(null);
    const [startingTime, setStartingTime] = useState(10);
    const [increment, setIncrement] = useState(0);
    const [isTimeControlEnabled, setIsTimeControlEnabled] = useState(true);

    useEffect(() => {
        getMe().then(data => {
            if (data.user) {
                setUser(data.user);
                if (data.user.default_time !== undefined) setStartingTime(data.user.default_time);
                if (data.user.default_increment !== undefined) setIncrement(data.user.default_increment);
                if (data.user.default_time_control_enabled !== undefined) {
                    setIsTimeControlEnabled(data.user.default_time_control_enabled);
                }
            }
        }).catch(e => console.error("Failed to fetch user:", e));
    }, []);

    return {
        user,
        startingTime,
        setStartingTime,
        increment,
        setIncrement,
        isTimeControlEnabled,
        setIsTimeControlEnabled
    };
}
