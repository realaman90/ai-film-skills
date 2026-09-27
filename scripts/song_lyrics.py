#!/usr/bin/env python3
"""Lyric timing + take picking for songs made with generate_song.py.

  lines  — sung line timings from a take's ElevenLabs word timestamps
           python3 scripts/song_lyrics.py lines --plan audio/song_plan.json --take audio/song_take1 \
               --out audio/lyric_lines.json
           → [{"start": 7.9, "end": 9.94, "text": "Every message gets a score"}, ...]
           Every kinetic-type line in the video comes in on `start` and is out by `end`.

  score  — which take sings the lyrics most clearly (local Whisper, nothing leaves the machine)
           python3 scripts/song_lyrics.py score --plan audio/song_plan.json audio/song_take1.mp3 audio/song_take2.mp3
           → prints % of lyric words Whisper recognises per take and names the winner.
           Needs the `whisper` CLI (pip install openai-whisper). Judgement call beyond this number is yours:
           listen to the winner once before building on it.
"""
import argparse
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile


def plan_lines(plan_path: str) -> list[str]:
    with open(plan_path) as f:
        plan = json.load(f)
    out = []
    for chunk in plan["chunks"]:
        for line in chunk["text"].split("\n"):
            line = line.strip()
            if not line or line.startswith("[") or (line.startswith("{") and line.endswith("}")):
                continue
            out.append(line)
    return out


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


def cmd_lines(args) -> None:
    lines = plan_lines(args.plan)
    with open(args.take + ".json") as f:
        stamps = json.load(f).get("words_timestamps") or []
    # drop direction words ({...}) and zero-length stamps
    stamps = [w for w in stamps if not w["word"].startswith("{") and not w["word"].endswith("}")]
    out, k = [], 0
    for line in lines:
        start = end = None
        for tok in line.split():
            while k < len(stamps) and stamps[k]["word"].strip() != tok:
                k += 1
            if k < len(stamps):
                if start is None:
                    start = stamps[k]["start_ms"]
                end = stamps[k]["end_ms"]
                k += 1
        out.append({
            "start": round(start / 1000, 2) if start is not None else None,
            "end": round(end / 1000, 2) if end is not None else None,
            "text": line,
        })
    missing = [o["text"] for o in out if o["start"] is None]
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1)
    for o in out:
        print(f'{o["start"]!s:>6} → {o["end"]!s:<6} {o["text"]}')
    if missing:
        print(f"WARN {len(missing)} line(s) not found in the timestamps — check spelling vs the plan", file=sys.stderr)


def cmd_score(args) -> None:
    if not shutil.which("whisper"):
        sys.exit("the `whisper` CLI is not installed (pip install openai-whisper)")
    lyric = words(" ".join(plan_lines(args.plan)))
    best = None
    with tempfile.TemporaryDirectory() as tmp:
        for take in args.takes:
            try:
                subprocess.run(
                    ["whisper", take, "--model", args.model, "--language", args.language,
                     "--output_format", "json", "--output_dir", tmp],
                    check=True, capture_output=True, text=True,
                )
            except subprocess.CalledProcessError as err:
                print(f"{take}: whisper failed: {err.stderr[-300:]}", file=sys.stderr)
                continue
            with open(os.path.join(tmp, os.path.splitext(os.path.basename(take))[0] + ".json")) as f:
                heard = words(json.load(f)["text"])
            sm = difflib.SequenceMatcher(a=lyric, b=heard, autojunk=False)
            matched = sum(b.size for b in sm.get_matching_blocks())
            pct = matched / max(1, len(lyric))
            print(f"{take}: {matched}/{len(lyric)} lyric words recognised ({pct:.0%})")
            if best is None or pct > best[1]:
                best = (take, pct)
    if best:
        print(f"PICK {best[0]} ({best[1]:.0%})")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("lines")
    a.add_argument("--plan", required=True)
    a.add_argument("--take", required=True, help="take path without extension (reads <take>.json)")
    a.add_argument("--out", required=True)
    b = sub.add_parser("score")
    b.add_argument("--plan", required=True)
    b.add_argument("--model", default="small")
    b.add_argument("--language", default="en")
    b.add_argument("takes", nargs="+")
    args = ap.parse_args()
    cmd_lines(args) if args.cmd == "lines" else cmd_score(args)


if __name__ == "__main__":
    main()
