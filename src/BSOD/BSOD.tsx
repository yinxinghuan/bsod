import React, { forwardRef, useState, useEffect, useRef } from 'react';
import { useBSOD } from './hooks/useBSOD';
import type { GameState } from './types';
import StatusBar from './components/StatusBar';
import ActionPanel from './components/ActionPanel';
import EventOverlay from './components/EventOverlay';
import StreamSession from './components/StreamSession';
import DayEndScreen from './components/DayEndScreen';
import EndingScreen from './components/EndingScreen';
import DeathScreen from './components/DeathScreen';
import ActionResultScreen from './components/ActionResultScreen';
import SplashScreen from './components/SplashScreen';
import NoiseCanvas from './components/NoiseCanvas';
import HelpPanel from './components/HelpPanel';
import bgRoom from './img/bg_room.png';
import laisaIdle from './img/laisa_idle.png';
import laisaHappy from './img/laisa_happy.png';
import laisaSad from './img/laisa_sad.png';
import laisaSurprised from './img/laisa_surprised.png';
import laisaTired from './img/laisa_tired.png';
import laisaFocused from './img/laisa_focused.png';
import aigramLogo from './img/aigram.svg';
import {
  resumeAudio, playClick, playConfirm, playPanelOpen,
  playGameStart, playStreamStart, playEvent, playStatUp, playStatDown,
  playDayEnd, playGameOver, playVictory,
} from './utils/sounds';
import './BSOD.less';

// Preload all heavy assets so first gameplay frame has no flicker
const PRELOAD_ASSETS = [
  bgRoom, laisaIdle, laisaHappy, laisaSad, laisaSurprised, laisaTired, laisaFocused,
];
PRELOAD_ASSETS.forEach(src => { const img = new Image(); img.src = src; });

const LAISA_IMGS: Record<string, string> = {
  normal:    laisaIdle,
  idle:      laisaIdle,
  happy:     laisaHappy,
  sad:       laisaSad,
  surprised: laisaSurprised,
  tired:     laisaTired,
  focused:   laisaFocused,
};

function getLaisaVisible(state: GameState): { visible: boolean; emotion: string } {
  const { phase, pendingEvent, lastAction } = state;
  if (phase === 'event' && pendingEvent) {
    return { visible: true, emotion: pendingEvent.laisaEmotion ?? 'normal' };
  }
  if (phase === 'actionResult' && lastAction) {
    const { energy = 0, mood = 0, focus = 0 } = lastAction.effect;
    const total = energy + mood + focus;
    if (Math.abs(total) >= 6) {
      return { visible: true, emotion: total > 0 ? 'happy' : 'sad' };
    }
  }
  return { visible: false, emotion: 'normal' };
}

// CSS filter classes for time of day simulation
const PHASE_FILTER: Record<string, string> = {
  morning:   'bs--morning',
  afternoon: 'bs--afternoon',
  evening:   'bs--evening',
  night:     'bs--night',
  stream:    'bs--night',
  event:     'bs--night',
  dayEnd:    'bs--night',
};

const BSOD = React.memo(
  forwardRef<HTMLDivElement, Record<string, never>>(function BSOD(_props, ref) {
    const { state, actions, currentPhaseActions } = useBSOD();
    const { phase, day, energy, mood, focus, followers, streamedToday } = state;

    const [showSplash, setShowSplash] = useState(true);
    const [showHelp, setShowHelp] = useState(false);

    // ── Phase-change sound effects ────────────────────────────────────────────
    const prevPhase = useRef(phase);
    useEffect(() => {
      const prev = prevPhase.current;
      prevPhase.current = phase;
      if (prev === phase) return;
      if (phase === 'stream')    playStreamStart();
      if (phase === 'event')     playEvent();
      if (phase === 'dayEnd')    playDayEnd();
      if (phase === 'dead')      playGameOver();
      if (phase === 'ending') {
        if (state.endingType === 'online' || state.endingType === 'restart') playVictory();
        else playGameOver();
      }
    }, [phase, state.endingType]);

    // Stat-change feedback (big swings only)
    const prevStats = useRef({ energy, mood, focus });
    useEffect(() => {
      const prev = prevStats.current;
      prevStats.current = { energy, mood, focus };
      const delta = (energy - prev.energy) + (mood - prev.mood) + (focus - prev.focus);
      if (delta >= 8) playStatUp();
      else if (delta <= -8) playStatDown();
    }, [energy, mood, focus]);

    // ── Sound-wrapped actions ─────────────────────────────────────────────────
    const sfx = {
      startGame: () => {
        resumeAudio();
        playGameStart();
        actions.startGame();
      },
      restart: () => {
        resumeAudio();
        playGameStart();
        actions.restart();
      },
      chooseAction: (action: Parameters<typeof actions.chooseAction>[0]) => {
        playConfirm();
        const before = { energy, mood, focus };
        actions.chooseAction(action);
        // stat feedback fires after state updates — effect handled in prev render delta
        void before;
      },
      chooseEventOption: (choice: Parameters<typeof actions.chooseEventOption>[0]) => {
        playConfirm();
        actions.chooseEventOption(choice);
      },
      chooseStreamOption: (...args: Parameters<typeof actions.chooseStreamOption>) => {
        playConfirm();
        actions.chooseStreamOption(...args);
      },
      dismissActionResult: () => {
        playClick();
        actions.dismissActionResult();
      },
      dismissEvent: () => {
        playClick();
        actions.dismissEvent();
      },
      confirmDayEnd: () => {
        playClick();
        actions.confirmDayEnd();
      },
    };

    const { visible: laisaVisible, emotion: laisaEmotion } = getLaisaVisible(state);
    const laisaSrc = LAISA_IMGS[laisaEmotion] ?? laisaIdle;
    const filterClass = PHASE_FILTER[phase] ?? 'bs--night';


    // ── Splash screen ─────────────────────────────────────────────────────
    if (showSplash) {
      return (
        <div className="bs" ref={ref}>
          <SplashScreen onDone={() => setShowSplash(false)} />
        </div>
      );
    }

    // ── Start screen ──────────────────────────────────────────────────────
    if (phase === 'start') {
      return (
        <div className="bs" ref={ref}>
          <img className="bs__watermark" src={aigramLogo} alt="Aigram" draggable={false} />
          <img className="bs__start-bg" src={bgRoom} alt="" draggable={false} />
          <NoiseCanvas opacity={0.72} className="bs__start-noise" />
          <div className="bs__start">
            <div className="bs__start-content">
              <h1 className="bs__start-title">BSOD</h1>
              <p className="bs__start-tagline">BLUE SCREEN OF DOOM</p>
              <p className="bs__start-subtitle">A 13-day streaming survival</p>
              <button className="bs__start-btn" onPointerDown={sfx.startGame}>
                START GAME
              </button>
            </div>
          </div>
        </div>
      );
    }

    // ── Death screen ──────────────────────────────────────────────────────
    if (phase === 'dead' && state.deathCause) {
      return (
        <div className="bs" ref={ref}>
          <img className="bs__watermark" src={aigramLogo} alt="Aigram" draggable={false} />
          <DeathScreen
            cause={state.deathCause}
            statValue={
              state.deathCause === 'energy' ? energy :
              state.deathCause === 'mood'   ? mood   :
              state.deathCause === 'focus'  ? focus  : followers
            }
            followers={followers}
            onRestart={sfx.restart}
          />
        </div>
      );
    }

    // ── Ending screen ─────────────────────────────────────────────────────
    if (phase === 'ending' && state.endingType) {
      return (
        <div className="bs" ref={ref}>
          <img className="bs__watermark" src={aigramLogo} alt="Aigram" draggable={false} />
          <EndingScreen
            endingType={state.endingType}
            followers={followers}
            connection={state.connection}
            onRestart={sfx.restart}
          />
        </div>
      );
    }

    // ── Day end screen ────────────────────────────────────────────────────
    if (phase === 'dayEnd') {
      return (
        <div className="bs" ref={ref}>
          <img className="bs__watermark" src={aigramLogo} alt="Aigram" draggable={false} />
          {showHelp && <HelpPanel onClose={() => setShowHelp(false)} />}
          <StatusBar
            energy={energy} mood={mood} focus={focus}
            followers={followers} day={day} phase={phase}
            streamedToday={state.streamedToday}
            onHelpOpen={() => { playPanelOpen(); setShowHelp(true); }}
          />
          <DayEndScreen state={state} onContinue={sfx.confirmDayEnd} />
        </div>
      );
    }

    // ── Main game screen ──────────────────────────────────────────────────
    return (
      <div className="bs" ref={ref}>
        <img className="bs__watermark" src={aigramLogo} alt="Aigram" draggable={false} />
        {showHelp && <HelpPanel onClose={() => setShowHelp(false)} />}

        {/* Room background with time-of-day filter */}
        <div className={`bs__bg-wrap${phase === 'event' ? ' bs__bg-wrap--blur' : ''}`}>
          <img
            className={`bs__bg ${filterClass}`}
            src={bgRoom}
            alt=""
            draggable={false}
          />
        </div>

        {/* Status bar */}
        <StatusBar
          energy={energy} mood={mood} focus={focus}
          followers={followers} day={day} phase={phase}
          streamedToday={streamedToday}
          onHelpOpen={() => { playPanelOpen(); setShowHelp(true); }}
        />

        {/* Laisa character sprite — only during events / big stat changes */}
        {laisaVisible && (
          <div className="bs__char-area">
            <img
              className="bs__char"
              src={laisaSrc}
              alt="Laisa"
              draggable={false}
            />
          </div>
        )}

        {/* Action panel — bottom overlay */}
        <div className="bs__panel">
          <ActionPanel
            phase={phase}
            actions={currentPhaseActions}
            onChoose={sfx.chooseAction}
          />
        </div>

        {/* Stream session — full screen overlay */}
        {phase === 'stream' && state.streamQueue[state.streamIndex] && (
          <StreamSession
            event={state.streamQueue[state.streamIndex]}
            eventIndex={state.streamIndex}
            totalEvents={state.streamQueue.length}
            onChoose={sfx.chooseStreamOption}
            lastFollowerEvent={state.streamLastEvent}
            pendingEnd={state.streamPendingEnd}
            onStreamEnd={actions.confirmStreamEnd}
          />
        )}

        {/* Action result screen */}
        {phase === 'actionResult' && state.lastAction && (
          <ActionResultScreen
            action={state.lastAction}
            onDismiss={sfx.dismissActionResult}
          />
        )}

        {/* Story event overlay */}
        {phase === 'event' && state.pendingEvent && (
          <EventOverlay
            event={state.pendingEvent}
            onChoice={idx => sfx.chooseEventOption(state.pendingEvent!.choices![idx])}
            onDismiss={sfx.dismissEvent}
          />
        )}
      </div>
    );
  })
);

BSOD.displayName = 'BSOD';
export default BSOD;
