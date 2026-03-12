import React, { forwardRef } from 'react';
import type { EndingType } from '../types';
import { t, getText } from '../i18n';
import bgOnline  from '../img/bg_ending_online.png';
import bgOffline from '../img/bg_ending_offline.png';
import bgRestart from '../img/bg_ending_restart.png';
import bgBsodRoom from '../img/bg_ending_bsod.png';
import isayaHappy     from '../img/isaya_happy.png';
import isayaIdle      from '../img/isaya_idle.png';
import isayaFocused   from '../img/isaya_focused.png';
import isayaSad       from '../img/isaya_sad.png';
import isayaTired     from '../img/isaya_tired.png';
import isayaSurprised from '../img/isaya_surprised.png';
import NoiseCanvas from './NoiseCanvas';
import './EndingScreen.less';

interface Props {
  endingType: EndingType;
  followers: number;
  connection: number;
  onRestart: () => void;
}

const ENDING_BG: Record<EndingType, string> = {
  online:       bgOnline,
  offline:      bgOffline,
  restart:      bgRestart,
  bsod:         bgBsodRoom,
  burnout:      bgOnline,
  cult_hero:    bgRestart,
  hollow_viral: bgOffline,
};

const ENDING_ISAYA: Record<EndingType, string> = {
  online:       isayaHappy,
  offline:      isayaIdle,
  restart:      isayaFocused,
  bsod:         isayaSad,
  burnout:      isayaTired,
  cult_hero:    isayaSurprised,
  hollow_viral: isayaSad,
};

const EndingScreen = React.memo(
  forwardRef<HTMLDivElement, Props>(function EndingScreen(
    { endingType, followers, connection, onRestart }, ref
  ) {
    const bg = ENDING_BG[endingType];

    const isayaSrc = ENDING_ISAYA[endingType];

    // ── BSOD ending: Windows BSOD aesthetic over the chaos room ──────────────
    if (endingType === 'bsod') {
      return (
        <div className="bs-ending bs-ending--bsod" ref={ref}>
          <img className="bs-ending__bg" src={bg} alt="" draggable={false} />
          <NoiseCanvas opacity={0.18} />
          <div className="bs-ending__bsod-panel">
            <div className="bs-ending__bsod-face">:(</div>
            <p className="bs-ending__bsod-main">
              {getText(
                '你的直播遭遇了严重错误，需要重启。',
                'Your stream encountered a problem and needs to restart.'
              )}
            </p>
            <p className="bs-ending__bsod-code">0x0000ISAYA</p>
            <p className="bs-ending__bsod-code">SYSTEM_THREAD_EXCEPTION_NOT_HANDLED</p>
            <p className="bs-ending__bsod-collecting">
              {getText('正在收集错误信息', 'Collecting error info')}
              <span className="bs-ending__bsod-dots" />
            </p>
            <div className="bs-ending__bsod-stats">
              <span>{getText('粉丝', 'Followers')}: {followers.toLocaleString()}</span>
              <span>{getText('羁绊', 'Bond')}: {connection} / 10</span>
            </div>
            <button className="bs-ending__bsod-btn" onPointerDown={onRestart}>
              PLAY AGAIN
            </button>
          </div>
          <img className="bs-ending__isaya" src={isayaSrc} alt="" draggable={false} />
        </div>
      );
    }

    // ── Normal endings: room background + gradient + text ────────────────────
    return (
      <div className={`bs-ending bs-ending--${endingType}`} ref={ref}>
        <img className="bs-ending__bg" src={bg} alt="" draggable={false} />
        <NoiseCanvas opacity={0.18} />
        <div className="bs-ending__overlay" />
        <img className="bs-ending__isaya" src={isayaSrc} alt="" draggable={false} />

        <div className="bs-ending__content">
          <div className="bs-ending__tag">{getText('第 13 天 · 结局', 'Day 13 · Ending')}</div>
          <h2 className="bs-ending__title">{t(`ending.${endingType}.title`)}</h2>
          <p className="bs-ending__sub">{t(`ending.${endingType}.sub`)}</p>
          <p className="bs-ending__text">{t(`ending.${endingType}.text`)}</p>

          <div className="bs-ending__stats">
            <div className="bs-ending__stat">
              <span className="bs-ending__stat-num" style={{ color: 'var(--bs-followers)' }}>
                {followers.toLocaleString()}
              </span>
              <span className="bs-ending__stat-label">{getText('最终粉丝', 'final followers')}</span>
            </div>
            <div className="bs-ending__stat">
              <span className="bs-ending__stat-num" style={{ color: 'var(--bs-connection)' }}>
                {connection} / 10
              </span>
              <span className="bs-ending__stat-label">{getText('羁绊', 'bond')}</span>
            </div>
          </div>

          <button className="bs-ending__btn" onPointerDown={onRestart}>
            PLAY AGAIN
          </button>
        </div>
      </div>
    );
  })
);

EndingScreen.displayName = 'EndingScreen';
export default EndingScreen;
