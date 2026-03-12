import React, { forwardRef, useEffect, useState } from 'react';
import posterSrc from '../img/poster.png';
// Backgrounds
import bgRoom from '../img/bg_room.png';
import bgStream from '../img/bg_stream.png';
// Isaya sprites — all emotional states
import isayaIdle from '../img/isaya_idle.png';
import isayaHappy from '../img/isaya_happy.png';
import isayaSad from '../img/isaya_sad.png';
import isayaSurprised from '../img/isaya_surprised.png';
import isayaTired from '../img/isaya_tired.png';
import isayaFocused from '../img/isaya_focused.png';
import isayaWorn from '../img/isaya_worn.png';
import isayaRundown from '../img/isaya_rundown.png';
import isayaManic from '../img/isaya_manic.png';
import isayaWreck from '../img/isaya_wreck.png';
// Status bar icons
import iconEnergy from '../img/icon_energy.png';
import iconMood from '../img/icon_mood.png';
import iconFocus from '../img/icon_focus.png';
import iconFollowers from '../img/icon_followers.png';
import iconConnection from '../img/icon_connection.png';
// Surveillance / action images
import svDesk from '../img/sv_desk.png';
import svRest from '../img/sv_rest.png';
import svEat from '../img/sv_eat.png';
import svPhone from '../img/sv_phone.png';
import svWalk from '../img/sv_walk.png';
import svSetup from '../img/sv_setup.png';
import svRelax from '../img/sv_relax.png';
import svVideo from '../img/sv_video.png';
import svGame from '../img/sv_game.png';
import './SplashScreen.less';

// Critical gameplay assets to preload while poster is showing
const PRELOAD = [
  // Backgrounds
  bgRoom, bgStream,
  // Isaya sprites
  isayaIdle, isayaHappy, isayaSad, isayaSurprised, isayaTired, isayaFocused,
  isayaWorn, isayaRundown, isayaManic, isayaWreck,
  // UI icons
  iconEnergy, iconMood, iconFocus, iconFollowers, iconConnection,
  // Surveillance images
  svDesk, svRest, svEat, svPhone, svWalk, svSetup, svRelax, svVideo, svGame,
];
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

    // Preload critical assets AFTER poster is visible (poster gets network priority)
    useEffect(() => {
      if (!posterReady) return;

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
    }, [posterReady]);

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
