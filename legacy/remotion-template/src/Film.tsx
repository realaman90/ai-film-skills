import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
  OffthreadVideo,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import scenesData from '../public/scenes.json';

type VideoScene = {
  type: 'video';
  src: string;
  durationFrames: number;
  fade?: boolean;
  kenBurns?: boolean;
  playbackRate?: number;
  text?: string;
};

type ImageScene = {
  type: 'image';
  src: string;
  durationFrames: number;
  fade?: boolean;
  kenBurns?: boolean;
  text?: string;
};

type TitleScene = {
  type: 'title';
  text: string;
  durationFrames: number;
  color?: string;
  background?: string;
};

type Scene = VideoScene | ImageScene | TitleScene;

interface ScenesData {
  fps: number;
  width: number;
  height: number;
  background?: string;
  scenes: Scene[];
  audio?: {
    music?: string;
    musicVolume?: number;
    voiceover?: string;
    voOffsetFrames?: number;
  };
  logo?: {
    src: string;
    position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
    width?: number;
    appearFrame?: number;
  };
  subtitles?: Array<{ start: number; end: number; text: string }>;
}

const data = scenesData as unknown as ScenesData;

const FadeWrapper: React.FC<{
  children: React.ReactNode;
  frames: number;
  enabled: boolean;
  kenBurns: boolean;
}> = ({ children, frames, enabled, kenBurns }) => {
  const frame = useCurrentFrame();
  const fadeIn = enabled
    ? interpolate(frame, [0, 18], [0, 1], { extrapolateRight: 'clamp' })
    : 1;
  const fadeOut = enabled
    ? interpolate(frame, [frames - 18, frames], [1, 0], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      })
    : 1;
  const scale = kenBurns
    ? interpolate(frame, [0, frames], [1.0, 1.06], { extrapolateRight: 'clamp' })
    : 1;
  return (
    <AbsoluteFill
      style={{
        opacity: Math.min(fadeIn, fadeOut),
        transform: `scale(${scale})`,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};

const TextOverlay: React.FC<{ text: string; frames: number }> = ({ text, frames }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(
    frame,
    [0, 15, Math.max(15, frames - 15), frames],
    [0, 1, 1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );
  const translateY = interpolate(frame, [0, 15], [30, 0], { extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill
      style={{ justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 120 }}
    >
      <div
        style={{
          opacity,
          transform: `translateY(${translateY}px)`,
          fontSize: 72,
          fontWeight: 800,
          color: 'white',
          textShadow: '0 4px 20px rgba(0,0,0,0.8)',
          fontFamily: 'sans-serif',
          textAlign: 'center',
          maxWidth: '80%',
          lineHeight: 1.1,
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};

const TitleCard: React.FC<{
  text: string;
  color?: string;
  background?: string;
}> = ({ text, color = '#ffffff', background = '#000000' }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame, fps, config: { damping: 12 } });
  return (
    <AbsoluteFill
      style={{
        backgroundColor: background,
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <div
        style={{
          transform: `scale(${scale})`,
          fontSize: 96,
          fontWeight: 900,
          color,
          fontFamily: 'sans-serif',
          letterSpacing: '-0.02em',
          textAlign: 'center',
          padding: '0 80px',
          lineHeight: 1.05,
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};

const Subtitles: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const voOffset = (data.audio?.voOffsetFrames ?? 0) / fps;
  const t = frame / fps - voOffset;
  const subs = data.subtitles ?? [];
  const active = subs.find((s) => t >= s.start - 0.1 && t <= s.end);
  if (!active) return null;
  const dur = Math.max(0.01, active.end - active.start);
  const p = Math.max(0, Math.min(1, (t - active.start) / dur));
  const fadeIn = interpolate(p, [0, 0.08], [0, 1], { extrapolateRight: 'clamp' });
  const fadeOut = interpolate(p, [0.92, 1], [1, 0], { extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill
      style={{ justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 60 }}
    >
      <div
        style={{
          opacity: Math.min(fadeIn, fadeOut),
          fontSize: 36,
          color: 'rgba(255,255,255,0.96)',
          backgroundColor: 'rgba(0,0,0,0.55)',
          padding: '10px 28px',
          borderRadius: 6,
          fontFamily: 'sans-serif',
          maxWidth: '80%',
          textAlign: 'center',
        }}
      >
        {active.text}
      </div>
    </AbsoluteFill>
  );
};

const Logo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const logo = data.logo;
  if (!logo) return null;
  const start = logo.appearFrame ?? 60;
  if (frame < start) return null;
  const local = frame - start;
  const scale = spring({ frame: local, fps, config: { damping: 12 } });
  const pos: Record<string, React.CSSProperties> = {
    'bottom-right': { bottom: 50, right: 50 },
    'bottom-left': { bottom: 50, left: 50 },
    'top-right': { top: 50, right: 50 },
    'top-left': { top: 50, left: 50 },
  };
  return (
    <Img
      src={staticFile(logo.src)}
      style={{
        position: 'absolute',
        width: logo.width ?? 200,
        transform: `scale(${scale})`,
        ...pos[logo.position ?? 'bottom-right'],
      }}
    />
  );
};

export const Film: React.FC = () => {
  let cursor = 0;
  return (
    <AbsoluteFill style={{ backgroundColor: data.background ?? '#0a0a0f' }}>
      {data.scenes.map((scene, i) => {
        const from = cursor;
        cursor += scene.durationFrames;
        return (
          <Sequence key={i} from={from} durationInFrames={scene.durationFrames}>
            {scene.type === 'video' && (
              <FadeWrapper
                frames={scene.durationFrames}
                enabled={scene.fade ?? true}
                kenBurns={scene.kenBurns ?? false}
              >
                <OffthreadVideo
                  src={staticFile(scene.src)}
                  volume={0}
                  playbackRate={scene.playbackRate ?? 1}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
                {scene.text && (
                  <TextOverlay text={scene.text} frames={scene.durationFrames} />
                )}
              </FadeWrapper>
            )}
            {scene.type === 'image' && (
              <FadeWrapper
                frames={scene.durationFrames}
                enabled={scene.fade ?? true}
                kenBurns={scene.kenBurns ?? true}
              >
                <Img
                  src={staticFile(scene.src)}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
                {scene.text && (
                  <TextOverlay text={scene.text} frames={scene.durationFrames} />
                )}
              </FadeWrapper>
            )}
            {scene.type === 'title' && (
              <TitleCard
                text={scene.text}
                color={scene.color}
                background={scene.background}
              />
            )}
          </Sequence>
        );
      })}

      {data.audio?.music && (
        <Audio
          src={staticFile(data.audio.music)}
          volume={data.audio.musicVolume ?? 0.12}
        />
      )}
      {data.audio?.voiceover && (
        <Sequence from={data.audio.voOffsetFrames ?? 0}>
          <Audio src={staticFile(data.audio.voiceover)} />
        </Sequence>
      )}

      <Subtitles />
      <Logo />
    </AbsoluteFill>
  );
};
