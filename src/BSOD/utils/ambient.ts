/**
 * BSOD — Ambient sound system: rain + dark drone pad.
 * All procedurally generated via Web Audio API.
 */

let audioCtx: AudioContext | null = null;
let running = false;

// Nodes
let rainSource: AudioBufferSourceNode | null = null;
let rainGain: GainNode | null = null;
let rainFilter: BiquadFilterNode | null = null;
let padOsc1: OscillatorNode | null = null;
let padOsc2: OscillatorNode | null = null;
let padGain: GainNode | null = null;
let masterGain: GainNode | null = null;

const getCtx = (): AudioContext => {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
  }
  return audioCtx;
};

function createNoiseBuffer(ctx: AudioContext, seconds = 2): AudioBuffer {
  const size = ctx.sampleRate * seconds;
  const buf = ctx.createBuffer(1, size, ctx.sampleRate);
  const data = buf.getChannelData(0);
  // Brown noise — integrated white noise for rain-like rumble
  let last = 0;
  for (let i = 0; i < size; i++) {
    const white = Math.random() * 2 - 1;
    last = (last + 0.02 * white) / 1.02;
    data[i] = last * 3.5;
  }
  return buf;
}

// Scene parameters: rain volume, pad volume, filter cutoff, pad base frequency
const SCENE: Record<string, { rain: number; pad: number; freq: number; padHz: number }> = {
  morning:   { rain: 0.04, pad: 0.005, freq: 900,  padHz: 65 },
  afternoon: { rain: 0.05, pad: 0.006, freq: 700,  padHz: 62 },
  evening:   { rain: 0.07, pad: 0.008, freq: 550,  padHz: 58 },
  night:     { rain: 0.09, pad: 0.009, freq: 400,  padHz: 55 },
  stream:    { rain: 0.07, pad: 0.008, freq: 550,  padHz: 58 },
  event:     { rain: 0.06, pad: 0.007, freq: 500,  padHz: 56 },
  dayEnd:    { rain: 0.05, pad: 0.006, freq: 600,  padHz: 60 },
};

const FADE = 1.5; // seconds for crossfade

export function startAmbient(scene = 'morning'): void {
  if (running) return;
  running = true;

  const ctx = getCtx();
  const now = ctx.currentTime;

  // Master gain
  masterGain = ctx.createGain();
  masterGain.gain.setValueAtTime(0.001, now);
  masterGain.gain.exponentialRampToValueAtTime(1, now + FADE);
  masterGain.connect(ctx.destination);

  // ── Rain layer ──
  const noiseBuf = createNoiseBuffer(ctx, 3);
  rainSource = ctx.createBufferSource();
  rainSource.buffer = noiseBuf;
  rainSource.loop = true;

  rainFilter = ctx.createBiquadFilter();
  rainFilter.type = 'lowpass';
  rainFilter.Q.value = 0.8;

  rainGain = ctx.createGain();

  rainSource.connect(rainFilter).connect(rainGain).connect(masterGain);
  rainSource.start(now);

  // ── Drone pad (two detuned oscillators) ──
  padGain = ctx.createGain();

  padOsc1 = ctx.createOscillator();
  padOsc1.type = 'sine';

  padOsc2 = ctx.createOscillator();
  padOsc2.type = 'triangle';

  const padFilter = ctx.createBiquadFilter();
  padFilter.type = 'lowpass';
  padFilter.frequency.value = 200;
  padFilter.Q.value = 1;

  padOsc1.connect(padFilter);
  padOsc2.connect(padFilter);
  padFilter.connect(padGain).connect(masterGain);

  padOsc1.start(now);
  padOsc2.start(now);

  // Apply initial scene
  setAmbientScene(scene);
}

export function setAmbientScene(scene: string): void {
  if (!running || !rainGain || !rainFilter || !padGain || !padOsc1 || !padOsc2) return;
  const ctx = getCtx();
  const now = ctx.currentTime;
  const p = SCENE[scene] ?? SCENE.morning;

  rainGain.gain.cancelScheduledValues(now);
  rainGain.gain.setValueAtTime(rainGain.gain.value, now);
  rainGain.gain.linearRampToValueAtTime(p.rain, now + FADE);

  rainFilter.frequency.cancelScheduledValues(now);
  rainFilter.frequency.setValueAtTime(rainFilter.frequency.value, now);
  rainFilter.frequency.linearRampToValueAtTime(p.freq, now + FADE);

  padGain.gain.cancelScheduledValues(now);
  padGain.gain.setValueAtTime(padGain.gain.value, now);
  padGain.gain.linearRampToValueAtTime(p.pad, now + FADE);

  padOsc1.frequency.cancelScheduledValues(now);
  padOsc1.frequency.setValueAtTime(padOsc1.frequency.value, now);
  padOsc1.frequency.linearRampToValueAtTime(p.padHz, now + FADE);

  padOsc2.frequency.cancelScheduledValues(now);
  padOsc2.frequency.setValueAtTime(padOsc2.frequency.value, now);
  padOsc2.frequency.linearRampToValueAtTime(p.padHz * 1.003, now + FADE); // slight detune
}

export function stopAmbient(): void {
  if (!running) return;
  running = false;
  const ctx = getCtx();
  const now = ctx.currentTime;

  if (masterGain) {
    masterGain.gain.cancelScheduledValues(now);
    masterGain.gain.setValueAtTime(masterGain.gain.value, now);
    masterGain.gain.exponentialRampToValueAtTime(0.001, now + FADE);
  }

  // Clean up after fade
  setTimeout(() => {
    try { rainSource?.stop(); } catch { /* */ }
    try { padOsc1?.stop(); } catch { /* */ }
    try { padOsc2?.stop(); } catch { /* */ }
    try { masterGain?.disconnect(); } catch { /* */ }
    rainSource = null; rainGain = null; rainFilter = null;
    padOsc1 = null; padOsc2 = null; padGain = null;
    masterGain = null;
  }, FADE * 1000 + 200);
}
