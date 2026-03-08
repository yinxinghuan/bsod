import React, { forwardRef } from 'react';
import posterSrc from '../img/poster.png';
import './SplashScreen.less';

interface Props {
  onDone: () => void;
}

const SplashScreen = React.memo(
  forwardRef<HTMLDivElement, Props>(function SplashScreen({ onDone }, ref) {
    return (
      <div className="bs-splash" ref={ref}>
        <img
          className="bs-splash__img"
          src={posterSrc}
          alt="BSOD"
          draggable={false}
          onAnimationEnd={onDone}
        />
      </div>
    );
  })
);

SplashScreen.displayName = 'SplashScreen';
export default SplashScreen;
