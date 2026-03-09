import React, { forwardRef } from 'react';
import './DailyDrainNotice.less';

interface Props {
  // no interaction needed — dismissed automatically when stat animation ends
}

const DailyDrainNotice = React.memo(
  forwardRef<HTMLDivElement, Props>(function DailyDrainNotice(_props, ref) {
    return (
      <div className="bs-drain-notice" ref={ref}>
        <span className="bs-drain-notice__text">DAILY DRAIN</span>
      </div>
    );
  })
);

DailyDrainNotice.displayName = 'DailyDrainNotice';
export default DailyDrainNotice;
