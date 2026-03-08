import React, { forwardRef } from 'react';
import { useLocale } from '../i18n';
import type { StoryEvent } from '../types';
import './EventOverlay.less';

interface Props {
  event: StoryEvent;
  onChoice: (index: number) => void;
  onDismiss: () => void;
}

const EventOverlay = React.memo(
  forwardRef<HTMLDivElement, Props>(function EventOverlay({ event, onChoice, onDismiss }, ref) {
    const { getText } = useLocale();
    const text = getText(event.textZh, event.textEn);

    return (
      <div className="bs-event" ref={ref}>
        <div className="bs-event__card">
          <p className="bs-event__text">{text}</p>
          {event.choices && event.choices.length > 0 ? (
            <div className="bs-event__choices">
              {event.choices.map((c, i) => (
                <button
                  key={i}
                  className="bs-event__choice"
                  onPointerDown={() => onChoice(i)}
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
