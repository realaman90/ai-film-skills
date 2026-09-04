#!/usr/bin/env python3
"""Generate a Remotion scenes.json from CLI flags.

Example:
    python3 build_remotion_timeline.py \
        --project /tmp/my-film \
        --clip clips/scene_01.mp4:10 \
        --clip clips/scene_02.mp4:12 \
        --image hero.png:4 \
        --title "Chapter One|3" \
        --music audio/bgmusic.mp3 \
        --voiceover audio/vo.mp3 \
        --logo logo.png

All asset paths are relative to <project>/public/.
"""
import argparse
import json
import os
import sys


def split_last(value: str, sep: str) -> tuple[str, str]:
    if sep not in value:
        raise ValueError(f"expected '{sep}' in value: {value!r}")
    head, tail = value.rsplit(sep, 1)
    return head, tail


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True, help="Remotion project dir")
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--width", type=int, default=1920)
    p.add_argument("--height", type=int, default=1080)
    p.add_argument(
        "--clip",
        action="append",
        default=[],
        help="Video clip 'path:seconds' (repeatable)",
    )
    p.add_argument(
        "--image",
        action="append",
        default=[],
        help="Image 'path:seconds' (Ken Burns on, repeatable)",
    )
    p.add_argument(
        "--title",
        action="append",
        default=[],
        help="Title card 'text|seconds' (repeatable)",
    )
    p.add_argument("--music", help="Background music path (under public/)")
    p.add_argument("--music-volume", type=float, default=0.12)
    p.add_argument("--voiceover", help="Voiceover audio path (under public/)")
    p.add_argument(
        "--vo-offset",
        type=float,
        default=1.0,
        help="Voiceover start offset in seconds (default 1.0)",
    )
    p.add_argument("--logo", help="Logo path (under public/)")
    p.add_argument(
        "--logo-position",
        default="bottom-right",
        choices=["bottom-right", "bottom-left", "top-right", "top-left"],
    )
    p.add_argument("--logo-width", type=int, default=200)
    p.add_argument("--background", default="#0a0a0f")
    p.add_argument(
        "--subtitles",
        help="Path to a subtitles JSON file (list of {start,end,text})",
    )
    args = p.parse_args()

    scenes: list[dict] = []

    for entry in args.clip:
        try:
            src, dur = split_last(entry, ":")
        except ValueError as e:
            print(f"bad --clip: {e}", file=sys.stderr)
            return 2
        scenes.append(
            {
                "type": "video",
                "src": src,
                "durationFrames": int(float(dur) * args.fps),
                "fade": True,
                "kenBurns": False,
            }
        )

    for entry in args.image:
        try:
            src, dur = split_last(entry, ":")
        except ValueError as e:
            print(f"bad --image: {e}", file=sys.stderr)
            return 2
        scenes.append(
            {
                "type": "image",
                "src": src,
                "durationFrames": int(float(dur) * args.fps),
                "fade": True,
                "kenBurns": True,
            }
        )

    for entry in args.title:
        try:
            text, dur = split_last(entry, "|")
        except ValueError as e:
            print(f"bad --title (expected 'text|seconds'): {e}", file=sys.stderr)
            return 2
        scenes.append(
            {
                "type": "title",
                "text": text,
                "durationFrames": int(float(dur) * args.fps),
            }
        )

    if not scenes:
        print("error: provide at least one --clip, --image, or --title", file=sys.stderr)
        return 2

    data: dict = {
        "fps": args.fps,
        "width": args.width,
        "height": args.height,
        "background": args.background,
        "scenes": scenes,
    }

    audio: dict = {}
    if args.music:
        audio["music"] = args.music
        audio["musicVolume"] = args.music_volume
    if args.voiceover:
        audio["voiceover"] = args.voiceover
        audio["voOffsetFrames"] = int(args.vo_offset * args.fps)
    if audio:
        data["audio"] = audio

    if args.logo:
        data["logo"] = {
            "src": args.logo,
            "position": args.logo_position,
            "width": args.logo_width,
            "appearFrame": args.fps * 2,
        }

    if args.subtitles:
        with open(args.subtitles) as f:
            data["subtitles"] = json.load(f)

    out_path = os.path.join(args.project, "public", "scenes.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)

    total = sum(s["durationFrames"] for s in scenes)
    print(f"Wrote {out_path}")
    print(f"Total duration: {total} frames ({total / args.fps:.2f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
