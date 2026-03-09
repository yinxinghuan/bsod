import React, { forwardRef, useEffect, useState } from 'react';
import type { GameAction, SvFootage, VolatileType } from '../types';
import { useLocale } from '../i18n';

// ── Surveillance footage imports ───────────────────────────────────────────────
import svRest   from '../img/sv_rest.png';
import svEat    from '../img/sv_eat.png';
import svPhone  from '../img/sv_phone.png';
import svDesk   from '../img/sv_desk.png';
import svWalk   from '../img/sv_walk.png';
import svSetup  from '../img/sv_setup.png';
import svRelax  from '../img/sv_relax.png';
import svVideo  from '../img/sv_video.png';
import svGame   from '../img/sv_game.png';

// ── Stat icon imports ──────────────────────────────────────────────────────────
import iconEnergy     from '../img/icon_energy.png';
import iconMood       from '../img/icon_mood.png';
import iconFocus      from '../img/icon_focus.png';
import iconFollowers  from '../img/icon_followers.png';
import iconConnection from '../img/icon_connection.png';

import './ActionResultScreen.less';

const SV_FOOTAGE: Record<SvFootage, string> = {
  rest:  svRest,
  eat:   svEat,
  phone: svPhone,
  desk:  svDesk,
  walk:  svWalk,
  setup: svSetup,
  relax: svRelax,
  video: svVideo,
  game:  svGame,
};

interface Props {
  action: GameAction;
  onDismiss: () => void;
}

const ActionResultScreen = React.memo(
  forwardRef<HTMLDivElement, Props>(function ActionResultScreen({ action, onDismiss }, ref) {
    const { getText } = useLocale();
    const [visible, setVisible] = useState(false);
    const [tappable, setTappable] = useState(false);

    useEffect(() => {
      const t1 = setTimeout(() => setVisible(true), 30);
      const t2 = setTimeout(() => setTappable(true), 700);
      return () => { clearTimeout(t1); clearTimeout(t2); };
    }, []);

    const footageSrc = SV_FOOTAGE[action.svFootage ?? 'desk'];

    return (
      <div
        ref={ref}
        className={`ar ${visible ? 'ar--in' : ''}`}
        onPointerDown={tappable ? onDismiss : undefined}
      >
        <SurveillanceView action={action} footageSrc={footageSrc} getText={getText} />
        <div className="ar__tap-hint">
          {getText('点击继续', 'Tap to continue')}
        </div>
      </div>
    );
  })
);

// ── Surveillance View ──────────────────────────────────────────────────────────

function SurveillanceView({
  action,
  footageSrc,
  getText,
}: {
  action: GameAction;
  footageSrc: string;
  getText: (zh: string, en: string) => string;
}) {
  const now = new Date();
  const ts =
    [now.getFullYear(), String(now.getMonth() + 1).padStart(2, '0'), String(now.getDate()).padStart(2, '0')].join('-') +
    ' ' +
    [String(now.getHours()).padStart(2, '0'), String(now.getMinutes()).padStart(2, '0'), String(now.getSeconds()).padStart(2, '0')].join(':');

  return (
    <div className="ar__sv">
      {/* ── CRT monitor frame ── */}
      <div className="ar__crt">
        <img className="ar__crt-img" src={footageSrc} alt="" draggable={false} />
        <div className="ar__crt-vignette" />
        <div className="ar__crt-scanlines" />
        <div className="ar__crt-noise" />
        <div className="ar__crt-hud">
          <span className="ar__crt-cam">CAM 01 · ROOM F1</span>
          <span className="ar__crt-rec">● REC</span>
        </div>
        <div className="ar__crt-ts">{ts}</div>
      </div>

      {/* ── Info panel below CRT ── */}
      <div className="ar__info">
        <h2 className="ar__title">{getText(action.labelZh, action.labelEn)}</h2>
        <p className="ar__desc">{getText(action.descZh, action.descEn)}</p>
        <EffectReadout action={action} getText={getText!} />
      </div>
    </div>
  );
}

// ── Volatile event config ──────────────────────────────────────────────────────

const VOLATILE_BANNER: Record<string, { kaomoji: string; label: string; colorClass: string; descZh: string; descEn: string }> = {
  viral:       { kaomoji: '(*≧▽≦)', label: 'VIRAL',       colorClass: 'viral',
                 descZh: '粉丝暴涨！远超预期',          descEn: 'Followers surged! Way beyond expected' },
  boost:       { kaomoji: '(＾▽＾)',  label: 'BOOST',       colorClass: 'boost',
                 descZh: '热度上升，粉丝增加',          descEn: 'Trending up, extra followers gained' },
  controversy: { kaomoji: '(╯°□°）╯', label: 'CONTROVERSY', colorClass: 'controversy',
                 descZh: '引发争议！粉丝大量流失',      descEn: 'Controversy erupted! Followers dropped hard' },
  flop:        { kaomoji: '(´・ω・`)', label: 'FLOP',        colorClass: 'flop',
                 descZh: '反应平平，效果大打折扣',      descEn: 'Fell flat. Much less than expected' },
};

// ── Effect readout ─────────────────────────────────────────────────────────────

const STAT_ICONS: Record<string, string> = {
  energy:     iconEnergy,
  mood:       iconMood,
  focus:      iconFocus,
  followers:  iconFollowers,
  connection: iconConnection,
};

function EffectReadout({ action, getText }: { action: GameAction; getText: (zh: string, en: string) => string }) {
  const { effect } = action;
  const banner = action.volatileType && action.volatileType !== 'normal'
    ? VOLATILE_BANNER[action.volatileType as string]
    : null;
  const rows: { key: string; val: number; color: string }[] = [];
  if (effect.energy)     rows.push({ key: 'energy',     val: effect.energy,     color: 'var(--bs-energy)' });
  if (effect.mood)       rows.push({ key: 'mood',       val: effect.mood,       color: 'var(--bs-mood)' });
  if (effect.focus)      rows.push({ key: 'focus',      val: effect.focus,      color: 'var(--bs-focus)' });
  if (effect.followers)  rows.push({ key: 'followers',  val: effect.followers,  color: 'var(--bs-followers)' });
  if (effect.connection) rows.push({ key: 'connection', val: effect.connection, color: 'var(--bs-connection)' });
  if (!rows.length && !banner) return null;

  return (
    <>
    {banner && (
      <div className={`ar__volatile ar__volatile--${banner.colorClass}`}>
        <span className="ar__volatile-kaomoji">{banner.kaomoji}</span>
        <div className="ar__volatile-body">
          <span className="ar__volatile-label">{banner.label}</span>
          <span className="ar__volatile-desc">{getText(banner.descZh, banner.descEn)}</span>
        </div>
      </div>
    )}
    {rows.length > 0 && (
    <div className="ar__effects">
      {rows.map(r => (
        <div
          key={r.key}
          className="ar__effect"
          style={{ color: r.val < 0 ? 'var(--bs-danger)' : r.color }}
        >
          <img
            className="ar__effect-icon"
            src={STAT_ICONS[r.key]}
            alt={r.key}
            draggable={false}
          />
          <span className="ar__effect-val">
            {r.val > 0 ? '+' : ''}{r.val}
          </span>
        </div>
      ))}
    </div>
    )}
    </>
  );
}

// Fix unused type import warning
export type { VolatileType };

ActionResultScreen.displayName = 'ActionResultScreen';
export default ActionResultScreen;
