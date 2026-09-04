# Remotion -- Video Assembly & Rendering

## Setup

```bash
npx create-video@latest my-film && cd my-film && npm install
npm run dev  # Preview at localhost:3000
```

## Core Concepts

### Composition = Video Definition

```tsx
import {Composition} from 'remotion';
import {Film} from './Film';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Film"
    component={Film}
    durationInFrames={1440}  // 60s at 24fps
    fps={24}
    width={1920}
    height={1080}
  />
);
```

### Sequencing Clips

```tsx
import {Sequence, Audio, AbsoluteFill, OffthreadVideo, useCurrentFrame, interpolate, staticFile} from 'remotion';

export const Film: React.FC = () => (
  <AbsoluteFill style={{backgroundColor: '#0a0a0f'}}>
    {/* Scene 1: 0-10s (frames 0-240) */}
    <Sequence from={0} durationInFrames={240}>
      <OffthreadVideo src={staticFile('cfr/scene_01.mp4')} volume={0}
        style={{width: '100%', height: '100%', objectFit: 'cover'}} />
    </Sequence>

    {/* Scene 2: 10-20s */}
    <Sequence from={240} durationInFrames={240}>
      <OffthreadVideo src={staticFile('cfr/scene_02.mp4')} volume={0}
        style={{width: '100%', height: '100%', objectFit: 'cover'}} />
    </Sequence>

    {/* Background music - full duration */}
    <Audio src={staticFile('audio/bgmusic.mp3')} volume={0.12} />

    {/* Voiceover starting at 1s */}
    <Sequence from={24}>
      <Audio src={staticFile('audio/voiceover.mp3')} volume={1.0} />
    </Sequence>
  </AbsoluteFill>
);
```

### Fade Transitions

```tsx
const FadeScene: React.FC<{src: string; frames: number; rate?: number}> = ({src, frames, rate = 1}) => {
  const frame = useCurrentFrame();
  const fadeIn = interpolate(frame, [0, 18], [0, 1], {extrapolateRight: 'clamp'});
  const fadeOut = interpolate(frame, [frames - 18, frames], [1, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  // Ken Burns: subtle zoom 1.0 -> 1.05
  const scale = interpolate(frame, [0, frames], [1.0, 1.05], {extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{opacity: Math.min(fadeIn, fadeOut)}}>
      <OffthreadVideo src={src} volume={0} playbackRate={rate}
        style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${scale})`}} />
    </AbsoluteFill>
  );
};
```

### Text Overlays

```tsx
const TextOverlay: React.FC<{text: string}> = ({text}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 15, 75, 90], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const translateY = interpolate(frame, [0, 15], [30, 0], {extrapolateRight: 'clamp'});

  return (
    <div style={{
      position: 'absolute', bottom: 100, width: '100%', textAlign: 'center',
      opacity, transform: `translateY(${translateY}px)`,
      fontSize: 72, fontWeight: 'bold', color: 'white',
      textShadow: '0 4px 20px rgba(0,0,0,0.8)',
    }}>
      {text}
    </div>
  );
};
```

### Subtitle Overlay (Whisper-synced)

```tsx
type Sub = {start: number; end: number; text: string};

const Subtitles: React.FC<{subs: Sub[]; fps: number; voOffset?: number}> = ({
  subs, fps, voOffset = 0,
}) => {
  const frame = useCurrentFrame();
  const t = frame / fps - voOffset;
  const active = subs.find(s => t >= s.start - 0.1 && t <= s.end);
  if (!active) return null;

  const dur = active.end - active.start;
  const p = Math.max(0, Math.min(1, (t - active.start) / dur));
  const fadeIn = interpolate(p, [0, 0.05], [0, 1], {extrapolateRight: 'clamp'});
  const fadeOut = interpolate(p, [0.92, 1], [1, 0], {extrapolateRight: 'clamp'});

  return (
    <div style={{
      position: 'absolute', bottom: 60, left: 0, right: 0,
      display: 'flex', justifyContent: 'center',
      opacity: Math.min(fadeIn, fadeOut),
    }}>
      <div style={{
        fontSize: 32, fontFamily: "'Georgia', serif", fontStyle: 'italic',
        padding: '8px 24px', backgroundColor: 'rgba(0,0,0,0.5)', borderRadius: 4,
        color: 'rgba(255,255,255,0.92)', maxWidth: '80%', textAlign: 'center',
      }}>
        {active.text}
      </div>
    </div>
  );
};
```

### Logo with Spring Animation

```tsx
import {Img, spring, useVideoConfig} from 'remotion';

const Logo: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const scale = spring({frame, fps, config: {damping: 12}});

  return (
    <Img src={staticFile('logo.png')} style={{
      position: 'absolute', bottom: 50, right: 50, width: 200,
      transform: `scale(${scale})`,
    }} />
  );
};
```

---

## Rendering

```bash
# Standard render
npx remotion render src/index.ts Film out/film.mp4

# Fix WebGL issues
npx remotion render src/index.ts Film out/film.mp4 --concurrency=1 --gl=angle

# Single frame (thumbnail)
npx remotion render src/index.ts Film out/thumb.png --frames=0

# GIF
npx remotion render src/index.ts Film out/clip.gif
```

---

## Key APIs

| API | Purpose |
|-----|---------|
| `<OffthreadVideo>` | Video clips (better than `<Video>`) |
| `<Audio>` | Audio tracks |
| `<Img>` | Image overlays |
| `<Sequence>` | Time sequencing |
| `useCurrentFrame()` | Current frame for animations |
| `interpolate()` | Map frame ranges to values |
| `spring()` | Physics-based animations |
| `staticFile()` | Reference public/ files |
| `<AbsoluteFill>` | Full-frame positioning |

---

## Audio Levels

| Track | Volume |
|-------|--------|
| Voiceover | 1.0 |
| Background music | 0.10-0.15 |
| Sound effects | 0.15-0.30 |

---

## Timeline Mapping

```
scene_duration_frames = (vo_segment_end - vo_segment_start + padding) * FPS
playback_rate = clip_actual_duration / scene_duration
```

If playback_rate < 0.6, scene is too stretched -- split into two clips or add text card.

---

## Quick ffmpeg Alternative

```bash
# Concatenate clips
ffmpeg -f concat -safe 0 -i filelist.txt -c copy merged.mp4

# Add audio
ffmpeg -i merged.mp4 -i bgmusic.mp3 -i voiceover.mp3 \
  -filter_complex "[1]volume=0.15[bg];[2]adelay=1000|1000[vo];[bg][vo]amix=inputs=2[a]" \
  -map 0:v -map "[a]" -shortest -c:v copy final.mp4
```

## Output Formats

MP4 (H.264), WebM (VP8/VP9), GIF, PNG sequence, ProRes
