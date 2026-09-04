import React from 'react';
import { Composition } from 'remotion';
import { Film } from './Film';
import scenes from '../public/scenes.json';

const totalFrames = (scenes.scenes as Array<{ durationFrames: number }>).reduce(
  (acc, s) => acc + (s.durationFrames || 0),
  0,
);

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Film"
      component={Film}
      durationInFrames={Math.max(totalFrames, 30)}
      fps={scenes.fps || 30}
      width={scenes.width || 1920}
      height={scenes.height || 1080}
    />
  );
};
