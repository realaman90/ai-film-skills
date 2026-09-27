#!/usr/bin/env python3
"""Estimate generation spend for a project from what is on disk.

Counts Omni sidecars (<clip>.mp4.json → resolution × seconds), FLUX 3 sidecars (settled credits, else mode/resolution × seconds), Seedance/LTX clips (mp4 without an Omni sidecar, by
folder), GPT Image / Seedream / Nano Banana stills (png count, quality guessed from sidecar or filename), ElevenLabs
files and Gemini analysis JSONs, then prices them with the list rates below. Prices are approximate — check the
provider dashboards for the exact bill. Update RATES when prices change.

Usage: python scripts/cost_report.py /path/to/project [--seedance-dirs eras,clips] [--image-quality medium] [--image-model gpt-image-2]
"""
import argparse, glob, json, os, re, subprocess
from collections import Counter

RATES = {
    "omni_per_s": {"360p": 0.03, "720p": 0.10, "1080p": 0.15, "4k": 0.30},   # Gemini Omni 1.1 Flash, Sept 2026
    "seedance_per_s": 0.21,                                                 # Seedance 2.5 720p (≈ $1.50 per 7 s take)
    "ltx_per_s": 0.06,                                                      # LTX 2.5 fast
    "flux_per_s": {"draft": 0.06, "hd": 0.17, "fhd": 0.29, "v2v_draft": 0.12, "v2v_hd": 0.43, "v2v_fhd": 0.54},  # FLUX 3 Video, Sept 2026; settled credits win when present
    "gpt_image": {"gpt-image-2.5": {"low": 0.006, "medium": 0.015, "high": 0.035},   # Sunburst (default) at 1K, measured 2026-09-11
                  "gpt-image-2": {"low": 0.016, "medium": 0.063, "high": 0.25}},     # stills made before v2.3, or runs that fell back
    "gemini_video_call": 0.02,                                              # 3.8 Flash on a ≤60 s clip
    "elevenlabs_tts_1k_chars": 0.30, "elevenlabs_music_track": 0.50, "elevenlabs_sfx": 0.05,
}
SKIP = re.compile(r"renders/|/frames/|contact|_sheet|assets/ui|assets/images|/hd/|_prev|node_modules")


def dur(p):
    try:
        return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip() or 0)
    except Exception:
        return 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project"); ap.add_argument("--seedance-dirs", default="eras,clips", help="folders whose sidecar-less mp4s are Seedance takes")
    ap.add_argument("--ltx-dirs", default=""); ap.add_argument("--image-quality", default="medium", help="assumed quality when a still has no sidecar")
    ap.add_argument("--image-model", default="gpt-image-2.5", choices=sorted(RATES["gpt_image"]),
                    help="price stills at this model's rates (gpt-image-2 for projects made before v2.3 or runs that fell back)")
    a = ap.parse_args(); P = a.project; total = 0.0; lines = []
    # Omni (+ FLUX 3 sidecars, which carry provider=flux3)
    by = {}; flux_n = 0; flux_s = 0.0; flux_cost = 0.0
    for j in glob.glob(f"{P}/**/*.mp4.json", recursive=True):
        try:
            m = json.load(open(j))
        except Exception:
            continue
        if m.get("provider") == "flux3":
            mp4 = j[:-5]; d = m.get("output_duration_s") or (dur(mp4) if os.path.exists(mp4) else 0.0) or 0.0
            cr = m.get("cost_credits")
            if isinstance(cr, (int, float)):
                c = cr / 100.0
            else:
                key = ("v2v_" if m.get("mode") == "v2v" else "") + ("draft" if m.get("draft") else (m.get("resolution") or "hd"))
                c = d * RATES["flux_per_s"].get(key, 0.17)
            flux_n += 1; flux_s += d; flux_cost += c
            continue
        if "interaction_id" not in m:
            continue
        mp4 = j[:-5]; d = dur(mp4) if os.path.exists(mp4) else 0.0; r = m.get("resolution", "720p")
        by.setdefault(r, [0, 0.0]); by[r][0] += 1; by[r][1] += d
    for r, (n, s) in by.items():
        c = s * RATES["omni_per_s"].get(r, 0.10); total += c; lines.append((f"Omni {r}", f"{n} clips · {s:.0f} s", c))
    if flux_n:
        total += flux_cost; lines.append(("FLUX 3", f"{flux_n} clips · {flux_s:.0f} s", flux_cost))
    # Seedance / LTX: mp4s without sidecars in the named folders
    for label, dirs, rate in (("Seedance", a.seedance_dirs, RATES["seedance_per_s"]), ("LTX", a.ltx_dirs, RATES["ltx_per_s"])):
        n = s = 0
        for d_ in [x for x in dirs.split(",") if x]:
            for f in glob.glob(f"{P}/{d_}/**/*.mp4", recursive=True):
                if SKIP.search(f) or os.path.exists(f + ".json"):
                    continue
                n += 1; s += dur(f)
        if n:
            c = s * rate; total += c; lines.append((label, f"{n} clips · {s:.0f} s", c))
    # stills
    q = Counter()
    for f in glob.glob(f"{P}/**/*.png", recursive=True):
        if SKIP.search(f) or re.search(r"logo|screenshot|hero|_debug|mockup", f):
            continue
        side = f + ".json"; qual = a.image_quality
        if os.path.exists(side):
            try:
                qual = json.load(open(side)).get("quality", qual)
            except Exception:
                pass
        q[qual] += 1
    for qual, n in q.items():
        rates = RATES["gpt_image"][a.image_model]
        note = "" if qual in rates else " — no measured rate, priced as high"
        c = n * rates.get(qual, rates["high"]); total += c; lines.append((f"Stills ({a.image_model}, {qual}{note})", f"{n} images", c))
    # audio
    tts = [f for f in glob.glob(f"{P}/audio/*.mp3") if not re.search(r"bgmusic|music|sfx|pulse|tick", f)]
    music = glob.glob(f"{P}/audio/*music*.mp3"); sfx = glob.glob(f"{P}/audio/sfx/*.mp3") + [f for f in glob.glob(f"{P}/audio/*.mp3") if re.search(r"sfx|tick|pulse|whoosh", f)]
    chars = sum(dur(f) * 15 for f in tts)   # ≈15 chars per second of speech
    c = chars / 1000 * RATES["elevenlabs_tts_1k_chars"] + len(music) * RATES["elevenlabs_music_track"] + len(sfx) * RATES["elevenlabs_sfx"]; total += c
    lines.append(("ElevenLabs", f"{len(tts)} VO files · {len(music)} music · {len(sfx)} sfx", c))
    # gemini analysis
    n = len([f for f in glob.glob(f"{P}/**/*.json", recursive=True) if re.search(r"jury|analysis|picks|path_to|blind|cut[A-Z]", f)])
    c = n * RATES["gemini_video_call"]; total += c; lines.append(("Gemini analysis", f"{n} calls", c))
    w = max(len(l[0]) for l in lines)
    for k, v, c in lines:
        print(f"{k:{w}s}  {v:34s} ${c:7.2f}")
    print(f"{'TOTAL (estimate)':{w}s}  {'':34s} ${total:7.2f}")


if __name__ == "__main__":
    main()
