import React, { useState } from 'react';
import './UsernamePrompt.css';
import { setUsername } from '../../api';

function UsernamePrompt({ onComplete }) {
    const [name, setName] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        
        if (name.length < 3) {
            setError('Username must be at least 3 characters');
            return;
        }

        setLoading(true);
        try {
            const res = await setUsername(name);
            if (res.status === 'success') {
                onComplete(res.username);
            } else {
                setError(res.detail || 'Failed to set username');
            }
        } catch (err) {
            setError('An unexpected error occurred');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="username-prompt-overlay">
            <div className="username-prompt-modal">
                <h1>Welcome to V-Chess!</h1>
                <p>Before you continue, please choose a unique username.</p>
                <form onSubmit={handleSubmit}>
                    <input 
                        type="text" 
                        placeholder="Username" 
                        value={name} 
                        onChange={(e) => setName(e.target.value.replace(/[^a-zA-Z0-9_\-]/g, ''))}
                        disabled={loading}
                        autoFocus
                    />
                    <p className="hint">3-20 characters. Letters, numbers, _ and - allowed.</p>
                    {error && <p className="error-message">{error}</p>}
                    <button type="submit" disabled={loading || !name}>
                        {loading ? 'Saving...' : 'Set Username'}
                    </button>
                </form>
            </div>
        </div>
    );
}

export default UsernamePrompt;
