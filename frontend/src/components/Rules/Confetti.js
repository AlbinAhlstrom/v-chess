import { useEffect } from 'react';
import confetti from 'canvas-confetti';

const Confetti = ({ trigger }) => {
    useEffect(() => {
        if (trigger) {
            // High-performance burst from the bottom center
            const duration = 3 * 1000;
            const animationEnd = Date.now() + duration;
            const defaults = { startVelocity: 45, spread: 70, ticks: 100, zIndex: 99999, gravity: 1.2, scalar: 1.2 };

            const randomInRange = (min, max) => Math.random() * (max - min) + min;

            const interval = setInterval(function() {
                const timeLeft = animationEnd - Date.now();

                if (timeLeft <= 0) {
                    return clearInterval(interval);
                }

                const particleCount = 50 * (timeLeft / duration);
                
                // Fountain burst from bottom center
                confetti({
                    ...defaults,
                    particleCount,
                    origin: { x: 0.5, y: 1.1 },
                    angle: randomInRange(75, 105), // Narrower upward cone
                    spread: randomInRange(40, 80),
                    gravity: 1.5,
                    startVelocity: randomInRange(45, 75)
                });
            }, 250);

            return () => clearInterval(interval);
        }
    }, [trigger]);

    return null; // canvas-confetti creates its own global canvas
};

export default Confetti;