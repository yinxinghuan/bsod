import React, { forwardRef } from 'react';
import type { DeathCause } from '../types';
import { t, getText } from '../i18n';
import bgDark from '../img/bg_ending_bsod.png';
import iconEnergy from '../img/icon_energy.png';
import iconMood from '../img/icon_mood.png';
import iconFocus from '../img/icon_focus.png';
import iconFollowers from '../img/icon_followers.png';
import NoiseCanvas from './NoiseCanvas';
import './DeathScreen.less';

interface Props {
  cause: DeathCause;
  statValue: number;
  followers: number;
  onRestart: () => void;
}

const CAUSE_ICON: Record<string, string> = {
  energy:    'z(>_<)z',
  mood:      '(T_T)',
  followers: '(X_X)',
  focus:     '(@_@)',
};

const CAUSE_STAT_ICON: Record<string, string> = {
  energy: iconEnergy, mood: iconMood, followers: iconFollowers, focus: iconFocus,
};

const CAUSE_STAT_LABEL: Record<string, [string, string]> = {
  energy:    ['精力', 'Energy'],
  mood:      ['心情', 'Mood'],
  followers: ['粉丝', 'Followers'],
  focus:     ['专注', 'Focus'],
};

const DeathScreen = React.memo(
  forwardRef<HTMLDivElement, Props>(function DeathScreen({ cause, statValue, followers, onRestart }, ref) {
    const [zh, en] = CAUSE_STAT_LABEL[cause];
    return (
      <div className={`bs-death bs-death--${cause}`} ref={ref}>
        <img className="bs-death__bg" src={bgDark} alt="" draggable={false} />
        <NoiseCanvas opacity={0.22} />
        <div className="bs-death__overlay" />

        <div className="bs-death__inner">
          <div className="bs-death__icon" data-text={CAUSE_ICON[cause]}>{CAUSE_ICON[cause]}</div>

          <div className="bs-death__stat-cause">
            <img className="bs-death__stat-icon" src={CAUSE_STAT_ICON[cause]} alt="" draggable={false} />
            <span className="bs-death__stat-name">{getText(zh, en)}</span>
            <span className="bs-death__stat-val">{statValue}</span>
          </div>

          <h2 className="bs-death__title">{t(`deathTitle_${cause}`)}</h2>
          <p className="bs-death__desc">{t(`deathDesc_${cause}`)}</p>
          <p className="bs-death__followers">
            {getText('最终粉丝', 'Final followers')}{' '}<strong>{followers.toLocaleString()}</strong>
          </p>
          <button className="bs-death__btn" onPointerDown={onRestart}>
            PLAY AGAIN
          </button>
        </div>
      </div>
    );
  })
);

DeathScreen.displayName = 'DeathScreen';
export default DeathScreen;
