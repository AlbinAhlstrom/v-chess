import React from 'react';
import './Settings.css';

// Subcomponents
import { GamePreferences } from './subcomponents/GamePreferences';
import { TimeControlSettings } from './subcomponents/TimeControlSettings';

// Hooks
import { useSettings } from './hooks/useSettings';

function Settings() {
    const {
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
    } = useSettings();

    return (
        <div className='settings-container'>
            <div className='settings-card'>
                <h1>Account Settings</h1>
                
                <GamePreferences 
                    autoPromote={autoPromote}
                    handleAutoPromoteToggle={handleAutoPromoteToggle}
                    showCoordinates={showCoordinates}
                    handleCoordinatesToggle={handleCoordinatesToggle}
                />

                {user && (
                    <TimeControlSettings 
                        timeControlEnabled={timeControlEnabled}
                        setTimeControlEnabled={setTimeControlEnabled}
                        defaultTime={defaultTime}
                        setDefaultTime={setDefaultTime}
                        defaultIncrement={defaultIncrement}
                        setDefaultIncrement={setDefaultIncrement}
                        saveSettings={saveSettings}
                        saving={saving}
                    />
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