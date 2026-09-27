#!/usr/bin/env python3
"""Generate a SONG WITH LYRICS from a composition plan (ElevenLabs Music v2.5).

generate_music.py is instrumental-only (force_instrumental). Use this when the words
must be sung: a lyric video, a jingle, a spoken-word bridge.

Plan file (JSON): {"chunks": [{"text": "[Verse 1]\nline one\nline two",
                               "duration_ms": 15200,
                               "positive_styles": [...], "negative_styles": [...],
                               "context_adherence": "high"}, ...]}
  - one chunk per song section; duration_ms = bars × 4 × 60000 / BPM (126 BPM → 1905 ms/bar)
  - lyrics go in "text" (\n between lines); {braces} = performance cues, e.g.
    "{instrumental intro}", "{spoken, deadpan}", "{ends abruptly on the last word}"
  - the FIRST chunk's styles set the whole song's tone; no artist names (TOS)

Usage (after `source ~/config.env`):
  python3 scripts/generate_song.py --plan audio/song_plan.json --out audio/song_take1 --seed 11
  python3 scripts/generate_song.py --plan audio/song_plan.json --out audio/song_take2 --seed 42

Writes <out>.mp3 and <out>.json (composition plan, song metadata and `words_timestamps`
— word-level timing of the sung lyrics). Score takes with song_lyrics.py. The key is read
from ELEVENLABS_KEY and never written anywhere.
"""
import argparse
import json
import os
import sys

import requests

API = "https://api.elevenlabs.io/v1/music/detailed"


def split_multipart(body: bytes, content_type: str) -> list[tuple[dict, bytes]]:
    """Split a multipart/mixed body into (headers, payload) parts."""
    boundary = None
    for piece in content_type.split(";"):
        piece = piece.strip()
        if piece.lower().startswith("boundary="):
            boundary = piece.split("=", 1)[1].strip('"')
    if not boundary:
        raise ValueError(f"no boundary in content type: {content_type}")
    delim = b"--" + boundary.encode()
    parts = []
    for raw in body.split(delim):
        raw = raw.strip(b"\r\n")
        if not raw or raw == b"--":
            continue
        head, _, payload = raw.partition(b"\r\n\r\n")
        headers = {}
        for line in head.decode("latin-1").split("\r\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip().lower()] = v.strip()
        parts.append((headers, payload.rstrip(b"\r\n")))
    return parts


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out", required=True, help="output path without extension")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--model", default="music_v2_5")
    args = ap.parse_args()

    key = os.environ.get("ELEVENLABS_KEY")
    if not key:
        sys.exit("ELEVENLABS_KEY is not set — run `source ~/config.env` first")

    with open(args.plan) as f:
        plan = json.load(f)
    body = {
        "composition_plan": {"chunks": plan["chunks"]},
        "model_id": args.model,
        "with_timestamps": True,
        "output_format": "mp3_44100_192",
    }
    if args.seed is not None:
        body["seed"] = args.seed

    try:
        resp = requests.post(
            API,
            headers={"xi-api-key": key, "Content-Type": "application/json"},
            json=body,
            timeout=600,
        )
    except requests.RequestException as err:
        sys.exit(f"request failed: {err}")
    if resp.status_code != 200:
        sys.exit(f"ERROR {resp.status_code}: {resp.text[:500]}")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    ctype = resp.headers.get("content-type", "")
    audio, meta = None, None
    if ctype.startswith("multipart/"):
        for headers, payload in split_multipart(resp.content, ctype):
            part_type = headers.get("content-type", "")
            if "json" in part_type:
                meta = json.loads(payload.decode("utf-8"))
            elif part_type.startswith("audio/") or "octet-stream" in part_type:
                audio = payload
    elif ctype.startswith("audio/"):
        audio = resp.content
    else:
        sys.exit(f"unexpected content type {ctype}: {resp.content[:300]!r}")

    if audio is None:
        sys.exit("no audio part in the response")
    with open(args.out + ".mp3", "wb") as f:
        f.write(audio)
    with open(args.out + ".json", "w") as f:
        json.dump(meta or {}, f, indent=2)
    print(f"SAVED {args.out}.mp3 ({len(audio) / 1024 / 1024:.1f} MB), metadata keys: {sorted((meta or {}).keys())}")


if __name__ == "__main__":
    main()
