import React, { forwardRef, useEffect, useState } from 'react';
import { useLocale } from '../i18n';
import type { GameAction } from '../types';
import iconEnergy from '../img/icon_energy.png';
import iconMood from '../img/icon_mood.png';
import iconFocus from '../img/icon_focus.png';
import iconFollowers from '../img/icon_followers.png';
import iconConnection from '../img/icon_connection.png';
import './ActionPanel.less';

interface Props {
  phase: string;
  actions: GameAction[];
  onChoose: (action: GameAction) => void;
}

const ActionPanel = React.memo(
  forwardRef<HTMLDivElement, Props>(function ActionPanel({ phase, actions, onChoose }, ref) {
    const { getText } = useLocale();
    const [expanded, setExpanded] = useState(false);

    useEffect(() => { setExpanded(false); }, [phase]);

    const streamAction = actions.find(a => a.isStream);
    const regularActions = actions.filter(a => !a.isStream);

    const handleGoLive = () => {
      if (streamAction) { setExpanded(false); onChoose(streamAction); }
    };

    const handleChoose = (action: GameAction) => {
      setExpanded(false);
      onChoose(action);
    };

    return (
      <div className="bs-actions" ref={ref}>
        <div className="bs-actions__btns">
          <button
            className={`bs-btn bs-btn--live ${!streamAction ? 'bs-btn--live-off' : ''}`}
            onPointerDown={streamAction ? handleGoLive : undefined}
            disabled={!streamAction}
          >
            <span className="bs-btn__dot" />
            GO LIVE
          </button>
          <button
            className={`bs-btn bs-btn--act ${expanded ? 'bs-btn--act-open' : ''}`}
            onPointerDown={() => setExpanded(e => !e)}
          >
            <span className="bs-btn__arrow">{expanded ? '▲' : '▼'}</span>
            {expanded ? 'CLOSE' : 'ACTIONS'}
          </button>
        </div>

        {expanded && (
          <div className="bs-actions__list">
            {regularActions.map(action => (
              <button key={action.id} className="bs-card" onPointerDown={() => handleChoose(action)}>
                <span className="bs-card__name">
                  {getText(action.labelZh, action.labelEn)}
                </span>
                <div className="bs-card__fx">
                  {renderFx(action.effect)}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    );
  })
);

function renderFx(effect: GameAction['effect']): React.ReactNode[] {
  const out: React.ReactNode[] = [];
  if (effect.energy)     out.push(<Chip key="e"  icon={iconEnergy}     v={effect.energy} />);
  if (effect.mood)       out.push(<Chip key="m"  icon={iconMood}       v={effect.mood} />);
  if (effect.focus)      out.push(<Chip key="f"  icon={iconFocus}      v={effect.focus} />);
  if (effect.followers)  out.push(<Chip key="fl" icon={iconFollowers}  v={effect.followers} />);
  if (effect.connection) out.push(<Chip key="c"  icon={iconConnection} v={effect.connection} />);
  return out;
}

function Chip({ icon, v }: { icon: string; v: number }) {
  const neg = v < 0;
  return (
    <span className={`bs-chip ${neg ? 'bs-chip--neg' : 'bs-chip--pos'}`}>
      <img className="bs-chip__icon" src={icon} alt="" draggable={false} />
      {v > 0 ? '+' : ''}{v}
    </span>
  );
}

ActionPanel.displayName = 'ActionPanel';
export default ActionPanel;
