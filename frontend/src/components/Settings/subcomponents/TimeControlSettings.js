import React from 'react';

export function TimeControlSettings({
    timeControlEnabled,
    setTimeControlEnabled,
    defaultTime,
    setDefaultTime,
    defaultIncrement,
    setDefaultIncrement,
    saveSettings,
    saving
}) {
    return (
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
    );
}
