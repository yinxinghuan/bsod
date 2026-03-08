import React, { forwardRef } from 'react';
import iconEnergy from '../img/icon_energy.png';
import iconMood from '../img/icon_mood.png';
import iconFocus from '../img/icon_focus.png';
import iconFollowers from '../img/icon_followers.png';
import './StatusBar.less';

interface Props {
  energy: number;
  mood: number;
  focus: number;
  followers: number;
  day: number;
  phase: string;
  streamedToday: boolean;
}

const DAY_PHASES = ['morning', 'afternoon', 'evening', 'night'] as const;
type DayPhase = typeof DAY_PHASES[number];

const PHASE_LABEL: Record<DayPhase, string> = {
  morning: 'AM', afternoon: 'PM', evening: 'EVE', night: 'NIGHT',
};

const PHASE_FILL: Record<string, number> = {
  morning: 0, afternoon: 33, evening: 66, night: 100, stream: 66,
};

const StatusBar = React.memo(
  forwardRef<HTMLDivElement, Props>(function StatusBar(
    { energy, mood, focus, followers, day, phase, streamedToday }, ref
  ) {
    const activePhase: DayPhase | null =
      (DAY_PHASES as readonly string[]).includes(phase) ? phase as DayPhase
      : phase === 'stream' ? 'evening' : null;
    const activeIdx = activePhase ? DAY_PHASES.indexOf(activePhase) : -1;
    const fillPct = PHASE_FILL[phase] ?? 0;

    return (
      <div className="bs-status" ref={ref}>

        {/* Row 1: DAY + followers */}
        <div className="bs-status__top">
          <div className="bs-status__day">
            <span className="bs-status__day-label">DAY</span>
            <span className="bs-status__day-num">{day}</span>
            <span className="bs-status__day-slash">/ 13</span>
          </div>
          <div className="bs-status__flw">
            <img className="bs-status__flw-icon" src={iconFollowers} alt="" draggable={false} />
            <span className="bs-status__flw-num">{followers.toLocaleString()}</span>
          </div>
        </div>

        {/* Row 2: 3 stats side by side */}
        <div className="bs-status__stats">
          <Stat icon={iconEnergy} value={energy} color="var(--bs-energy)" />
          <Stat icon={iconMood}   value={mood}   color="var(--bs-mood)" />
          <Stat icon={iconFocus}  value={focus}  color="var(--bs-focus)" />
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
