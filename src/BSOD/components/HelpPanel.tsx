import React, { forwardRef } from 'react';
import iconEnergy    from '../img/icon_energy.png';
import iconMood      from '../img/icon_mood.png';
import iconFocus     from '../img/icon_focus.png';
import iconFollowers from '../img/icon_followers.png';
import { useLocale } from '../i18n';
import './HelpPanel.less';

interface Props {
  onClose: () => void;
}

const HelpPanel = React.memo(
  forwardRef<HTMLDivElement, Props>(function HelpPanel({ onClose }, ref) {
    const { getText } = useLocale();

    return (
      <div className="bs-help" ref={ref} onPointerDown={e => e.stopPropagation()}>
        {/* Backdrop */}
        <div className="bs-help__backdrop" onPointerDown={onClose} />

        {/* Panel */}
        <div className="bs-help__panel">
          <div className="bs-help__header">
            <span className="bs-help__title">HOW TO PLAY</span>
            <button className="bs-help__close" onPointerDown={onClose}>✕</button>
          </div>

          {/* Stats */}
          <div className="bs-help__section-label">
            {getText('状态指标', 'STATUS')}
          </div>
          <div className="bs-help__stats">
            <HelpStat
              icon={iconEnergy} color="var(--bs-energy)"
              name={getText('体力', 'Energy')}
              desc={getText('归零则游戏结束', 'Hits zero = game over')}
            />
            <HelpStat
              icon={iconMood} color="var(--bs-mood)"
              name={getText('心情', 'Mood')}
              desc={getText('影响直播质量与粉丝留存', 'Affects stream quality & retention')}
            />
            <HelpStat
              icon={iconFocus} color="var(--bs-focus)"
              name={getText('专注', 'Focus')}
              desc={getText('越高涨粉越快，归零则停滞', 'Higher = faster growth; zero = stagnation')}
            />
            <HelpStat
              icon={iconFollowers} color="var(--bs-followers)"
              name={getText('粉丝', 'Followers')}
              desc={getText('坚持 13 天直播即为胜利', 'Survive 13 days streaming = win')}
            />
          </div>

          {/* Timeline */}
          <div className="bs-help__section-label">
            {getText('每日时间轴', 'DAILY TIMELINE')}
          </div>
          <div className="bs-help__timeline-desc">
            <TimeSegment label="AM"   color="#7aaa60" desc={getText('上午 — 精力充沛，适合备课或休息', 'Morning — peak energy, good for prep or rest')} />
            <TimeSegment label="PM"   color="#7aaa60" desc={getText('下午 — 正常行动时段，处理日常事务', 'Afternoon — normal action window for daily tasks')} />
            <TimeSegment label="EVE"  color="#ef4444" desc={getText('傍晚 — 直播时段。必须在此开播，否则错过当日收益', 'Evening — LIVE window. Must stream here or miss the day\'s growth')} />
            <TimeSegment label="NIGHT" color="#7aaa60" desc={getText('深夜 — 一天结束，补充体力准备明天', 'Night — day wraps up, recover and prepare for tomorrow')} />
          </div>

          <p className="bs-help__tip">
            {getText(
              '💡 三项数值任意归零，或13天结束时粉丝为零，直播生涯结束。',
              '💡 Any stat hitting zero — or zero followers at day 13 — ends your run.'
            )}
          </p>
        </div>
      </div>
    );
  })
);

function HelpStat({ icon, color, name, desc }: {
  icon: string; color: string; name: string; desc: string;
}) {
  return (
    <div className="bs-help__stat">
      <img className="bs-help__stat-icon" src={icon} alt="" draggable={false}
           style={{ filter: `drop-shadow(0 0 4px ${color})` }} />
      <div className="bs-help__stat-text">
        <span className="bs-help__stat-name" style={{ color }}>{name}</span>
        <span className="bs-help__stat-desc">{desc}</span>
      </div>
    </div>
  );
}

function TimeSegment({ label, color, desc }: { label: string; color: string; desc: string }) {
  const isLive = label === 'EVE';
  return (
    <div className="bs-help__seg">
      <span className="bs-help__seg-label" style={{ color: isLive ? '#ef4444' : color }}>
        {label}{isLive && <span className="bs-help__seg-live"> LIVE</span>}
      </span>
      <span className="bs-help__seg-desc">{desc}</span>
    </div>
  );
}

HelpPanel.displayName = 'HelpPanel';
export default HelpPanel;
