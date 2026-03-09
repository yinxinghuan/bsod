import React, { forwardRef, useEffect, useState } from 'react';
import posterSrc from '../img/poster.png';
import bgRoom from '../img/bg_room.png';
import laisaIdle from '../img/laisa_idle.png';
import laisaHappy from '../img/laisa_happy.png';
import laisaSad from '../img/laisa_sad.png';
import laisaSurprised from '../img/laisa_surprised.png';
import laisaTired from '../img/laisa_tired.png';
import laisaFocused from '../img/laisa_focused.png';
import './SplashScreen.less';

// Critical gameplay assets to preload while poster is showing
const PRELOAD = [bgRoom, laisaIdle, laisaHappy, laisaSad, laisaSurprised, laisaTired, laisaFocused];
const MIN_MS = 2200;       // minimum splash display time
const MAX_ASSET_MS = 10000; // safety timeout for slow connections

interface Props { onDone: () => void; }

const SplashScreen = React.memo(
  forwardRef<HTMLDivElement, Props>(function SplashScreen({ onDone }, ref) {
    const [posterReady, setPosterReady] = useState(false);
    const [progress, setProgress] = useState(0);
    const [fading, setFading] = useState(false);
    const [minDone, setMinDone] = useState(false);
    const [assetsDone, setAssetsDone] = useState(false);

    // Minimum display timer
    useEffect(() => {
      const t = setTimeout(() => setMinDone(true), MIN_MS);
      return () => clearTimeout(t);
    }, []);

    // Preload critical assets, track progress
    useEffect(() => {
      let loaded = 0;
      const total = PRELOAD.length;

      const onOne = () => {
        loaded++;
        setProgress(loaded / total);
        if (loaded >= total) setAssetsDone(true);
      };

      PRELOAD.forEach(src => {
        const img = new Image();
        img.onload = img.onerror = onOne;
        img.src = src;
      });

      const maxT = setTimeout(() => setAssetsDone(true), MAX_ASSET_MS);
      return () => clearTimeout(maxT);
    }, []);

    // Begin fade-out when both gates pass
    useEffect(() => {
      if (minDone && assetsDone) setFading(true);
    }, [minDone, assetsDone]);

    // Call onDone after CSS fade completes
    useEffect(() => {
      if (!fading) return;
      const t = setTimeout(onDone, 500);
      return () => clearTimeout(t);
    }, [fading, onDone]);

    return (
      <div className={`bs-splash${fading ? ' bs-splash--fading' : ''}`} ref={ref}>
        <img
          className={`bs-splash__img${posterReady ? ' bs-splash__img--visible' : ''}`}
          src={posterSrc}
          alt="BSOD"
          draggable={false}
          onLoad={() => setPosterReady(true)}
        />
        <div className="bs-splash__bar-track">
          <div
            className="bs-splash__bar-fill"
            style={{ width: `${Math.round(progress * 100)}%` }}
          />
        </div>
      </div>
    );
  })
);

SplashScreen.displayName = 'SplashScreen';
export default SplashScreen;
