#!/usr/bin/env python3
"""Generate a HyperFrames composition (index.html) from CLI flags or a scenes.json spec.

HyperFrames = HTML + GSAP -> deterministic MP4 (replaces the old Remotion template).
Docs: reference/hyperframes.md. Validate with `npx hyperframes check`, render with
scripts/render_hyperframes.sh.

Examples:
    # Ad / promo: clips back-to-back with crossfades, music bed, VO, logo bug, end card
    python3 build_hyperframes_timeline.py \
        --project /tmp/my-film/film \
        --clip assets/clips/scene_01.mp4:3 \
        --clip assets/clips/scene_02.mp4:2.5:trim=1.2 \
        --clip "assets/clips/scene_03.mp4:3:text=Made for mornings" \
        --image assets/images/hero.png:3 \
        --title "NORRA|2" \
        --end-card "norra.se|3:cta=Shop the serum" \
        --music assets/audio/bgmusic.mp3 --music-volume 0.15 \
        --voiceover assets/audio/vo.mp3 --vo-offset 0.8 \
        --logo assets/images/logo.png --logo-position bottom-right \
        --subtitles assets/audio/vo_subs.json \
        --transition crossfade --transition-duration 0.5 \
        --aspect 9:16 --fps 24

    # Or drive everything from a JSON spec (same schema, written to <project>/scenes.json)
    python3 build_hyperframes_timeline.py --project /tmp/my-film/film --spec scenes.json

Scene entry syntax (CLI):
    --clip  path:seconds[:trim=S][:rate=R][:text=Overlay text][:audio=1]   (rate is baked in with ffmpeg setpts/atempo)
    --image path:seconds[:text=Overlay text][:kenburns=0]
    --title "Text|seconds"
    --end-card "Text|seconds[:cta=Call to action]"
    --sfx   path:start_seconds:volume

All asset paths are relative to <project>/ (convention: assets/clips, assets/audio, assets/images).
"""
import argparse
import json
import os
import sys
from html import escape

ASPECTS = {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080), "21:9": (2560, 1080)}
TRANSITIONS = ("cut", "crossfade", "blur", "dip")


# ---------------------------------------------------------------- parsing helpers

def parse_kv(parts):
    """['trim=1.2', 'text=Hello'] -> {'trim': '1.2', 'text': 'Hello'}"""
    out = {}
    for p in parts:
        if "=" in p:
            k, v = p.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def parse_clip(entry):
    parts = entry.split(":")
    if len(parts) < 2:
        raise ValueError(f"--clip expects 'path:seconds[...]', got {entry!r}")
    kv = parse_kv(parts[2:])
    scene = {"type": "video", "src": parts[0], "duration": float(parts[1])}
    if "trim" in kv:
        scene["mediaStart"] = float(kv["trim"])
    if "rate" in kv:
        scene["playbackRate"] = float(kv["rate"])
    if "text" in kv:
        scene["text"] = kv["text"]
    if kv.get("audio") in ("1", "true", "yes"):
        scene["clipAudio"] = True
    return scene


def parse_image(entry):
    parts = entry.split(":")
    if len(parts) < 2:
        raise ValueError(f"--image expects 'path:seconds[...]', got {entry!r}")
    kv = parse_kv(parts[2:])
    scene = {"type": "image", "src": parts[0], "duration": float(parts[1]), "kenBurns": True}
    if "text" in kv:
        scene["text"] = kv["text"]
    if kv.get("kenburns") in ("0", "false", "no"):
        scene["kenBurns"] = False
    return scene


def parse_title(entry, kind="title"):
    if "|" not in entry:
        raise ValueError(f"--{kind.replace('_', '-')} expects 'Text|seconds', got {entry!r}")
    text, rest = entry.rsplit("|", 1)
    parts = rest.split(":")
    kv = parse_kv(parts[1:])
    scene = {"type": kind, "text": text, "duration": float(parts[0])}
    if "cta" in kv:
        scene["cta"] = kv["cta"]
    if "sub" in kv:
        scene["subtitle"] = kv["sub"]
    return scene


def load_subtitles(path):
    """Accept [{start,end,text}] or Whisper JSON ({segments:[...]}) or hyperframes transcript."""
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict) and "segments" in data:
        return [{"start": s["start"], "end": s["end"], "text": s["text"].strip()} for s in data["segments"]]
    if isinstance(data, dict) and "words" in data:  # word-level -> group ~5 words
        words = data["words"]
        cues, chunk = [], []
        for w in words:
            chunk.append(w)
            if len(chunk) >= 5 or w.get("word", "").rstrip().endswith((".", "!", "?", ",")):
                cues.append({"start": chunk[0]["start"], "end": chunk[-1]["end"],
                             "text": " ".join(x["word"].strip() for x in chunk)})
                chunk = []
        if chunk:
            cues.append({"start": chunk[0]["start"], "end": chunk[-1]["end"],
                         "text": " ".join(x["word"].strip() for x in chunk)})
        return cues
    return data


# ---------------------------------------------------------------- html builder

def fmt(x):
    return f"{x:.3f}".rstrip("0").rstrip(".")


def retime_sidecar(project_dir, rel_src, rate):
    """clips/x.mp4 + rate 0.8 -> clips/x.rate0.8.mp4 (video stretched with setpts, audio with atempo).
    HyperFrames' frame extractor does not honor data-playback-rate reliably (coverage gate), so we bake it in."""
    import subprocess
    if not project_dir or abs(rate - 1.0) < 1e-3:
        return rel_src
    src = os.path.join(project_dir, rel_src)
    stem, ext = os.path.splitext(rel_src)
    rel_out = f"{stem}.rate{rate:g}{ext or '.mp4'}"
    out = os.path.join(project_dir, rel_out)
    if os.path.exists(out):
        return rel_out
    try:
        probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_type",
                                "-of", "csv=p=0", src], capture_output=True, text=True, timeout=20)
        has_audio = "audio" in probe.stdout
        if has_audio and 0.5 <= rate <= 100:
            fc = f"[0:v]setpts=PTS/{rate}[v];[0:a]atempo={rate}[a]"
            cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                   "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "aac", "-r", "24", out]
        else:
            cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-filter:v", f"setpts=PTS/{rate}", "-an",
                   "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-r", "24", out]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if res.returncode == 0 and os.path.exists(out):
            print(f"retimed {rel_src} x{rate:g} -> {rel_out}", file=sys.stderr)
            return rel_out
        print(f"WARNING could not retime {rel_src}: {res.stderr.strip()[:200]}", file=sys.stderr)
    except Exception as e:
        print(f"WARNING could not retime {rel_src}: {e}", file=sys.stderr)
    return rel_src


def extract_audio_sidecar(project_dir, rel_src):
    """clips/x.mp4 -> clips/x.audio.m4a (relative path) or None if the clip has no audio."""
    import subprocess
    if not project_dir:
        return None
    src = os.path.join(project_dir, rel_src)
    rel_out = os.path.splitext(rel_src)[0] + ".audio.m4a"
    out = os.path.join(project_dir, rel_out)
    if os.path.exists(out):
        return rel_out
    try:
        probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_type",
                                "-of", "csv=p=0", src], capture_output=True, text=True, timeout=20)
        if "audio" not in probe.stdout:
            return None
        res = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vn", "-c:a", "aac", "-b:a", "192k", out],
                             capture_output=True, text=True, timeout=120)
        return rel_out if res.returncode == 0 and os.path.exists(out) else None
    except Exception:
        return None


def media_duration(path):
    """Seconds via ffprobe, or None if unavailable."""
    import subprocess
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                             capture_output=True, text=True, timeout=20)
        return float(out.stdout.strip()) if out.returncode == 0 and out.stdout.strip() else None
    except Exception:
        return None


def build_html(spec):
    fps = spec.get("fps", 24)
    width, height = spec["width"], spec["height"]
    portrait = height > width
    bg = spec.get("background", "#0a0a0f")
    transition = spec.get("transition", "crossfade")
    tdur = float(spec.get("transitionDuration", 0.5)) if transition != "cut" else 0.0
    scenes = spec["scenes"]
    if not scenes:
        raise ValueError("no scenes")

    # --- timing: sequential, each scene overlaps the previous by tdur (except first)
    t = 0.0
    for i, s in enumerate(scenes):
        s["id"] = f"scene-{i + 1:02d}"
        s["start"] = 0.0 if i == 0 else max(0.0, t - tdur)
        s["end"] = s["start"] + float(s["duration"])
        t = s["end"]
    total = t

    base_font = 0.045 * min(width, height)  # scales with frame size
    title_font = base_font * 1.9
    overlay_font = base_font * 1.15
    sub_font = base_font * 0.75

    css = f"""
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {width}px; height: {height}px; overflow: hidden; background: #000; }}
      body {{ font-family: "Inter", system-ui, -apple-system, sans-serif; color: #fff; }}
      #root {{ position: relative; width: {width}px; height: {height}px; overflow: hidden; background: {bg}; }}
      .clip {{ position: absolute; inset: 0; }}
      video.clip {{ width: 100%; height: 100%; object-fit: cover; display: block; background: {bg}; }}
      .scene-img {{ position: absolute; inset: 0; overflow: hidden; }}
      .scene-img img {{ width: 100%; height: 100%; object-fit: cover; display: block; transform-origin: center center; }}
      .overlay {{ position: absolute; inset: 0; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;
                 padding: 0 {int(width * 0.08)}px {int(height * (0.16 if portrait else 0.12))}px; text-align: center; pointer-events: none; }}
      .overlay .line {{ font-size: {overlay_font:.0f}px; font-weight: 700; line-height: 1.15; letter-spacing: -0.01em;
                       text-shadow: 0 4px 24px rgba(0,0,0,0.75); max-width: 100%; }}
      .title-card {{ position: absolute; inset: 0; display: flex; flex-direction: column; justify-content: center; align-items: center;
                    background: {spec.get('titleBackground', '#000')}; padding: 0 {int(width * 0.1)}px; text-align: center; }}
      .title-card h1 {{ font-size: {title_font:.0f}px; font-weight: 800; letter-spacing: -0.02em; line-height: 1.05; color: {spec.get('titleColor', '#fff')}; }}
      .title-card .cta {{ margin-top: {int(base_font * 0.9)}px; font-size: {base_font * 0.95:.0f}px; font-weight: 500; opacity: 0.9;
                         padding: {int(base_font * 0.35)}px {int(base_font * 0.9)}px; border: 2px solid rgba(255,255,255,0.6); border-radius: 999px; }}
      .title-card .sub {{ margin-top: {int(base_font * 0.5)}px; font-size: {base_font * 0.9:.0f}px; font-weight: 400; opacity: 0.8; }}
      .subtitle {{ position: absolute; left: 0; right: 0; bottom: {int(height * (0.10 if portrait else 0.07))}px; display: flex; justify-content: center; pointer-events: none; }}
      .subtitle span {{ font-size: {sub_font:.0f}px; line-height: 1.3; color: rgba(255,255,255,0.96); background: rgba(0,0,0,0.55);
                       padding: {int(sub_font * 0.3)}px {int(sub_font * 0.8)}px; border-radius: 8px; max-width: 82%; text-align: center; }}
      .logo-wrap {{ pointer-events: none; }}
      .logo-wrap img {{ position: absolute; display: block; height: auto; transform-origin: center center; }}
      .fade {{ position: absolute; inset: 0; background: #000; pointer-events: none; }}
    """

    body = []
    tl = []  # GSAP lines

    def esc(s):
        return escape(str(s), quote=True)

    # --- scenes
    for i, s in enumerate(scenes):
        sid, st, du = s["id"], s["start"], float(s["duration"])
        z = 10 + i
        if s["type"] == "video":
            rate = float(s.get("playbackRate", 1.0) or 1.0)
            if abs(rate - 1.0) > 1e-3 and not s.get("retimedSrc"):
                s["retimedSrc"] = retime_sidecar(spec.get("_projectDir"), s["src"], rate)
            src = s.get("retimedSrc") or s["src"]
            # trim is authored in ORIGINAL clip seconds; scale it when the clip was retimed
            media_start = float(s.get("mediaStart", 0) or 0) / (rate if s.get("retimedSrc") and s["retimedSrc"] != s["src"] else 1.0)
            attrs = [f'id="{sid}"', 'class="clip"', f'data-start="{fmt(st)}"', f'data-duration="{fmt(du)}"',
                     'data-track-index="0"', f'src="{esc(src)}"', "muted", "playsinline", f'style="z-index:{z}"']
            if media_start:
                attrs.append(f'data-media-start="{fmt(media_start)}"')
            body.append(f"      <video {' '.join(attrs)}></video>")
            if s.get("clipAudio"):
                # HyperFrames wants a real audio file behind <audio>; extract a sidecar next to the clip
                audio_src = s.get("clipAudioSrc") or extract_audio_sidecar(spec.get("_projectDir"), src)
                if audio_src:
                    s["clipAudioSrc"] = audio_src
                    a = [f'id="{sid}-audio"', f'data-start="{fmt(st)}"', f'data-duration="{fmt(du)}"', 'data-track-index="12"',
                         f'data-volume="{fmt(float(s.get("clipAudioVolume", 0.6)))}"', f'src="{esc(audio_src)}"']
                    if media_start:
                        a.append(f'data-media-start="{fmt(media_start)}"')
                    body.append(f"      <audio {' '.join(a)}></audio>")
                else:
                    print(f"WARNING {s['src']}: audio=1 requested but no audio track could be extracted", file=sys.stderr)
        elif s["type"] == "image":
            body.append(f'      <div id="{sid}" class="clip scene-img" data-start="{fmt(st)}" data-duration="{fmt(du)}" '
                        f'data-track-index="0" style="z-index:{z}"><img id="{sid}-img" src="{esc(s["src"])}" alt="" data-layout-allow-overflow /></div>')
            if s.get("kenBurns", True):
                tl.append(f'tl.fromTo("#{sid}-img", {{ scale: 1.0 }}, {{ scale: 1.08, duration: {fmt(du)}, ease: "none" }}, {fmt(st)});')
        elif s["type"] in ("title", "end_card"):
            inner = [f'<h1 id="{sid}-h1">{esc(s["text"])}</h1>']
            if s.get("subtitle"):
                inner.append(f'<div id="{sid}-sub" class="sub">{esc(s["subtitle"])}</div>')
            if s.get("cta"):
                inner.append(f'<div id="{sid}-cta" class="cta">{esc(s["cta"])}</div>')
            body.append(f'      <div id="{sid}" class="clip title-card" data-start="{fmt(st)}" data-duration="{fmt(du)}" '
                        f'data-track-index="1" style="z-index:{z}">{"".join(inner)}</div>')
            tl.append(f'tl.fromTo("#{sid}-h1", {{ autoAlpha: 0, y: 40, scale: 0.96 }}, {{ autoAlpha: 1, y: 0, scale: 1, duration: 0.7, ease: "power3.out" }}, {fmt(st + 0.1)});')
            if s.get("subtitle"):
                tl.append(f'tl.fromTo("#{sid}-sub", {{ autoAlpha: 0, y: 24 }}, {{ autoAlpha: 1, y: 0, duration: 0.6, ease: "power3.out" }}, {fmt(st + 0.35)});')
            if s.get("cta"):
                tl.append(f'tl.fromTo("#{sid}-cta", {{ autoAlpha: 0, y: 24 }}, {{ autoAlpha: 1, y: 0, duration: 0.6, ease: "power3.out" }}, {fmt(st + 0.55)});')
        else:
            raise ValueError(f"unknown scene type {s['type']!r}")

        # text overlay on video/image scenes (separate timed clip: video can't be nested in a timed wrapper)
        if s.get("text") and s["type"] in ("video", "image"):
            oid = f"{sid}-text"
            body.append(f'      <div id="{oid}" class="clip overlay" data-start="{fmt(st + 0.3)}" data-duration="{fmt(max(0.5, du - 0.3))}" '
                        f'data-track-index="2" style="z-index:{40 + i}"><div id="{oid}-line" class="line">{esc(s["text"])}</div></div>')
            tl.append(f'tl.fromTo("#{oid}-line", {{ autoAlpha: 0, y: 30 }}, {{ autoAlpha: 1, y: 0, duration: 0.5, ease: "power3.out" }}, {fmt(st + 0.3)});')

        # transition IN (incoming scene animates over the overlap; outgoing stays untouched underneath)
        if i > 0 and tdur > 0:
            T = fmt(st)
            if transition == "crossfade":
                tl.append(f'tl.fromTo("#{sid}", {{ opacity: 0 }}, {{ opacity: 1, duration: {fmt(tdur)}, ease: "power2.inOut" }}, {T});')
            elif transition == "blur":
                tl.append(f'tl.fromTo("#{sid}", {{ opacity: 0, filter: "blur(12px)", scale: 1.04 }}, '
                          f'{{ opacity: 1, filter: "blur(0px)", scale: 1, duration: {fmt(tdur)}, ease: "power2.inOut" }}, {T});')
            elif transition == "dip":
                prev = scenes[i - 1]["id"]
                half = tdur / 2
                tl.append(f'tl.to("#{prev}", {{ opacity: 0, duration: {fmt(half)}, ease: "power2.in" }}, {T});')
                tl.append(f'tl.fromTo("#{sid}", {{ opacity: 0 }}, {{ opacity: 1, duration: {fmt(half)}, ease: "power2.out" }}, {fmt(st + half)});')

    # --- subtitles (one timed clip per cue; offset by voiceover start)
    subs = spec.get("subtitles") or []
    vo_offset = float(spec.get("audio", {}).get("voOffset", 0.0))
    for j, cue in enumerate(subs):
        cs = float(cue["start"]) + vo_offset
        ce = float(cue["end"]) + vo_offset
        if ce <= cs or cs >= total:
            continue
        ce = min(ce, total)
        body.append(f'      <div id="sub-{j + 1:03d}" class="clip subtitle" data-start="{fmt(cs)}" data-duration="{fmt(ce - cs)}" '
                    f'data-track-index="3" style="z-index:80"><span>{esc(cue["text"])}</span></div>')

    # --- logo bug
    logo = spec.get("logo")
    if logo:
        lw = int(logo.get("width", max(120, width * 0.11)))
        margin = int(min(width, height) * 0.045)
        pos = logo.get("position", "bottom-right")
        style = {"bottom-right": f"right:{margin}px;bottom:{margin}px", "bottom-left": f"left:{margin}px;bottom:{margin}px",
                 "top-right": f"right:{margin}px;top:{margin}px", "top-left": f"left:{margin}px;top:{margin}px"}[pos]
        ls = float(logo.get("appear", 1.0))
        # full-frame clip wrapper; the runtime may reset a clip's own offsets, so the img carries the position
        body.append(f'      <div id="logo" class="clip logo-wrap" data-start="{fmt(ls)}" data-duration="{fmt(total - ls)}" data-track-index="4" '
                    f'style="z-index:90"><img id="logo-img" src="{esc(logo["src"])}" alt="" style="width:{lw}px;{style}" /></div>')
        tl.append(f'tl.fromTo("#logo-img", {{ autoAlpha: 0, scale: 0.7 }}, {{ autoAlpha: 1, scale: 1, duration: 0.6, ease: "back.out(1.6)" }}, {fmt(ls)});')

    # --- fade in / fade out (black overlays)
    fi = float(spec.get("fadeIn", 0.0))
    fo = float(spec.get("fadeOut", 0.0))
    if fi > 0:
        body.append(f'      <div id="fade-in" class="clip fade" data-start="0" data-duration="{fmt(fi)}" data-track-index="5" style="z-index:95"></div>')
        tl.append(f'tl.fromTo("#fade-in", {{ opacity: 1 }}, {{ opacity: 0, duration: {fmt(fi)}, ease: "power2.out" }}, 0);')
    if fo > 0:
        body.append(f'      <div id="fade-out" class="clip fade" data-start="{fmt(total - fo)}" data-duration="{fmt(fo)}" data-track-index="5" style="z-index:95"></div>')
        tl.append(f'tl.fromTo("#fade-out", {{ opacity: 0 }}, {{ opacity: 1, duration: {fmt(fo)}, ease: "power2.in" }}, {fmt(total - fo)});')

    # --- audio
    audio = spec.get("audio", {})
    project_dir = spec.get("_projectDir")
    if audio.get("music"):
        mv = float(audio.get("musicVolume", 0.15))
        mfi = float(audio.get("musicFadeIn", 1.5))
        mfo = float(audio.get("musicFadeOut", 2.5))
        music_len = media_duration(os.path.join(project_dir, audio["music"])) if project_dir else None
        mdur = min(total, music_len) if music_len else total
        body.append(f'      <audio id="music" data-start="0" data-duration="{fmt(mdur)}" data-track-index="10" src="{esc(audio["music"])}"></audio>')
        # tween values are ABSOLUTE gain (replace data-volume), so we omit data-volume and carry the level in the tween
        tl.append(f'tl.fromTo("#music", {{ volume: 0 }}, {{ volume: {fmt(mv)}, duration: {fmt(mfi)}, ease: "none" }}, 0);')
        if mfo > 0:
            tl.append(f'tl.to("#music", {{ volume: 0, duration: {fmt(mfo)}, ease: "none" }}, {fmt(max(0, mdur - mfo))});')
        if music_len and music_len < total:
            print(f"WARNING music is {music_len:.1f}s but film is {total:.1f}s — generate a longer track or the last {total - music_len:.1f}s are silent", file=sys.stderr)
    if audio.get("voiceover"):
        vv = float(audio.get("voVolume", 1.0))
        body.append(f'      <audio id="vo" data-start="{fmt(vo_offset)}" data-track-index="11" data-volume="{fmt(vv)}" src="{esc(audio["voiceover"])}"></audio>')
    for k, sfx in enumerate(audio.get("sfx", [])):
        body.append(f'      <audio id="sfx-{k + 1:02d}" data-start="{fmt(float(sfx["start"]))}" data-track-index="{13 + k}" '
                    f'data-volume="{fmt(float(sfx.get("volume", 0.25)))}" src="{esc(sfx["src"])}"></audio>')

    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={width}, height={height}" />
    <title>{esc(spec.get('title', 'Film'))}</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>{css}    </style>
  </head>
  <body>
    <!-- generated by ai-film-studio/scripts/build_hyperframes_timeline.py — edit scenes.json and re-run, or hand-edit -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{fmt(total)}" data-width="{width}" data-height="{height}" data-fps="{fps}">
{chr(10).join(body)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {(chr(10) + '      ').join(tl)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    return html, total


# ---------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--project", required=True, help="HyperFrames project dir (from new_hyperframes_project.sh)")
    p.add_argument("--spec", help="scenes.json spec (overrides CLI scene flags)")
    p.add_argument("--fps", type=int, default=24)
    p.add_argument("--aspect", default="16:9", choices=list(ASPECTS.keys()))
    p.add_argument("--width", type=int); p.add_argument("--height", type=int)
    p.add_argument("--clip", action="append", default=[], help="path:seconds[:trim=S][:rate=R][:text=..][:audio=1]")
    p.add_argument("--image", action="append", default=[], help="path:seconds[:text=..][:kenburns=0]")
    p.add_argument("--title", action="append", default=[], help="'Text|seconds[:sub=Subtitle]'")
    p.add_argument("--end-card", action="append", default=[], help="'Text|seconds[:cta=Call to action][:sub=..]'")
    p.add_argument("--order", help="Comma list to reorder scene kinds, e.g. 'title,clips,images,end' (default: title,clips,images,end)")
    p.add_argument("--transition", default="crossfade", choices=TRANSITIONS)
    p.add_argument("--transition-duration", type=float, default=0.5)
    p.add_argument("--music"); p.add_argument("--music-volume", type=float, default=0.15)
    p.add_argument("--music-fade-in", type=float, default=1.5); p.add_argument("--music-fade-out", type=float, default=2.5)
    p.add_argument("--voiceover"); p.add_argument("--vo-offset", type=float, default=0.8); p.add_argument("--vo-volume", type=float, default=1.0)
    p.add_argument("--sfx", action="append", default=[], help="path:start_seconds:volume")
    p.add_argument("--logo"); p.add_argument("--logo-position", default="bottom-right",
                                            choices=["bottom-right", "bottom-left", "top-right", "top-left"])
    p.add_argument("--logo-width", type=int); p.add_argument("--logo-appear", type=float, default=1.0)
    p.add_argument("--subtitles", help="JSON: [{start,end,text}] or Whisper output")
    p.add_argument("--fade-in", type=float, default=0.6); p.add_argument("--fade-out", type=float, default=1.0)
    p.add_argument("--background", default="#0a0a0f")
    p.add_argument("--title-background", default="#000"); p.add_argument("--title-color", default="#fff")
    p.add_argument("--name", default="Film", help="HTML <title>")
    p.add_argument("--dry-run", action="store_true", help="Print HTML to stdout, write nothing")
    args = p.parse_args()

    if args.spec:
        with open(args.spec) as f:
            spec = json.load(f)
        spec.setdefault("fps", args.fps)
        if "width" not in spec or "height" not in spec:
            spec["width"], spec["height"] = ASPECTS[spec.get("aspect", args.aspect)]
        if isinstance(spec.get("subtitles"), str):
            spec["subtitles"] = load_subtitles(os.path.join(args.project, spec["subtitles"]))
    else:
        w, h = ASPECTS[args.aspect]
        if args.width and args.height:
            w, h = args.width, args.height
        try:
            clips = [parse_clip(e) for e in args.clip]
            images = [parse_image(e) for e in args.image]
            titles = [parse_title(e, "title") for e in args.title]
            ends = [parse_title(e, "end_card") for e in args.end_card]
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        groups = {"title": titles, "clips": clips, "images": images, "end": ends}
        order = (args.order or "title,clips,images,end").split(",")
        scenes = [s for g in order for s in groups.get(g.strip(), [])]
        if not scenes:
            print("error: provide at least one --clip, --image, --title or --end-card", file=sys.stderr)
            return 2
        spec = {
            "title": args.name, "fps": args.fps, "width": w, "height": h, "aspect": args.aspect,
            "background": args.background, "titleBackground": args.title_background, "titleColor": args.title_color,
            "transition": args.transition, "transitionDuration": args.transition_duration,
            "fadeIn": args.fade_in, "fadeOut": args.fade_out, "scenes": scenes, "audio": {},
        }
        if args.music:
            spec["audio"].update({"music": args.music, "musicVolume": args.music_volume,
                                  "musicFadeIn": args.music_fade_in, "musicFadeOut": args.music_fade_out})
        if args.voiceover:
            spec["audio"].update({"voiceover": args.voiceover, "voOffset": args.vo_offset, "voVolume": args.vo_volume})
        if args.sfx:
            sfx = []
            for e in args.sfx:
                parts = e.split(":")
                if len(parts) < 2:
                    print(f"bad --sfx {e!r} (path:start[:volume])", file=sys.stderr); return 2
                sfx.append({"src": parts[0], "start": float(parts[1]), "volume": float(parts[2]) if len(parts) > 2 else 0.25})
            spec["audio"]["sfx"] = sfx
        if args.logo:
            spec["logo"] = {"src": args.logo, "position": args.logo_position, "appear": args.logo_appear}
            if args.logo_width:
                spec["logo"]["width"] = args.logo_width
        if args.subtitles:
            spec["subtitles"] = load_subtitles(args.subtitles)

    spec["_projectDir"] = os.path.abspath(args.project)
    # warn when a video slot outruns its source (HyperFrames holds the last frame -> visible freeze)
    for s in spec["scenes"]:
        if s["type"] == "video":
            src_len = media_duration(os.path.join(args.project, s["src"]))
            if src_len:
                need = float(s.get("mediaStart", 0)) + float(s["duration"]) * float(s.get("playbackRate", 1.0))
                if need > src_len + 0.05:
                    print(f"WARNING {s['src']}: slot needs {need:.2f}s of source but clip is {src_len:.2f}s (freeze at the end). "
                          f"Shorten --clip seconds, lower trim, or extend the clip.", file=sys.stderr)
    try:
        html, total = build_html(spec)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    spec.pop("_projectDir", None)

    if args.dry_run:
        print(html)
        return 0

    os.makedirs(args.project, exist_ok=True)
    out_html = os.path.join(args.project, "index.html")
    out_spec = os.path.join(args.project, "scenes.json")
    with open(out_html, "w") as f:
        f.write(html)
    with open(out_spec, "w") as f:
        json.dump(spec, f, indent=2)

    # warn about missing assets (paths relative to project)
    missing = []
    for s in spec["scenes"]:
        if s.get("src") and not os.path.exists(os.path.join(args.project, s["src"])):
            missing.append(s["src"])
    for key in ("music", "voiceover"):
        v = spec.get("audio", {}).get(key)
        if v and not os.path.exists(os.path.join(args.project, v)):
            missing.append(v)
    if spec.get("logo") and not os.path.exists(os.path.join(args.project, spec["logo"]["src"])):
        missing.append(spec["logo"]["src"])

    print(f"Wrote {out_html}")
    print(f"Wrote {out_spec}")
    print(f"Scenes: {len(spec['scenes'])} | transition={spec.get('transition')} | total {total:.2f}s @ {spec['fps']}fps | {spec['width']}x{spec['height']}")
    if missing:
        print("WARNING missing assets (relative to project):")
        for m in missing:
            print(f"  - {m}")
    print(f"Next: (cd {args.project} && npx --yes hyperframes@0.8.27 check) then scripts/render_hyperframes.sh {args.project} renders/film.mp4")
    return 0


if __name__ == "__main__":
    sys.exit(main())
