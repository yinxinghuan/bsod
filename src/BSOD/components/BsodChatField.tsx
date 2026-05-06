import { useEffect, useLayoutEffect, useMemo, useRef } from 'react';
import { useLocale } from '../i18n';
import './BsodChatField.less';

type Tone = 'normal' | 'viral' | 'donate' | 'salty';

interface ChatMsg { user: string; text: string; tone?: Tone }

const CHAT_EN: ChatMsg[] = [
  { user: 'sleeplessfan',  text: 'first :))' },
  { user: 'midnight_cat',  text: 'go isaya' },
  { user: 'simp_master',   text: 'noticed me' },
  { user: 'mid_man',       text: 'this is mid',          tone: 'salty' },
  { user: 'gigachad',      text: 'peak content',         tone: 'viral' },
  { user: 'random_anon',   text: 'where energy?' },
  { user: 'late_owl',      text: 'still up isaya?' },
  { user: 'crash_andy',    text: 'PogChamp' },
  { user: 'foundering',    text: 'L stream',             tone: 'salty' },
  { user: 'cat_lover',     text: 'cat ily' },
  { user: 'isaya_fan',     text: 'drink water!!' },
  { user: 'lurker_42',     text: 'viral incoming',       tone: 'viral' },
  { user: 'no_thoughts',   text: 'KEKW' },
  { user: 'big_w',         text: 'W stream',             tone: 'viral' },
  { user: 'careful',       text: 'eyes look tired' },
  { user: 'just_passing',  text: 'mid' },
  { user: 'sleeping',      text: 'gn isaya' },
  { user: 'super_chat_42', text: '$5 — keep going!',     tone: 'donate' },
  { user: 'numbers_man',   text: '1000 viewers!!',       tone: 'viral' },
  { user: 'wholesome',     text: 'thanks for streaming' },
  { user: 'real_one',      text: 'rest soon ok?' },
  { user: 'pop_off',       text: 'POGGERS' },
  { user: 'unfunny',       text: 'mid stream',           tone: 'salty' },
  { user: 'actual_friend', text: 'streaming again??' },
  { user: 'ghost_viewer',  text: 'lurking' },
  { user: 'donator_x',     text: '$10 stay strong',      tone: 'donate' },
  { user: 'chat_bot',      text: 'energy: low' },
  { user: 'chat_bot',      text: 'mood: dipping' },
  { user: 'chat_bot',      text: 'focus: ???' },
  { user: 'isayan',        text: 'goated' },
  { user: 'wholesome_2',   text: 'i look forward to this' },
  { user: 'salty_andy',    text: 'where the games' },
  { user: 'viewer_88',     text: '8888' },
  { user: 'time_keeper',   text: '3am again??' },
  { user: 'watching',      text: 'just watching' },
  { user: 'soft_one',      text: 'be kind to yourself' },
  { user: 'deep_lurker',   text: 'super chat: thank you', tone: 'donate' },
  { user: 'numbers_man',   text: 'we hit 5k!',            tone: 'viral' },
  { user: 'cynic',         text: 'parasocial much',       tone: 'salty' },
  { user: 'genuine',       text: 'no really thank you' },
];

const CHAT_ZH: ChatMsg[] = [
  { user: '梦游患者',   text: '第一' },
  { user: '不眠夜',     text: 'isaya 加油' },
  { user: '隔壁老王',   text: '主播看起来累了' },
  { user: '卷王',       text: '卷死了',         tone: 'salty' },
  { user: '观察员',     text: '6666' },
  { user: '路人甲',     text: '感觉这太mid',     tone: 'salty' },
  { user: '糖果',       text: '主播喝水！' },
  { user: '夜班护士',   text: '辛苦了今天' },
  { user: '永远的神',   text: '永远的神',       tone: 'viral' },
  { user: '路过',       text: '又是凌晨三点' },
  { user: '黑猫粉',     text: '猫呢' },
  { user: '热心听众',   text: '看着想哭' },
  { user: '土豪',       text: '送您一个嘉年华',   tone: 'donate' },
  { user: '彩虹屁',     text: '牛' },
  { user: '弹幕机器',   text: '体力：低' },
  { user: '弹幕机器',   text: '心情：下滑' },
  { user: '弹幕机器',   text: '专注：???' },
  { user: '吃瓜',       text: '哈哈哈' },
  { user: '尾灯',       text: 'isaya 早点休息' },
  { user: '酸柠檬',     text: '直播又水了',     tone: 'salty' },
  { user: '陪伴',       text: '一直都在' },
  { user: '观察员',     text: '破千啦！',       tone: 'viral' },
  { user: '深夜食堂',   text: '记得吃饭' },
  { user: '老粉',       text: '一直在看' },
  { user: '无名氏',     text: '感谢主播' },
  { user: '小心心',     text: '抱抱主播' },
  { user: '糖纸',       text: '送花花' },
  { user: '路人乙',     text: 'mid' },
  { user: '观察员',     text: '在线人数破万了',  tone: 'viral' },
  { user: '冷面',       text: '陪我撑过最难的一段' },
  { user: '土豪',       text: '我充50请加油',    tone: 'donate' },
  { user: '路过',       text: '梦回大学时光' },
  { user: '夜班',       text: '加油 你不是一个人' },
  { user: '尾灯',       text: '注意身体' },
  { user: '梦中人',     text: '直播是我每天的盼头' },
  { user: '挑剔',       text: '今天有点没劲',     tone: 'salty' },
  { user: '冰淇淋',     text: '笑死' },
  { user: '小米',       text: '弹幕在涨' },
  { user: '热心',       text: '关心主播' },
  { user: '常驻',       text: 'isaya 永远滴神' },
];

interface FieldChat {
  msg: ChatMsg;
  laneX: number;
  x: number; y: number;
  vx: number; vy: number;
  baseVy: number;
  el: HTMLDivElement;
}

function mulberry32(a: number) {
  return () => {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export default function BsodChatField() {
  const { locale } = useLocale();
  const fieldRef = useRef<HTMLDivElement>(null);
  const elsRef = useRef<(HTMLDivElement | null)[]>([]);
  const wordsRef = useRef<FieldChat[]>([]);

  const initial = useMemo(() => {
    const pool = locale === 'zh' ? CHAT_ZH : CHAT_EN;
    const rng = mulberry32(11);
    const list: ChatMsg[] = [];
    const N = 70;
    for (let i = 0; i < N; i++) list.push(pool[Math.floor(rng() * pool.length)]);
    return list;
  }, [locale]);

  useLayoutEffect(() => {
    const field = fieldRef.current;
    if (!field) return;
    const fr = field.getBoundingClientRect();
    const lanes = new Map<number, number>();
    const lrng = mulberry32(31);

    const rawHomes = elsRef.current.map(el => {
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return { hx: r.left + r.width / 2 - fr.left, hy: r.top + r.height / 2 - fr.top };
    });

    // Stretch Y across full height so short flow doesn't pile at top.
    const ys = rawHomes.filter(h => h !== null).map(h => h!.hy);
    const minY = Math.min.apply(null, ys);
    const maxY = Math.max.apply(null, ys);
    const yRange = Math.max(maxY - minY, 1);
    const padTop = 16, padBottom = 16;
    const targetTop = padTop, targetBottom = fr.height - padBottom;

    const words: FieldChat[] = [];
    elsRef.current.forEach((el, i) => {
      if (!el) return;
      const raw = rawHomes[i];
      if (!raw) return;
      const hx = raw.hx;
      const hy = targetTop + ((raw.hy - minY) / yRange) * (targetBottom - targetTop);
      const colKey = Math.round(hx / 80);
      let baseVy = lanes.get(colKey);
      if (baseVy === undefined) {
        // Slower than agent-string-v2: ~25–55 px/sec — chat scroll feel
        const speed = 0.4 + lrng() * 0.55;
        baseVy = -speed;
        lanes.set(colKey, baseVy);
      }
      words.push({
        msg: initial[i], laneX: hx, x: hx, y: hy,
        vx: 0, vy: baseVy, baseVy, el,
      });
      el.style.position = 'absolute';
      el.style.left = '0';
      el.style.top = '0';
      el.style.transform = `translate3d(${hx.toFixed(2)}px,${hy.toFixed(2)}px,0) translate(-50%,-50%)`;
    });
    wordsRef.current = words;
  }, [initial]);

  useEffect(() => {
    let raf = 0;
    let last = performance.now();
    const SPRING_X = 0.04, X_DAMP = 0.88, Y_EASE = 0.06;
    const WAVE_AMP_X = 0.05, WRAP_PAD = 60;

    const tick = (now: number) => {
      const dtSec = Math.min((now - last) / 1000, 0.05);
      last = now;
      const dt = Math.min(dtSec * 60, 3);

      const field = fieldRef.current;
      if (!field) { raf = requestAnimationFrame(tick); return; }
      const fr = field.getBoundingClientRect();
      const fieldH = fr.height;

      const words = wordsRef.current;
      for (let i = 0; i < words.length; i++) {
        const w = words[i];
        w.vx += Math.sin(now * 0.0003 + w.laneX * 0.07) * WAVE_AMP_X;
        w.vy += (w.baseVy - w.vy) * Y_EASE;
        w.vx += (w.laneX - w.x) * SPRING_X;
        w.vx *= X_DAMP;
        w.x += w.vx * dt;
        w.y += w.vy * dt;
        if (w.y < -WRAP_PAD)              w.y += fieldH + 2 * WRAP_PAD;
        else if (w.y > fieldH + WRAP_PAD) w.y -= fieldH + 2 * WRAP_PAD;
        w.el.style.transform = `translate3d(${w.x.toFixed(2)}px,${w.y.toFixed(2)}px,0) translate(-50%,-50%)`;
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, []);

  return (
    <div className="bs-chat-field" ref={fieldRef} aria-hidden>
      {initial.map((m, i) => (
        <div
          key={i}
          ref={el => { elsRef.current[i] = el; }}
          className={`bs-chat-msg bs-chat-msg--${m.tone ?? 'normal'}`}
        >
          <span className="bs-chat-msg__user">@{m.user}</span>
          <span className="bs-chat-msg__text">{m.text}</span>
        </div>
      ))}
    </div>
  );
}
