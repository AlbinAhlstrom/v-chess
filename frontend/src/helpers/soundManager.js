import { Howl } from 'howler';

const sounds = {
    // Core Game Sounds (Wooden/Classic)
    move: new Howl({ src: ['/sounds/move.mp3'], volume: 0.8 }),
    capture: new Howl({ src: ['/sounds/capture.mp3'], volume: 0.9 }),
    castle: new Howl({ src: ['/sounds/castle.mp3'], volume: 0.8 }),
    check: new Howl({ src: ['/sounds/check.mp3'], volume: 0.9 }),
    promote: new Howl({ src: ['/sounds/promote.mp3'], volume: 0.8 }),
    illegal: new Howl({ src: ['/sounds/illegal.mp3'], volume: 0.7 }),
    gameStart: new Howl({ src: ['/sounds/game-start.mp3'], volume: 0.8 }),
    premove: new Howl({ src: ['/sounds/premove.mp3'], volume: 0.6 }),
    victory: new Howl({ src: ['/sounds/win-sound.wav'], volume: 1.0 }),
    
    // Visceral Variant SFX (High-Quality Kenney Physical Assets)
    
    // Atomic: Heavy, deep mining impact
    explosion: new Howl({ 
        src: ['/sounds/atomic_explosion.mp3'], 
        volume: 1.0 
    }),

    caution: new Howl({ 
        src: ['/sounds/caution.wav'], 
        volume: 0.8 
    }),
    
    // Antichess: Heavy crystalline glass shatter
    shatter: new Howl({ 
        src: ['/sounds/kenney_impact-sounds/Audio/impactGlass_heavy_000.ogg'], 
        volume: 0.8 
    }),
    
    // Crazyhouse: Light metallic plate clink for the pocket
    clink: new Howl({ 
        src: ['/sounds/kenney_impact-sounds/Audio/impactMetal_light_001.ogg'], 
        volume: 0.6 
    }),
    
    // Standard: Solid heavy plate thud for royal slam
    slam: new Howl({ 
        src: ['/sounds/kenney_impact-sounds/Audio/impactPlate_heavy_000.ogg'], 
        volume: 1.0 
    }),
    
    // Three-Check: Sharp metallic strike
    strike: new Howl({ 
        src: ['/sounds/kenney_impact-sounds/Audio/impactMetal_heavy_001.ogg'], 
        volume: 0.8 
    }),
    
    // Chess960: Mechanical drop/lock
    lock: new Howl({ 
        src: ['/sounds/kenney_interface-sounds/Audio/drop_004.ogg'], 
        volume: 0.9 
    }),

    // UI Feedback
    click: new Howl({ 
        src: ['/sounds/kenney_interface-sounds/Audio/click_001.ogg'], 
        volume: 0.4 
    }),
    whoosh: new Howl({ 
        src: ['/sounds/castle.mp3'], 
        rate: 1.5, 
        volume: 0.6 
    })
};

const SoundManager = {
    play: (name) => {
        if (sounds[name]) {
            // Restart if already playing for sharp, overlapping sounds
            if (sounds[name].playing() && name !== 'victory') {
                sounds[name].stop();
            }
            sounds[name].play();
        } else {
            console.warn(`Sound "${name}" not found in SoundManager.`);
        }
    },
    stop: (name) => {
        if (sounds[name]) {
            sounds[name].stop();
        }
    },
    stopAll: () => {
        Object.values(sounds).forEach(s => s.stop());
    }
};

export default SoundManager;
