import React, { forwardRef } from 'react';
import { useLocale } from '../i18n';
import type { DeathCause } from '../types';
import bgDark from '../img/bg_ending_bsod.png';
import './DeathScreen.less';

interface Props {
  cause: DeathCause;
  followers: number;
  onRestart: () => void;
}

const CAUSE_ICON: Record<string, string> = {
  energy:    '💤',
  mood:      '🌑',
  followers: '📉',
  focus:     '🔲',
};

const DeathScreen = React.memo(
  forwardRef<HTMLDivElement, Props>(function DeathScreen({ cause, followers, onRestart }, ref) {
    const { t, getText } = useLocale();

    return (
      <div className={`bs-death bs-death--${cause}`} ref={ref}>
        <img className="bs-death__bg" src={bgDark} alt="" draggable={false} />
        <div className="bs-death__overlay" />

        <div className="bs-death__inner">
          <div className="bs-death__icon">{CAUSE_ICON[cause]}</div>
          <h2 className="bs-death__title">{t(`deathTitle_${cause}`)}</h2>
          <p className="bs-death__desc">{t(`deathDesc_${cause}`)}</p>
          <p className="bs-death__followers">
            {getText('最终粉丝', 'Final followers')}
            {' '}<strong>{followers.toLocaleString()}</strong>
          </p>
          <button className="bs-death__btn" onPointerDown={onRestart}>
            {t('replayBtn')}
          </button>
        </div>
      </div>
    );
  })
);

DeathScreen.displayName = 'DeathScreen';
export default DeathScreen;
