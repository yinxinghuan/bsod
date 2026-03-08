import React, { forwardRef } from 'react';
import { useLocale } from '../i18n';
import type { GameState } from '../types';
import iconEnergy from '../img/icon_energy.png';
import iconMood from '../img/icon_mood.png';
import iconFocus from '../img/icon_focus.png';
import iconFollowers from '../img/icon_followers.png';
import './DayEndScreen.less';

interface Props {
  state: GameState;
  onContinue: () => void;
}

const DAY_LINES_ZH: Record<number, string> = {
  1: '第一天，你把镜头对准了自己。',
  2: '夜里，直播间的灯还亮着。',
  3: '手机屏幕亮了又暗，暗了又亮。',
  4: '猫在键盘上睡着了，你把它挪开，继续打字。',
  5: '弹幕刷过去，每一条都是真实的人。',
  6: '你发现房间有点乱，随手收拾了一下。',
  7: '七天了。你还在。',
  8: '直播间有个常驻观众，你开始记得他们的名字。',
  9: '今天笑了好几次。没想到。',
  10: '有人说，你的声音让他们不孤单。',
  11: '妈妈打来电话，问你吃饭了没。',
  12: '快了。还有最后一天。',
  13: '最后一天。',
};
const DAY_LINES_EN: Record<number, string> = {
  1: 'Day one. You pointed the camera at yourself.',
  2: 'The stream light was still on when you went to sleep.',
  3: 'Phone screen on, off, on again.',
  4: 'The cat slept on the keyboard. You moved it, kept typing.',
  5: 'Chat flew by. Every message was a real person.',
  6: 'You noticed the room was a mess. You tidied up a little.',
  7: 'Seven days. You\'re still here.',
  8: 'A regular viewer. You\'re starting to remember their name.',
  9: 'You laughed a few times today. Unexpected.',
  10: 'Someone said your voice makes them feel less alone.',
  11: 'Mom called. Asked if you\'d eaten.',
  12: 'Almost there. One more day.',
  13: 'Last day.',
};

const DayEndScreen = React.memo(
  forwardRef<HTMLDivElement, Props>(function DayEndScreen({ state, onContinue }, ref) {
    const { getText } = useLocale();
    const { day, energy, mood, focus, followers, dayLogStart, streamedToday } = state;

    const deltas = {
      energy: Math.round(energy - dayLogStart.energy),
      mood: Math.round(mood - dayLogStart.mood),
      focus: Math.round(focus - dayLogStart.focus),
      followers: followers - dayLogStart.followers,
    };

    const line = getText(DAY_LINES_ZH[day] ?? '', DAY_LINES_EN[day] ?? '');

    return (
      <div className="bs-dayend" ref={ref}>
        <div className="bs-dayend__inner">
          <div className="bs-dayend__header">
            <span className="bs-dayend__label">DAY {day} / 13</span>
            <span className="bs-dayend__tag">{getText('结束', 'END')}</span>
          </div>

          <p className="bs-dayend__line">{line}</p>

          {streamedToday && (
            <p className="bs-dayend__streamed">{getText('今天开播了。', 'You streamed today.')}</p>
          )}

          <div className="bs-dayend__deltas">
            <StatDelta icon={iconEnergy} val={deltas.energy} color="var(--bs-energy)" />
            <StatDelta icon={iconMood}   val={deltas.mood}   color="var(--bs-mood)" />
            <StatDelta icon={iconFocus}  val={deltas.focus}  color="var(--bs-focus)" />
          </div>
          <div className="bs-dayend__followers">
            <img className="bs-dayend__flw-icon" src={iconFollowers} alt="" draggable={false} />
            <span className={`bs-dayend__flw-val${deltas.followers < 0 ? ' bs-dayend__flw-val--neg' : ''}`}
                  style={{ color: 'var(--bs-followers)' }}>
              {deltas.followers > 0 ? '+' : ''}{deltas.followers}
            </span>
          </div>

          <button className="bs-dayend__continue" onPointerDown={onContinue}>
            {day >= 13
              ? getText('查看结局', 'See ending')
              : getText(`继续 → 第 ${day + 1} 天`, `Continue → Day ${day + 1}`)}
          </button>
        </div>
      </div>
    );
  })
);

function StatDelta({ icon, val, color }: { icon: string; val: number; color: string }) {
  const sign = val > 0 ? '+' : '';
  return (
    <div className="bs-dayend__stat">
      <img className="bs-dayend__stat-icon" src={icon} alt="" draggable={false} />
      <span className={`bs-dayend__stat-val${val < 0 ? ' bs-dayend__stat-val--neg' : ''}`}
            style={{ color }}>
        {sign}{val}
      </span>
    </div>
  );
}

DayEndScreen.displayName = 'DayEndScreen';
export default DayEndScreen;
