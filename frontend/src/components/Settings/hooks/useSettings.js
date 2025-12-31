import { useState, useEffect } from 'react';
import { getMe, updateUserSettings } from '../../../api';

export function useSettings() {
    const [user, setUser] = useState(null);
    const [autoPromote, setAutoPromote] = useState(() => {
        const saved = localStorage.getItem('autoPromoteToQueen');
        return saved !== null ? JSON.parse(saved) : true;
    });
    const [showCoordinates, setShowCoordinates] = useState(() => {
        const saved = localStorage.getItem('showBoardCoordinates');
        return saved !== null ? JSON.parse(saved) : false;
    });

    const [defaultTime, setDefaultTime] = useState(10);
    const [defaultIncrement, setDefaultIncrement] = useState(0);
    const [timeControlEnabled, setTimeControlEnabled] = useState(true);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        getMe().then(data => {
            if (data.user) {
                setUser(data.user);
                setDefaultTime(data.user.default_time || 10);
                setDefaultIncrement(data.user.default_increment || 0);
                setTimeControlEnabled(data.user.default_time_control_enabled !== undefined ? data.user.default_time_control_enabled : true);
            }
        });
    }, []);

    const saveSettings = (updatedFields) => {
        const settings = {
            default_time: updatedFields.defaultTime !== undefined ? updatedFields.defaultTime : defaultTime,
            default_increment: updatedFields.defaultIncrement !== undefined ? updatedFields.defaultIncrement : defaultIncrement,
            default_time_control_enabled: updatedFields.timeControlEnabled !== undefined ? updatedFields.timeControlEnabled : timeControlEnabled
        };
        
        setSaving(true);
        updateUserSettings(settings).then(() => {
            setSaving(false);
        }).catch(err => {
            console.error("Failed to save settings:", err);
            setSaving(false);
        });
    };

    const handleAutoPromoteToggle = () => {
        const newValue = !autoPromote;
        setAutoPromote(newValue);
        localStorage.setItem('autoPromoteToQueen', JSON.stringify(newValue));
    };

    const handleCoordinatesToggle = () => {
        const newValue = !showCoordinates;
        setShowCoordinates(newValue);
        localStorage.setItem('showBoardCoordinates', JSON.stringify(newValue));
    };

    return {
        user,
        autoPromote,
        handleAutoPromoteToggle,
        showCoordinates,
        handleCoordinatesToggle,
        defaultTime,
        setDefaultTime,
        defaultIncrement,
        setDefaultIncrement,
        timeControlEnabled,
        setTimeControlEnabled,
        saving,
        saveSettings
    };
}
