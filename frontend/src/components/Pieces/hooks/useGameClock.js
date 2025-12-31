import { useState, useEffect } from 'react';

export function useGameClock(isGameOver, moveHistoryLength, turn) {
    const [timers, setTimers] = useState(null); // {w: seconds, b: seconds}

    // Timer formatting helper
    const formatTime = (seconds) => {
        if (seconds === null || seconds === undefined) return "";
        const s = Math.max(0, Math.floor(seconds));
        const mins = Math.floor(s / 60);
        const secs = s % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    // Live countdown effect
    useEffect(() => {
        if (!timers || isGameOver || moveHistoryLength === 0) return;

        const interval = setInterval(() => {
            setTimers(prev => {
                if (!prev) return prev;
                return {
                    ...prev,
                    [turn]: Math.max(0, prev[turn] - 0.1)
                };
            });
        }, 100);

        return () => clearInterval(interval);
    }, [timers, turn, isGameOver, moveHistoryLength]);

    return {
        timers,
        setTimers,
        formatTime
    };
}
