import React, { useState, useEffect } from 'react';
import './Settings.css';
import { getMe, updateUserSettings } from '../../api';

function Settings() {
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

    return (
        <div className='settings-container'>
            <div className='settings-card'>
                <h1>Account Settings</h1>
                
                <section className='settings-section'>
                    <h2>Game Preferences</h2>
                    <div className='preference-row'>
                        <div className='preference-info'>
                            <span className='label'>Auto Promote to Queen</span>
                            <p className='description'>Automatically promote pawns to Queen when reaching the last row.</p>
                        </div>
                        <label className='switch'>
                            <input type='checkbox' checked={autoPromote} onChange={handleAutoPromoteToggle} />
                            <span className='slider round'></span>
                        </label>
                    </div>

                    <div className='preference-row'>
                        <div className='preference-info'>
                            <span className='label'>Show Board Coordinates</span>
                            <p className='description'>Display rank (1-8) and file (a-h) labels on the board edges.</p>
                        </div>
                        <label className='switch'>
                            <input type='checkbox' checked={showCoordinates} onChange={handleCoordinatesToggle} />
                            <span className='slider round'></span>
                        </label>
                    </div>
                </section>

                {user && (
                    <section className='settings-section'>
                        <h2>Default Time Control</h2>
                        <div className='preference-row'>
                            <div className='preference-info'>
                                <span className='label'>Enable Time Control</span>
                                <p className='description'>Use a clock by default when creating or joining games.</p>
                            </div>
                            <label className='switch'>
                                <input 
                                    type='checkbox' 
                                    checked={timeControlEnabled} 
                                    onChange={(e) => {
                                        const val = e.target.checked;
                                        setTimeControlEnabled(val);
                                        saveSettings({ timeControlEnabled: val });
                                    }} 
                                />
                                <span className='slider round'></span>
                            </label>
                        </div>

                        {timeControlEnabled && (
                            <>
                                <div className='preference-row'>
                                    <div className='preference-info'>
                                        <span className='label'>Starting Time (minutes)</span>
                                    </div>
                                    <select 
                                        className='settings-select'
                                        value={defaultTime} 
                                        onChange={(e) => {
                                            const val = parseFloat(e.target.value);
                                            setDefaultTime(val);
                                            saveSettings({ defaultTime: val });
                                        }}
                                    >
                                        <option value={0.25}>1/4 min</option>
                                        <option value={0.5}>1/2 min</option>
                                        <option value={1}>1 min</option>
                                        <option value={2}>2 min</option>
                                        <option value={3}>3 min</option>
                                        <option value={5}>5 min</option>
                                        <option value={10}>10 min</option>
                                        <option value={15}>15 min</option>
                                        <option value={30}>30 min</option>
                                    </select>
                                </div>

                                <div className='preference-row'>
                                    <div className='preference-info'>
                                        <span className='label'>Increment (seconds)</span>
                                    </div>
                                    <select 
                                        className='settings-select'
                                        value={defaultIncrement} 
                                        onChange={(e) => {
                                            const val = parseInt(e.target.value);
                                            setDefaultIncrement(val);
                                            saveSettings({ defaultIncrement: val });
                                        }}
                                    >
                                        {[0, 1, 2, 3, 5, 10, 20, 30].map(s => (
                                            <option key={s} value={s}>{s} sec</option>
                                        ))}
                                    </select>
                                </div>
                            </>
                        )}
                        {saving && <p className="saving-indicator">Saving...</p>}
                    </section>
                )}

                <section className='settings-section'>
                    <h2>About V-Chess</h2>
                    <p className='settings-info-text'>
                        V-Chess is a variant-first chess platform. Game preferences are saved to your browser, while time controls are linked to your account.
                    </p>
                </section>
            </div>
        </div>
    );
}

export default Settings;
