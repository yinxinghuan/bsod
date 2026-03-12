import React, { forwardRef, useEffect, useRef, useState } from 'react';
import iconEnergy from '../img/icon_energy.png';
import iconMood from '../img/icon_mood.png';
import iconFocus from '../img/icon_focus.png';
import iconFollowers from '../img/icon_followers.png';
import { playCountTick } from '../utils/sounds';
import './StatusBar.less';

interface Props {
  energy: number;
  mood: number;
  focus: number;
  followers: number;
  day: number;
  phase: string;
  streamedToday: boolean;
  onHelpOpen: () => void;
  /** Pre-change snapshot — when provided, animate changed stats from these values to current */
  statAnimFrom?: { energy: number; mood: number; focus: number; followers: number };
  /** Called after all stat animations complete */
  onStatAnimEnd?: () => void;
}

const DAY_PHASES = ['morning', 'afternoon', 'evening', 'night'] as const;
type DayPhase = typeof DAY_PHASES[number];

const PHASE_LABEL: Record<DayPhase, string> = {
  morning: 'AM', afternoon: 'PM', evening: 'EVE', night: 'NIGHT',
};

const PHASE_FILL: Record<string, number> = {
  morning: 0, afternoon: 33, evening: 66, night: 100, stream: 66,
};

const STAT_DUR_MS = 650; // duration per stat countdown

const StatusBar = React.memo(
  forwardRef<HTMLDivElement, Props>(function StatusBar(
    { energy, mood, focus, followers, day, phase, streamedToday, onHelpOpen,
      statAnimFrom, onStatAnimEnd }, ref
  ) {
    const activePhase: DayPhase | null =
      (DAY_PHASES as readonly string[]).includes(phase) ? phase as DayPhase
      : phase === 'stream' ? 'evening' : null;
    const activeIdx = activePhase ? DAY_PHASES.indexOf(activePhase) : -1;
    const fillPct = PHASE_FILL[phase] ?? 0;

    // Animated display values — start at current, overridden during drain animation
    const [anim, setAnim] = useState({ energy, mood, focus, followers });
    const onStatAnimEndRef = useRef(onStatAnimEnd);
    onStatAnimEndRef.current = onStatAnimEnd;

    // Sync anim values with real values when not animating
    useEffect(() => {
      if (!statAnimFrom) {
        setAnim({ energy, mood, focus, followers });
      }
    }, [energy, mood, focus, followers, statAnimFrom]);

    // Run sequential countdown animation for each changed stat
    useEffect(() => {
      if (!statAnimFrom) return;

      type StatKey = 'energy' | 'mood' | 'focus' | 'followers';
      const ALL_STATS: StatKey[] = ['energy', 'mood', 'focus', 'followers'];
      const targets: Record<StatKey, number> = { energy, mood, focus, followers };

      // Only animate stats that actually changed
      const changed = ALL_STATS.filter(k => statAnimFrom[k] !== targets[k]);
      if (changed.length === 0) {
        onStatAnimEndRef.current?.();
        return;
      }

      setAnim({ ...statAnimFrom });

      let statIdx = 0;
      let elapsed = 0;
      let lastTime = performance.now();
      let rafId: number;
      let prevDisplayVal = statAnimFrom[changed[0]];

      function step(now: number) {
        const dt = now - lastTime;
        lastTime = now;
        elapsed += dt;

        const key = changed[statIdx];
        const from = statAnimFrom![key];
        const to = targets[key];
        const t = Math.min(elapsed / STAT_DUR_MS, 1);
        const val = Math.round(from + (to - from) * t);

        if (val !== prevDisplayVal) {
          playCountTick(to > from);
          prevDisplayVal = val;
        }

        setAnim(prev => ({ ...prev, [key]: val }));

        if (t >= 1) {
          elapsed = 0;
          statIdx++;
          if (statIdx >= changed.length) {
            onStatAnimEndRef.current?.();
            return;
          }
          prevDisplayVal = statAnimFrom![changed[statIdx]];
        }
        rafId = requestAnimationFrame(step);
      }

      rafId = requestAnimationFrame(step);
      return () => cancelAnimationFrame(rafId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [statAnimFrom]);

    return (
      <div className="bs-status" ref={ref} onPointerDown={onHelpOpen}>

        {/* Row 1: DAY + followers */}
        <div className="bs-status__top">
          <div className="bs-status__day">
            <span className="bs-status__day-label">DAY</span>
            <span className="bs-status__day-num">{day}</span>
            <span className="bs-status__day-slash">/ 13</span>
          </div>
          <div className="bs-status__right">
            <div className="bs-status__flw">
              <img className="bs-status__flw-icon" src={iconFollowers} alt="" draggable={false} />
              <span className={`bs-status__flw-num${statAnimFrom && anim.followers !== followers ? ' bs-status__flw-num--counting' : ''}`}>
                {anim.followers.toLocaleString()}
              </span>
            </div>
            <span className="bs-status__help-hint">?</span>
          </div>
        </div>

        {/* Row 2: 3 stats side by side */}
        <div className="bs-status__stats">
          <Stat icon={iconEnergy} value={anim.energy} color="var(--bs-energy)" />
          <Stat icon={iconMood}   value={anim.mood}   color="var(--bs-mood)" />
          <Stat icon={iconFocus}  value={anim.focus}  color="var(--bs-focus)" />
        </div>

        {/* Row 3: Day timeline — pixel progress bar */}
        <div className="bs-timeline">
          <div className="bs-timeline__track">
          <div className="bs-timeline__bar">
            <div className="bs-timeline__fill" style={{ width: `${fillPct}%` }} />
            {/* LIVE zone highlight (evening = 66–100%) */}
            <div className="bs-timeline__live-zone" />
            {/* Tick marks at phase boundaries */}
            <div className="bs-timeline__tick" style={{ left: '33%' }} />
            <div className="bs-timeline__tick bs-timeline__tick--live" style={{ left: '66%' }} />
            {/* Current phase cursor — protrudes above/below bar */}
            {activeIdx >= 0 && (
              <div className="bs-timeline__cursor"
                   style={{ left: `${[0, 33, 66, 100][activeIdx]}%` }} />
            )}
          </div>
          <div className="bs-timeline__labels">
            {DAY_PHASES.map((p, i) => {
              const pct  = [0, 33, 66, 100][i];
              const isActive = i === activeIdx;
              const isPast   = i < activeIdx;
              const isLive   = p === 'evening';
              const isDone   = isLive && streamedToday;
              return (
                <div key={p} className="bs-timeline__lbl-item" style={{ left: `${pct}%` }}>
                  <span className={[
                    'bs-timeline__lbl',
                    isActive ? 'bs-timeline__lbl--active' : '',
                    isPast   ? 'bs-timeline__lbl--past'   : '',
                  ].join(' ')}>
                    {PHASE_LABEL[p]}
                  </span>
                  {isLive && (
                    <span className={[
                      'bs-timeline__live-tag',
                      isActive && !isDone ? 'bs-timeline__live-tag--on' : '',
                      isDone ? 'bs-timeline__live-tag--done' : '',
                    ].join(' ')}>
                      {isDone ? '✓' : 'LIVE'}
                    </span>
                  )}
                </div>
              );
            })}
          </div>
          </div>
        </div>

      </div>
    );
  })
);

function Stat({ icon, value, color }: { icon: string; value: number; color: string }) {
  const danger = value <= 20;
  return (
    <div className="bs-stat">
      <img className="bs-stat__icon" src={icon} alt="" draggable={false} />
      <span className={`bs-stat__num ${danger ? 'bs-stat__num--danger' : ''}`}
            style={danger ? undefined : { color }}>
        {Math.round(value)}
      </span>
    </div>
  );
}

StatusBar.displayName = 'StatusBar';
export default StatusBar;
