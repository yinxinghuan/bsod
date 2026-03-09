import React, { forwardRef, useEffect, useRef, useState } from 'react';
import type { StreamEvent, ResponseSpeed, VolatileType } from '../types';
import bgStream from '../img/bg_stream.png';
import './StreamSession.less';

interface Props {
  event: StreamEvent;
  eventIndex: number;
  totalEvents: number;
  onChoose: (index: number, speed: ResponseSpeed) => void;
  lastFollowerEvent?: { delta: number; type: VolatileType; key: number } | null;
}

// ── Chat comment pool ──────────────────────────────────────────────────────────
const COMMENT_POOL = [
  'わあ！', 'aaaa', '666', '加油！', 'poggers', 'LUL',
  '哇', 'pog', '牛！', 'gg', '好耶', '冲！', 'POG', '哈哈哈',
  'OMG', '来了来了', '太强了', 'KEKW', '芜湖', 'monkaS',
  '！！！', '主播主播', 'w', '爱看', 'hype', '666666',
  'Pog', '草', '牛牛', 'Sadge', '开冲', '真的假的', 'xd', 'XD',
  '哇哦', '主播好棒', 'LMAO', '哈哈哈哈', 'NotLikeThis',
];

const TIMER_TOTAL = 8000; // ms
const FAST_THRESHOLD  = 3000;
const SLOW_THRESHOLD  = 6000;

// ── Volatile event display config ─────────────────────────────────────────────
const VOLATILE_CONFIG: Record<VolatileType, { label: string; emoji: string; colorClass: string } | null> = {
  viral:       { label: 'VIRAL',       emoji: '🔥', colorClass: 'viral' },
  boost:       { label: 'BOOST',       emoji: '⚡', colorClass: 'boost' },
  controversy: { label: 'CRASH',       emoji: '💥', colorClass: 'controversy' },
  flop:        { label: 'FLOP',        emoji: '📉', colorClass: 'flop' },
  normal:      null,
};

const StreamSession = React.memo(
  forwardRef<HTMLDivElement, Props>(function StreamSession(
    { event, eventIndex, totalEvents, onChoose, lastFollowerEvent }, ref
  ) {
    const [comments, setComments] = useState<{ id: number; text: string }[]>([]);
    const [elapsed, setElapsed] = useState(0);
    const [timedOut, setTimedOut] = useState(false);
    const [flash, setFlash] = useState<{ delta: number; type: VolatileType; key: number } | null>(null);
    const startRef = useRef(Date.now());
    const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
    const commentIdRef = useRef(0);
    const viewersRef = useRef(Math.floor(Math.random() * 120 + 60));
    const chosenRef = useRef(false);
    const flashTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    // Show volatile flash when a result comes in
    useEffect(() => {
      if (!lastFollowerEvent || lastFollowerEvent.delta === 0) return;
      setFlash(lastFollowerEvent);
      if (flashTimerRef.current) clearTimeout(flashTimerRef.current);
      flashTimerRef.current = setTimeout(() => setFlash(null), 2600);
    }, [lastFollowerEvent?.key]);

    // Reset on new event
    useEffect(() => {
      chosenRef.current = false;
      setElapsed(0);
      setTimedOut(false);
      startRef.current = Date.now();

      // Countdown tick
      timerRef.current = setInterval(() => {
        const e = Date.now() - startRef.current;
        setElapsed(e);
        if (e >= TIMER_TOTAL && !chosenRef.current) {
          clearInterval(timerRef.current!);
          setTimedOut(true);
          // Auto-choose random option after brief pause
          setTimeout(() => {
            if (!chosenRef.current) {
              chosenRef.current = true;
              onChoose(Math.floor(Math.random() * event.choices.length), 'timeout');
            }
          }, 600);
        }
      }, 80);

      return () => { if (timerRef.current) clearInterval(timerRef.current); };
    }, [eventIndex]);

    // Scrolling chat
    useEffect(() => {
      const add = () => {
        const text = COMMENT_POOL[Math.floor(Math.random() * COMMENT_POOL.length)];
        setComments(c => [...c.slice(-14), { id: commentIdRef.current++, text }]);
      };
      add();
      const iv = setInterval(add, 500);
      return () => clearInterval(iv);
    }, []);

    const handleChoose = (index: number) => {
      if (chosenRef.current) return;
      chosenRef.current = true;
      if (timerRef.current) clearInterval(timerRef.current);
      const e = Date.now() - startRef.current;
      const speed: ResponseSpeed = e < FAST_THRESHOLD ? 'fast' : e < SLOW_THRESHOLD ? 'normal' : 'slow';
      onChoose(index, speed);
    };

    const remaining = Math.max(0, TIMER_TOTAL - elapsed);
    const progress = remaining / TIMER_TOTAL; // 1 → 0
    const timerColor = progress > 0.625 ? '#4ade80' : progress > 0.25 ? '#fbbf24' : '#f87171';
    const speedHint = elapsed < FAST_THRESHOLD
      ? 'Fast reply ×1.5 followers'
      : elapsed < SLOW_THRESHOLD
        ? 'Responding…'
        : 'Chat is going cold…';

    // Render the volatile flash overlay
    const flashConfig = flash ? VOLATILE_CONFIG[flash.type] : null;

    return (
      <div className="bs-stream" ref={ref}>
        {/* Background illustration */}
        <img className="bs-stream__bg" src={bgStream} alt="" draggable={false} />
        <div className="bs-stream__overlay" />

        {/* Top bar */}
        <div className="bs-stream__topbar">
          <span className="bs-stream__live-badge">LIVE</span>
          <span className="bs-stream__title">Laisa の配信部屋</span>
          <span className="bs-stream__viewers">👁 {viewersRef.current}</span>
          <span className="bs-stream__progress">{eventIndex + 1}/{totalEvents}</span>
        </div>

        {/* Scrolling chat column */}
        <div className="bs-stream__chat">
          {comments.map(c => (
            <div key={c.id} className="bs-stream__chat-msg">
              <span className="bs-stream__chat-name">
                {`viewer_${(c.id % 60 + 10).toString().padStart(2, '0')}`}
              </span>
              <span className="bs-stream__chat-text">{c.text}</span>
            </div>
          ))}
        </div>

        {/* Volatile event flash — shows result of previous choice */}
        {flash && flashConfig && (
          <div
            key={flash.key}
            className={`bs-stream__volatile bs-stream__volatile--${flashConfig.colorClass}`}
          >
            <span className="bs-stream__volatile-emoji">{flashConfig.emoji}</span>
            <span className="bs-stream__volatile-label">{flashConfig.label}</span>
            <span className="bs-stream__volatile-delta">
              {flash.delta > 0 ? '+' : ''}{flash.delta}
            </span>
          </div>
        )}
        {flash && !flashConfig && (
          <div key={flash.key} className="bs-stream__volatile bs-stream__volatile--normal">
            <span className="bs-stream__volatile-delta">
              {flash.delta > 0 ? '+' : ''}{flash.delta}
            </span>
          </div>
        )}

        {/* Featured event card */}
        <div className="bs-stream__card">
          <div className="bs-stream__card-tag">
            💬 Chat Event
          </div>
          <p className="bs-stream__card-text">
            {event.textEn}
          </p>

          {/* Timer bar */}
          <div className="bs-stream__timer-wrap">
            <div
              className="bs-stream__timer-bar"
              style={{ width: `${progress * 100}%`, background: timerColor }}
            />
            <span className="bs-stream__timer-hint" style={{ color: timerColor }}>
              {timedOut ? 'Timed out…' : speedHint}
            </span>
          </div>

          {/* Choice buttons */}
          <div className="bs-stream__choices">
            {event.choices.map((c, i) => (
              <button
                key={i}
                className="bs-stream__choice"
                onPointerDown={() => handleChoose(i)}
                disabled={timedOut}
              >
                {c.labelEn}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  })
);

StreamSession.displayName = 'StreamSession';
export default StreamSession;
