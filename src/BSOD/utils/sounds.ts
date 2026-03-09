/**
 * BSOD — synthesized sound effects via Web Audio API.
 * All sounds are procedurally generated (no audio files needed).
 */

let audioCtx: AudioContext | null = null;

const ctx = (): AudioContext => {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
  }
  return audioCtx;
};

export const resumeAudio = (): void => {
  const c = ctx();
  if (c.state === 'suspended') c.resume();
};

// ── Helpers ──────────────────────────────────────────────────────────────────

type OscType = OscillatorType;

function tone(
  freq: number, duration: number,
  { type = 'sine' as OscType, gain = 0.12, freqEnd = freq, gainEnd = 0.001,
    delay = 0 } = {}
): void {
  try {
    const c = ctx();
    const now = c.currentTime + delay;
    const osc = c.createOscillator();
    const g   = c.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, now);
    if (freqEnd !== freq) osc.frequency.exponentialRampToValueAtTime(freqEnd, now + duration);
    g.gain.setValueAtTime(gain, now);
    g.gain.exponentialRampToValueAtTime(gainEnd, now + duration);
    osc.connect(g).connect(c.destination);
    osc.start(now);
    osc.stop(now + duration);
  } catch { /* ignore */ }
}

// ── UI ────────────────────────────────────────────────────────────────────────

/** Soft click — action button press */
export const playClick = (): void => {
  tone(220, 0.05, { type: 'square', gain: 0.06, freqEnd: 180 });
};

/** Confirm — action executed */
export const playConfirm = (): void => {
  tone(440, 0.07, { type: 'square', gain: 0.08, freqEnd: 520 });
  tone(520, 0.08, { type: 'square', gain: 0.06, freqEnd: 600, delay: 0.07 });
};

/** Help panel open */
export const playPanelOpen = (): void => {
  tone(600, 0.06, { type: 'sine', gain: 0.06, freqEnd: 700 });
};

// ── Game events ───────────────────────────────────────────────────────────────

/** Game start — digital boot-up */
export const playGameStart = (): void => {
  [0, 0.08, 0.16, 0.26].forEach((delay, i) => {
    const freqs = [220, 330, 440, 660];
    tone(freqs[i], 0.1, { type: 'square', gain: 0.07, freqEnd: freqs[i] * 1.05, delay });
  });
};

/** Stream start — electric buzz then sweep up */
export const playStreamStart = (): void => {
  tone(80, 0.12, { type: 'sawtooth', gain: 0.1, freqEnd: 120 });
  tone(440, 0.18, { type: 'square', gain: 0.08, freqEnd: 880, delay: 0.1 });
  tone(880, 0.2,  { type: 'sine',   gain: 0.09, freqEnd: 1100, delay: 0.25 });
};

/** Story event triggered — soft ping */
export const playEvent = (): void => {
  tone(880, 0.08, { type: 'sine', gain: 0.1, freqEnd: 1100 });
  tone(660, 0.15, { type: 'sine', gain: 0.07, freqEnd: 600, delay: 0.08 });
};

/** Stat change positive — upward chirp */
export const playStatUp = (): void => {
  tone(440, 0.06, { type: 'square', gain: 0.07 });
  tone(660, 0.08, { type: 'square', gain: 0.06, delay: 0.06 });
};

/** Stat change negative — downward buzz */
export const playStatDown = (): void => {
  tone(300, 0.1, { type: 'sawtooth', gain: 0.08, freqEnd: 180 });
};

/** Day end — short summary jingle */
export const playDayEnd = (): void => {
  [[440, 0], [550, 0.1], [660, 0.2], [880, 0.32]].forEach(([freq, delay]) => {
    tone(freq, 0.12, { type: 'square', gain: 0.08, delay });
  });
};

/** Game over — somber descending tone */
export const playGameOver = (): void => {
  tone(440, 0.25, { type: 'sawtooth', gain: 0.1, freqEnd: 330 });
  tone(330, 0.3,  { type: 'sawtooth', gain: 0.09, freqEnd: 220, delay: 0.2 });
  tone(220, 0.5,  { type: 'sawtooth', gain: 0.08, freqEnd: 110, delay: 0.45 });
};

/** Victory ending — uplifting arpeggio */
export const playVictory = (): void => {
  [[440, 0], [550, 0.1], [660, 0.2], [880, 0.32], [1100, 0.46]].forEach(([freq, delay]) => {
    tone(freq, 0.15, { type: 'sine', gain: 0.09, freqEnd: freq * 1.02, delay });
  });
};
