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
import DailyDrainNotice from './components/DailyDrainNotice';
import bgRoom from './img/bg_room.png';
import isayaIdle from './img/laisa_idle.png';
import isayaHappy from './img/laisa_happy.png';
import isayaSad from './img/laisa_sad.png';
import isayaSurprised from './img/laisa_surprised.png';
import isayaTired from './img/laisa_tired.png';
import isayaFocused from './img/laisa_focused.png';
import isayaWorn from './img/laisa_worn.png';
import isayaRundown from './img/laisa_rundown.png';
import isayaWreck from './img/laisa_wreck.png';
import isayaManic from './img/laisa_manic.png';
import {
  resumeAudio, playClick, playConfirm, playPanelOpen,
  playGameStart, playStreamStart, playEvent, playStatUp, playStatDown,
  playDayEnd, playGameOver, playVictory,
} from './utils/sounds';
import { startAmbient, setAmbientScene, stopAmbient } from './utils/ambient';
import './BSOD.less';


const ISAYA_IMGS: Record<string, string> = {
  normal:    isayaIdle,
  idle:      isayaIdle,
  happy:     isayaHappy,
  sad:       isayaSad,
  surprised: isayaSurprised,
  tired:     isayaTired,
  focused:   isayaFocused,
};

function getConditionSprite(energy: number, mood: number, focus: number): string {
  if (energy < 30 && focus > 65) return isayaManic;
  if (energy < 20 && mood < 20) return isayaWreck;
  if (energy < 30 || mood < 30) return isayaRundown;
  if (energy < 45 || mood < 45) return isayaWorn;
  if (energy >= 65 && mood >= 65) return isayaHappy;
  return isayaIdle;
}

function getIsayaVisible(state: GameState): { visible: boolean; emotion: string } {
  const { phase, pendingEvent } = state;
  if (phase === 'event' && pendingEvent) {
    return { visible: true, emotion: pendingEvent.isayaEmotion ?? 'normal' };
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
      // Ambient scene follows phase
      setAmbientScene(phase);
      if (phase === 'stream')    playStreamStart();
      if (phase === 'event')     playEvent();
      if (phase === 'dayEnd')    playDayEnd();
      if (phase === 'dead')      { playGameOver(); stopAmbient(); }
      if (phase === 'ending') {
        stopAmbient();
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
        startAmbient('morning');
        actions.startGame();
      },
      restart: () => {
        resumeAudio();
        playGameStart();
        stopAmbient();
        startAmbient('morning');
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

    const { visible: isayaVisible, emotion: isayaEmotion } = getIsayaVisible(state);
    const conditionSprite = state.showConditionSprite ? getConditionSprite(energy, mood, focus) : null;
    const isayaSrc = conditionSprite ?? (ISAYA_IMGS[isayaEmotion] ?? isayaIdle);
    const isayaShowing = isayaVisible || !!conditionSprite || state.showDrainNotice;
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
          <DeathScreen
            cause={state.deathCause}
            deathContext={state.deathContext}
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

        {/* Status bar — hidden during events */}
        {phase !== 'event' && (
          <StatusBar
            energy={energy} mood={mood} focus={focus}
            followers={followers} day={day} phase={phase}
            streamedToday={streamedToday}
            onHelpOpen={() => { playPanelOpen(); setShowHelp(true); }}
            statAnimFrom={state.statAnimFrom ?? undefined}
            onStatAnimEnd={actions.clearStatAnim}
          />
        )}

        {/* Laisa character sprite — during events or condition state after daily drain */}
        {isayaShowing && (
          <div className={`bs__char-area${phase === 'event' ? ' bs__char-area--event' : ''}`}>
            <img
              className="bs__char"
              src={isayaSrc}
              alt="Isaya"
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

        {/* Daily drain notice */}
        {state.showDrainNotice && <DailyDrainNotice />}

        {/* Story event overlay — key forces remount on each new event, resetting local state */}
        {phase === 'event' && state.pendingEvent && (
          <EventOverlay
            key={state.pendingEvent.id}
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
