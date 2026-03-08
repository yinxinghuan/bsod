import { useRef, useEffect } from 'react';

interface Props {
  opacity?: number;
  className?: string;
}

/** Reusable TV-static noise canvas. Low-res (160×284) scaled up for chunky pixels. */
export default function NoiseCanvas({ opacity = 0.28, className }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const W = 160, H = 284;
    canvas.width = W;
    canvas.height = H;
    let animId: number;
    let tick = 0;
    const draw = () => {
      tick++;
      if (tick % 2 === 0) {
        const img = ctx.createImageData(W, H);
        const d = img.data;
        for (let i = 0; i < d.length; i += 4) {
          const v = Math.floor(Math.random() * 200);
          d[i] = v; d[i + 1] = v; d[i + 2] = v; d[i + 3] = 255;
        }
        ctx.putImageData(img, 0, 0);
      }
      animId = requestAnimationFrame(draw);
    };
    draw();
    return () => cancelAnimationFrame(animId);
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className={className}
      style={{
        position: 'absolute',
        inset: 0,
        width: '100%',
        height: '100%',
        imageRendering: 'pixelated',
        opacity,
        mixBlendMode: 'screen',
        pointerEvents: 'none',
        zIndex: 1,
      }}
    />
  );
}
