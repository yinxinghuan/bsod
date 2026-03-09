import React, { forwardRef, useRef, useState } from 'react';
import type { StatEffect, StoryEvent } from '../types';
import { getText } from '../i18n';
import iconEnergy    from '../img/icon_energy.png';
import iconMood      from '../img/icon_mood.png';
import iconFocus     from '../img/icon_focus.png';
import iconFollowers from '../img/icon_followers.png';
import './EventOverlay.less';

interface Props {
  event: StoryEvent;
  onChoice: (index: number) => void;
  onDismiss: () => void;
}

const STAT_ICONS: { key: keyof StatEffect; icon: string }[] = [
  { key: 'energy',    icon: iconEnergy },
  { key: 'mood',      icon: iconMood },
  { key: 'focus',     icon: iconFocus },
  { key: 'followers', icon: iconFollowers },
];

const EventOverlay = React.memo(
  forwardRef<HTMLDivElement, Props>(function EventOverlay({ event, onChoice, onDismiss }, ref) {
    const [feedback, setFeedback] = useState<{ effect: StatEffect; index: number } | null>(null);
    const chosenRef = useRef(false);

    const handleChoice = (index: number) => {
      if (chosenRef.current) return;
      chosenRef.current = true;
      setFeedback({ effect: event.choices![index].effect, index });
    };

    const handleFeedbackDismiss = () => {
      if (feedback) onChoice(feedback.index);
    };

    return (
      <div className="bs-event" ref={ref}>
        <div className="bs-event__card">
          {/* Visitor header — avatar + name */}
          {event.visitorImg && (
            <div className="bs-event__visitor-header">
              <div className="bs-event__visitor-avatar">
                <img
                  src={event.visitorImg}
                  alt={event.visitorName ?? ''}
                  draggable={false}
                />
              </div>
              {event.visitorName && (
                <span className="bs-event__visitor-name">{event.visitorName}</span>
              )}
            </div>
          )}
          <p className="bs-event__text">{getText(event.textZh, event.textEn)}</p>

          {/* Stat delta feedback — shown after a choice is made */}
          {feedback ? (
            <div className="bs-event__feedback" onPointerDown={handleFeedbackDismiss}>
              <div className="bs-event__feedback-pills">
                {STAT_ICONS.map(({ key, icon }) => {
                  const v = feedback.effect[key] as number | undefined;
                  if (!v) return null;
                  return (
                    <div key={key} className={`bs-event__feedback-pill bs-event__feedback-pill--${v > 0 ? 'pos' : 'neg'}`}>
                      <img src={icon} alt={key} draggable={false} />
                      <span>{v > 0 ? '+' : ''}{v}</span>
                    </div>
                  );
                })}
              </div>
              <div className="bs-event__feedback-hint">{getText('点击继续', 'Tap to continue')}</div>
            </div>
          ) : event.choices && event.choices.length > 0 ? (
            <div className="bs-event__choices">
              {event.choices.map((c, i) => (
                <button
                  key={i}
                  className="bs-event__choice"
                  onPointerDown={() => handleChoice(i)}
                >
                  {getText(c.labelZh, c.labelEn)}
                </button>
              ))}
            </div>
          ) : (
            <button className="bs-event__dismiss" onPointerDown={onDismiss}>
              {getText('继续', 'Continue')}
            </button>
          )}
        </div>
      </div>
    );
  })
);

EventOverlay.displayName = 'EventOverlay';
export default EventOverlay;
