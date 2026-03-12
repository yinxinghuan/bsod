import React, { forwardRef, useEffect, useRef, useState } from 'react';
import type { StreamEvent, ResponseSpeed, VolatileType } from '../types';
import { getText } from '../i18n';
import bgStream from '../img/bg_stream.png';
import './StreamSession.less';


interface Props {
  event: StreamEvent;
  eventIndex: number;
  totalEvents: number;
  onChoose: (index: number, speed: ResponseSpeed) => void;
  lastFollowerEvent?: { delta: number; type: VolatileType; key: number } | null;
  pendingEnd?: boolean;
  onStreamEnd?: () => void;
}

// ── Chat comment pool ──────────────────────────────────────────────────────────
const COMMENT_POOL = [
  // 中文
  '加油！', '牛！', '好耶', '冲！', '哈哈哈', '来了来了', '太强了', '芜湖',
  '主播主播', '爱看', '草', '牛牛', '开冲', '真的假的', '哇哦', '主播好棒',
  '哈哈哈哈', '666', '666666', '！！！', '啊啊啊啊', '我在我在', '厉害了',
  // 英文
  'aaaa', 'poggers', 'LUL', 'pog', 'gg', 'OMG', 'KEKW', 'monkaS',
  'POG', 'Pog', 'Sadge', 'xd', 'XD', 'LMAO', 'NotLikeThis', 'hype',
  'lets gooo', 'W', 'w', 'sheesh', 'no way', 'actual god', 'clip it',
  'EZ', 'OMEGALUL', 'lol', 'based', 'certified moment',
  // 日文
  'わあ！', 'すごい！', 'かわいい', 'やばい', 'がんばれ！', 'うまい！',
  'ｗｗｗ', 'えー！', 'なるほど', 'マジか', '草', 'いいね！', 'ドンマイ',
  // 韩文
  '대박', '진짜요?', 'ㅋㅋㅋ', '헐', '잘한다！', '귀엽다', 'ㅠㅠ',
  '오오오', '와', '레전드', '존잘', 'ㅋㅋㅋㅋ',
];

const TIMER_TOTAL = 8000; // ms
const FAST_THRESHOLD  = 3000;
const SLOW_THRESHOLD  = 6000;

// ── Volatile event display config ─────────────────────────────────────────────
const VOLATILE_CONFIG: Record<VolatileType, {
  label: string; kaomoji: string; colorClass: string;
  descZh: string; descEn: string;
} | null> = {
  viral:       { label: 'VIRAL',       kaomoji: '(*≧▽≦)', colorClass: 'viral',
                 descZh: '直播爆了！粉丝暴涨', descEn: 'Gone viral! Massive surge' },
  boost:       { label: 'BOOST',       kaomoji: '(＾▽＾)',  colorClass: 'boost',
                 descZh: '热度上升！粉丝增加', descEn: 'Trending up! Followers boosted' },
  controversy: { label: 'CONTROVERSY', kaomoji: '(╯°□°）╯', colorClass: 'controversy',
                 descZh: '引发争议！粉丝大量流失', descEn: 'Went controversial! Followers leaving' },
  flop:        { label: 'FLOP',        kaomoji: '(´・ω・`)', colorClass: 'flop',
                 descZh: '反应平平，效果打折', descEn: 'Fell flat. Reduced gain' },
  normal:      null,
};

const StreamSession = React.memo(
  forwardRef<HTMLDivElement, Props>(function StreamSession(
    { event, eventIndex, totalEvents, onChoose, lastFollowerEvent, pendingEnd, onStreamEnd }, ref
  ) {
    const [comments, setComments] = useState<{ id: number; text: string }[]>([]);
    const [elapsed, setElapsed] = useState(0);
    const [timedOut, setTimedOut] = useState(false);
    const [flash, setFlash] = useState<{ delta: number; type: VolatileType; key: number } | null>(null);
    const [resultText, setResultText] = useState<string | null>(null);
    const [cardMinH, setCardMinH] = useState<number | undefined>(undefined);
    const startRef = useRef(Date.now());
    const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
    const commentIdRef = useRef(0);
    const viewersRef = useRef(Math.floor(Math.random() * 120 + 60));
    const chosenRef = useRef(false);
    const flashTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const resultTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const lastResultRef = useRef<string | null>(null);
    const cardRef = useRef<HTMLDivElement | null>(null);

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
      setResultText(null);
      setCardMinH(undefined);
      if (resultTimerRef.current) clearTimeout(resultTimerRef.current);
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

      return () => {
        if (timerRef.current) clearInterval(timerRef.current);
        if (resultTimerRef.current) clearTimeout(resultTimerRef.current);
      };
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
      if (cardRef.current) setCardMinH(cardRef.current.offsetHeight);
      if (timerRef.current) clearInterval(timerRef.current);
      const e = Date.now() - startRef.current;
      const speed: ResponseSpeed = e < FAST_THRESHOLD ? 'fast' : e < SLOW_THRESHOLD ? 'normal' : 'slow';
      const c = event.choices[index];
      const rText = getText(c.resultZh ?? '', c.resultEn ?? '');
      if (rText) {
        setResultText(rText);
        lastResultRef.current = rText;
        resultTimerRef.current = setTimeout(() => {
          setResultText(null);
          onChoose(index, speed);
        }, 2000);
      } else {
        onChoose(index, speed);
      }
    };

    const remaining = Math.max(0, TIMER_TOTAL - elapsed);
    const progress = remaining / TIMER_TOTAL; // 1 → 0
    const timerColor = progress > 0.625 ? '#4ade80' : progress > 0.25 ? '#fbbf24' : '#f87171';
    const speedHint = elapsed < FAST_THRESHOLD
      ? getText('快速回应 ×1.5 粉丝', 'Fast reply ×1.5 followers')
      : elapsed < SLOW_THRESHOLD
        ? getText('回应中…', 'Responding…')
        : getText('观众在流失…', 'Chat is going cold…');

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
          <span className="bs-stream__title">Isaya の配信部屋</span>
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
            <div className="bs-stream__volatile-backdrop" />
            <span className="bs-stream__volatile-kaomoji">{flashConfig.kaomoji}</span>
            <span className="bs-stream__volatile-label">{flashConfig.label}</span>
            <span className="bs-stream__volatile-delta">
              {flash.delta > 0 ? '+' : ''}{flash.delta}
            </span>
            <span className="bs-stream__volatile-desc">
              {getText(flashConfig.descZh, flashConfig.descEn)}
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
        <div
          ref={cardRef}
          className={`bs-stream__card${event.tag ? ' bs-stream__card--special' : ''}`}
          style={cardMinH ? { minHeight: cardMinH } : undefined}
        >
          {event.tag ? (
            <div className="bs-stream__card-tag bs-stream__card-tag--special"
                 style={{ color: event.tag.color, borderColor: event.tag.color }}>
              {getText(event.tag.zh, event.tag.en)}
            </div>
          ) : (
            <div className="bs-stream__card-tag">
              💬 {getText('弹幕事件', 'Chat Event')}
            </div>
          )}
          <p className="bs-stream__card-text">
            {resultText ?? (pendingEnd ? lastResultRef.current : null) ?? getText(event.textZh, event.textEn)}
          </p>

          {/* Timer bar */}
          {!resultText && !pendingEnd && (
            <div className="bs-stream__timer-wrap">
              <div
                className="bs-stream__timer-bar"
                style={{ width: `${progress * 100}%`, background: timerColor }}
              />
              <span className="bs-stream__timer-hint" style={{ color: timerColor }}>
                {timedOut ? getText('超时…', 'Timed out…') : speedHint}
              </span>
            </div>
          )}

          {resultText ? (
            <div className="bs-stream__result-hint">
              {getText('观众正在反应…', 'Chat is reacting…')}
            </div>
          ) : pendingEnd ? (
            <button className="bs-stream__end-btn" onPointerDown={onStreamEnd}>
              {getText('结束直播', 'End Stream')}
            </button>
          ) : (
            <div className="bs-stream__choices">
              {event.choices.map((c, i) => (
                <button
                  key={i}
                  className="bs-stream__choice"
                  onPointerDown={() => handleChoose(i)}
                  disabled={timedOut}
                >
                  {getText(c.labelZh, c.labelEn)}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  })
);

StreamSession.displayName = 'StreamSession';
export default StreamSession;
