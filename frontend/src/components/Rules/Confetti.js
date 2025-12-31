import { useEffect } from 'react';
import confetti from 'canvas-confetti';

const Confetti = ({ trigger }) => {
    useEffect(() => {
        if (trigger) {
            // Add 0.2s delay as requested
            const timer = setTimeout(() => {
                // Very brief high-impact bursts
                const duration = 0.5 * 1000;
                const animationEnd = Date.now() + duration;
                const defaults = { startVelocity: 85, spread: 60, ticks: 60, zIndex: 99999, gravity: 1.4, scalar: 1.2 };

                const randomInRange = (min, max) => Math.random() * (max - min) + min;

                const interval = setInterval(function() {
                    const timeLeft = animationEnd - Date.now();

                    if (timeLeft <= 0) {
                        return clearInterval(interval);
                    }

                    const particleCount = 40 * (timeLeft / duration);
                    
                    // Three evenly spaced origins at the bottom
                    [0.2, 0.5, 0.8].forEach(xOrigin => {
                        confetti({
                            ...defaults,
                            particleCount,
                            origin: { x: xOrigin, y: 1.1 },
                            angle: randomInRange(80, 100),
                            startVelocity: randomInRange(75, 105)
                        });
                    });
                }, 150);
            }, 200); // 0.2s delay

            return () => clearTimeout(timer);
        }
    }, [trigger]);

    return null;
};

export default Confetti;
