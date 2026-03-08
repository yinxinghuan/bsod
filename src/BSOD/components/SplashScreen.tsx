import { useEffect, useState } from 'react';
import posterSrc from '../img/poster.png';
import './SplashScreen.less';

interface Props {
  onDone: () => void;
}

export default function SplashScreen({ onDone }: Props) {
  const [phase, setPhase] = useState<'in' | 'hold' | 'out'>('in');

  useEffect(() => {
    const t1 = setTimeout(() => setPhase('hold'), 500);
    const t2 = setTimeout(() => setPhase('out'),  2500);
    const t3 = setTimeout(() => onDone(),         3100);
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); };
  }, [onDone]);

  return (
    <div className={`bs-splash bs-splash--${phase}`}>
      <img className="bs-splash__poster" src={posterSrc} alt="" draggable={false} />
    </div>
  );
}
