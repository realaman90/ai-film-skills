#!/usr/bin/env python3
"""Analyze inspiration / reference videos (ads, promos, films) BEFORE generating anything.

Uses Gemini video understanding to produce a shot-by-shot breakdown, pacing stats, palette,
camera language, product/brand strategy, audio style and copy-paste-ready prompt blocks.
Multiple references are fused into one "style DNA" creative brief for your target film.

Inputs: local files (.mp4/.mov/.webm), YouTube URLs (sent straight to Gemini, no download),
        or other http(s) URLs (downloaded with yt-dlp first).

Usage:
    source ~/config.env   # needs GEMINI_API_KEY

    # One reference ad
    python3 scripts/analyze_reference.py --input refs/chanel_25.mp4 --output refs/analysis

    # Several references + what you're making -> fused brief
    python3 scripts/analyze_reference.py \
        --input https://www.youtube.com/watch?v=XXXX \
        --input refs/competitor_promo.mp4 \
        --goal "30s vertical product promo for NORRA face serum, launch on Instagram Reels" \
        --brand "NORRA" \
        --output refs/analysis

    # Cheaper / faster: sample 0.5 fps, skip the ffmpeg contact sheet
    python3 scripts/analyze_reference.py --input ref.mp4 --output refs/analysis --sample-fps 0.5 --no-contact-sheet

Outputs (in --output dir):
    <name>.json          structured analysis (shots, pacing, palette, audio, structure, prompt_blocks)
    <name>.md            human-readable version of the same
    <name>_cuts.json     ffmpeg scene-change timestamps (local files only)
    <name>_contact.png   contact sheet of detected shots (local files only)
    brief.md             fused creative brief (when --goal given or >1 input)
    brief.json           machine-readable brief (style_lock, pacing_target, shot_plan, ...)
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time

DEFAULT_MODEL = "gemini-3.8-flash"
FALLBACK_MODELS = ["gemini-3.5-flash", "gemini-2.5-flash"]

ANALYSIS_PROMPT = """You are a senior commercial director and editor doing a forensic breakdown of a reference video
so an AI film pipeline can reproduce its craft (NOT its brand assets) for a different product.

Analyze the whole video. Be concrete and quantitative. Use timestamps in seconds.

Return ONLY JSON matching this schema:
{
  "meta": {"title_guess": str, "category": str, "duration_s": number, "aspect_ratio": str, "format_guess": "tv_spot|social_vertical|brand_film|product_demo|trailer|other"},
  "one_line_summary": str,
  "structure": [{"phase": "hook|setup|build|payoff|cta|other", "start": number, "end": number, "what_happens": str, "why_it_works": str}],
  "shots": [{"n": int, "start": number, "end": number, "duration": number,
             "shot_size": "ECU|CU|MCU|MS|MWS|WS|EWS|insert|macro",
             "camera": {"move": "static|push_in|pull_out|pan|tilt|dolly|track|orbit|handheld|crane|whip|rack_focus|zoom", "detail": str},
             "lens_feel": str, "subject": str, "action": str,
             "lighting": str, "color": str,
             "product_visible": bool, "product_frame_pct": number, "product_role": str,
             "text_on_screen": str, "transition_out": "cut|crossfade|match_cut|whip|dip|wipe|other",
             "ai_generation_risk": "low|medium|high", "risk_reason": str}],
  "pacing": {"shot_count": int, "avg_shot_len_s": number, "min_shot_len_s": number, "max_shot_len_s": number,
             "cuts_per_10s": number, "rhythm": str, "tempo_curve": str},
  "palette": {"dominant_hex": [str], "accent_hex": [str], "grade": str, "contrast": str, "saturation": str},
  "camera_language": {"vocabulary": [str], "rules": [str]},
  "product_strategy": {"first_reveal_s": number, "screen_time_pct": number, "framing_rules": [str], "hero_moment_s": number, "what_they_avoid": [str]},
  "talent": {"people_present": bool, "faces_in_closeup": bool, "how_used": str},
  "audio": {"music_style": str, "tempo_bpm_guess": number, "voiceover": str, "sfx": [str], "sync_notes": str, "silence_use": str},
  "typography_graphics": {"style": str, "when": [str], "animation": str, "end_card": str},
  "techniques": [str],
  "do_not_copy": [str],
  "prompt_blocks": {
    "STYLE_LOCK": "One paragraph, copy-paste into every image/video prompt: medium, lens feel, grade, light, texture, palette. No brand names.",
    "CAMERA_VOCAB": ["short camera directions in the video's language, one per line"],
    "PACING_TARGET": "e.g. 'Avg 2.4s per shot, hook in 1.5s, 12 cuts in 30s, slow 5s hero at 60%'",
    "AUDIO_DIRECTION": "music + sfx + vo direction as one paragraph, no artist names",
    "SHOT_TEMPLATE": [{"beat": str, "shot_size": str, "camera": str, "duration_s": number, "purpose": str}]
  }
}
Rules: shots must cover the full runtime with no gaps. Estimate hex colors honestly. Mark ai_generation_risk high for
fluid dynamics, fine logo/hardware close-ups, complex hand-object interaction, crowds, text in-scene, fast whole-body action."""

BRIEF_PROMPT = """You are a creative director fusing reference analyses into ONE production brief for an AI-generated film.

TARGET: {goal}
BRAND/PRODUCT: {brand}

Below are JSON analyses of {n} reference video(s). Extract the transferable craft (pacing, camera, light, structure,
audio, typography) and adapt it to the target. Never copy brand-specific assets, slogans, mascots or protected designs.

Return ONLY JSON:
{{
  "style_dna": str,
  "creative_direction": str,
  "target_spec": {{"duration_s": number, "aspect_ratio": str, "fps": 24, "platform": str}},
  "STYLE_LOCK": "copy-paste block for every image/video prompt (medium, lens, grade, light, palette, texture)",
  "PACING_TARGET": {{"avg_shot_len_s": number, "shot_count": int, "hook_by_s": number, "hero_moment_at_pct": number, "rhythm": str}},
  "CAMERA_VOCAB": [str],
  "AUDIO_DIRECTION": str,
  "TYPOGRAPHY": str,
  "shot_plan": [{{"n": int, "beat": "hook|setup|build|payoff|cta", "duration_s": number, "shot_size": str, "camera": str,
                  "subject_action": str, "light_color": str, "product_visible": bool,
                  "recommended_model": "omni|ltx|seedance|still_kenburns", "why_model": str,
                  "image_prompt_seed": str, "video_prompt_seed": str}}],
  "consistency_locks_needed": {{"characters": [str], "locations": [str], "props": [str]}},
  "risks_and_mitigations": [str],
  "do_not_copy": [str]
}}
Model routing hints: Seedance blocks photoreal faces (use it for products/3D/motion refs, or 2.5 with video refs);
Gemini Omni 1.1 Flash for hero shots with people, conversational edits and 360p drafts upscaled to 4K (3-10 s, extend to 40 s);
LTX 2.3/2.5 for cheap iteration, long takes, retakes; still + Ken Burns for zero-cost inserts. Stills come from GPT Image 2.

ANALYSES:
{analyses}"""


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def is_youtube(u):
    return bool(re.match(r"https?://(www\.)?(youtube\.com|youtu\.be)/", u))


def is_url(u):
    return u.startswith("http://") or u.startswith("https://")


def slug(s):
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    return s[:60] or "ref"


def find_ytdlp():
    for c in ("yt-dlp", os.path.expanduser("~/Library/Python/3.9/bin/yt-dlp"), os.path.expanduser("~/.local/bin/yt-dlp")):
        if shutil.which(c) or os.path.exists(c):
            return c
    return None


def download(url, out_dir):
    ytdlp = find_ytdlp()
    if not ytdlp:
        raise SystemExit("yt-dlp not found. Install: pip3 install --user yt-dlp (or pass a YouTube URL / local file)")
    os.makedirs(out_dir, exist_ok=True)
    tmpl = os.path.join(out_dir, "%(title).60s.%(ext)s")
    log(f"Downloading {url} ...")
    subprocess.run([ytdlp, "-q", "-f", "bv*[height<=1080]+ba/b[height<=1080]", "--merge-output-format", "mp4",
                    "-o", tmpl, url], check=True)
    files = sorted((os.path.join(out_dir, f) for f in os.listdir(out_dir) if f.endswith(".mp4")), key=os.path.getmtime)
    return files[-1]


def ffprobe_duration(path):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                             capture_output=True, text=True, check=True).stdout.strip()
        return float(out)
    except Exception:
        return None


def detect_cuts(path, threshold=0.3):
    """Return scene-change timestamps via ffmpeg's scene filter."""
    cmd = ["ffmpeg", "-hide_banner", "-i", path, "-vf", f"select='gt(scene,{threshold})',showinfo", "-an", "-f", "null", "-"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    times = [float(m) for m in re.findall(r"pts_time:([0-9.]+)", res.stderr)]
    return sorted(set(round(t, 2) for t in times))


def contact_sheet(path, cuts, out_png, cols=6, max_tiles=36):
    """Grab one frame just after each cut (plus t=0) and tile them."""
    points = [0.0] + [c + 0.15 for c in cuts]
    points = points[:max_tiles]
    n = len(points)
    if n == 0:
        return None
    select = "+".join(f"lt(prev_pt,{p})*gte(pt,{p})" for p in points)
    rows = (n + cols - 1) // cols
    vf = f"select='{select}',scale=320:-1,drawbox=0:0:0:0:color=black,tile={cols}x{rows}:margin=4:padding=4"
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", path, "-vf", vf, "-vsync", "vfr", "-frames:v", "1", out_png]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        # fallback: evenly spaced thumbnails
        dur = ffprobe_duration(path) or 30
        step = max(dur / max_tiles, 0.5)
        vf = f"fps=1/{step:.3f},scale=320:-1,tile={cols}x{rows}:margin=4:padding=4"
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", path, "-vf", vf, "-frames:v", "1", out_png])
    return out_png if os.path.exists(out_png) else None


def make_client():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY not set. Run: source ~/config.env")
    from google import genai
    return genai.Client(api_key=key)


def upload_video(client, path):
    log(f"Uploading {os.path.basename(path)} to Gemini Files API ...")
    f = client.files.upload(file=path)
    waited = 0
    while not f.state or f.state.name != "ACTIVE":
        if f.state and f.state.name == "FAILED":
            raise SystemExit(f"Gemini file processing failed for {path}")
        time.sleep(4)
        waited += 4
        f = client.files.get(name=f.name)
        if waited % 20 == 0:
            log(f"  processing... ({waited}s)")
    return f


def strip_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text


def generate_json(client, model, contents, temperature=0.2):
    from google.genai import types
    models = [model] + [m for m in FALLBACK_MODELS if m != model]
    last_err = None
    for m in models:
        try:
            resp = client.models.generate_content(
                model=m, contents=contents,
                config=types.GenerateContentConfig(response_mime_type="application/json", temperature=temperature),
            )
            return json.loads(strip_json(resp.text)), m
        except json.JSONDecodeError as e:
            last_err = f"{m}: bad JSON ({e})"
            log(f"  {last_err}; retrying once with same model")
            try:
                resp = client.models.generate_content(
                    model=m, contents=contents + ["Return valid JSON only."],
                    config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.1),
                )
                return json.loads(strip_json(resp.text)), m
            except Exception as e2:
                last_err = f"{m}: {e2}"
        except Exception as e:
            last_err = f"{m}: {e}"
            log(f"  model {m} failed: {e}")
    raise SystemExit(f"All models failed. Last error: {last_err}")


def video_part(client, src, sample_fps, work_dir):
    """Return (Part for Gemini, local_path_or_None, display_name)."""
    from google.genai import types
    meta = None
    if sample_fps:
        meta = types.VideoMetadata(fps=sample_fps)
    if is_youtube(src):
        part = types.Part(file_data=types.FileData(file_uri=src), video_metadata=meta) if meta else \
            types.Part(file_data=types.FileData(file_uri=src))
        return part, None, slug(src.rsplit("=", 1)[-1] if "=" in src else src.rsplit("/", 1)[-1])
    path = download(src, work_dir) if is_url(src) else src
    if not os.path.exists(path):
        raise SystemExit(f"Input not found: {path}")
    f = upload_video(client, path)
    part = types.Part(file_data=types.FileData(file_uri=f.uri, mime_type=f.mime_type), video_metadata=meta) if meta else \
        types.Part(file_data=types.FileData(file_uri=f.uri, mime_type=f.mime_type))
    return part, path, slug(os.path.splitext(os.path.basename(path))[0])


def analysis_to_md(a, name):
    L = [f"# Reference analysis — {name}", ""]
    m = a.get("meta", {})
    L.append(f"**{m.get('title_guess', '')}** · {m.get('category', '')} · {m.get('duration_s', '?')}s · {m.get('aspect_ratio', '?')} · {m.get('format_guess', '')}")
    L.append("")
    L.append(a.get("one_line_summary", ""))
    L.append("")
    L.append("## Structure")
    for s in a.get("structure", []):
        L.append(f"- **{s.get('phase')}** {s.get('start')}–{s.get('end')}s — {s.get('what_happens')} _(why: {s.get('why_it_works')})_")
    p = a.get("pacing", {})
    L += ["", "## Pacing",
          f"- {p.get('shot_count')} shots · avg {p.get('avg_shot_len_s')}s · min {p.get('min_shot_len_s')}s · max {p.get('max_shot_len_s')}s · {p.get('cuts_per_10s')} cuts/10s",
          f"- Rhythm: {p.get('rhythm')}", f"- Tempo curve: {p.get('tempo_curve')}"]
    L += ["", "## Shot list", "", "| # | t | dur | size | camera | subject / action | light / color | product | risk |", "|---|---|---|---|---|---|---|---|---|"]
    for s in a.get("shots", []):
        cam = s.get("camera", {})
        prod = f"{'✓' if s.get('product_visible') else '–'} {s.get('product_frame_pct', '')}%" if s.get("product_visible") else "–"
        L.append(f"| {s.get('n')} | {s.get('start')}–{s.get('end')} | {s.get('duration')} | {s.get('shot_size')} | {cam.get('move')}: {cam.get('detail', '')} | "
                 f"{s.get('subject', '')} — {s.get('action', '')} | {s.get('lighting', '')} / {s.get('color', '')} | {prod} | {s.get('ai_generation_risk')} |")
    pal = a.get("palette", {})
    L += ["", "## Palette & grade", f"- Dominant: {', '.join(pal.get('dominant_hex', []))} · Accent: {', '.join(pal.get('accent_hex', []))}",
          f"- Grade: {pal.get('grade')} · Contrast: {pal.get('contrast')} · Saturation: {pal.get('saturation')}"]
    cl = a.get("camera_language", {})
    L += ["", "## Camera language", "- Vocabulary: " + ", ".join(cl.get("vocabulary", []))]
    L += [f"- {r}" for r in cl.get("rules", [])]
    ps = a.get("product_strategy", {})
    L += ["", "## Product strategy", f"- First reveal at {ps.get('first_reveal_s')}s · screen time {ps.get('screen_time_pct')}% · hero moment {ps.get('hero_moment_s')}s"]
    L += [f"- Rule: {r}" for r in ps.get("framing_rules", [])]
    L += [f"- Avoids: {r}" for r in ps.get("what_they_avoid", [])]
    au = a.get("audio", {})
    L += ["", "## Audio", f"- Music: {au.get('music_style')} (~{au.get('tempo_bpm_guess')} bpm)", f"- VO: {au.get('voiceover')}",
          f"- SFX: {', '.join(au.get('sfx', []))}", f"- Sync: {au.get('sync_notes')} · Silence: {au.get('silence_use')}"]
    tg = a.get("typography_graphics", {})
    L += ["", "## Typography / graphics", f"- {tg.get('style')} · when: {', '.join(tg.get('when', []))} · anim: {tg.get('animation')} · end card: {tg.get('end_card')}"]
    L += ["", "## Techniques worth stealing"] + [f"- {t}" for t in a.get("techniques", [])]
    L += ["", "## Do NOT copy (brand-specific)"] + [f"- {t}" for t in a.get("do_not_copy", [])]
    pb = a.get("prompt_blocks", {})
    L += ["", "## Prompt blocks (copy-paste)", "", "### STYLE_LOCK", "```", pb.get("STYLE_LOCK", ""), "```",
          "", "### CAMERA_VOCAB", "```"] + list(pb.get("CAMERA_VOCAB", [])) + ["```",
          "", "### PACING_TARGET", "```", pb.get("PACING_TARGET", ""), "```",
          "", "### AUDIO_DIRECTION", "```", pb.get("AUDIO_DIRECTION", ""), "```",
          "", "### SHOT_TEMPLATE", "", "| beat | size | camera | dur | purpose |", "|---|---|---|---|---|"]
    for s in pb.get("SHOT_TEMPLATE", []):
        L.append(f"| {s.get('beat')} | {s.get('shot_size')} | {s.get('camera')} | {s.get('duration_s')} | {s.get('purpose')} |")
    return "\n".join(L) + "\n"


def brief_to_md(b, goal, brand, sources):
    L = [f"# Creative brief — {brand or 'untitled'}", "", f"**Goal:** {goal}", "", "**References:** " + ", ".join(sources), ""]
    L += ["## Style DNA", b.get("style_dna", ""), "", "## Creative direction", b.get("creative_direction", ""), ""]
    ts = b.get("target_spec", {})
    L += ["## Target spec", f"- {ts.get('duration_s')}s · {ts.get('aspect_ratio')} · {ts.get('fps')}fps · {ts.get('platform')}", ""]
    L += ["## STYLE_LOCK (paste into every image + video prompt)", "```", b.get("STYLE_LOCK", ""), "```", ""]
    pt = b.get("PACING_TARGET", {})
    L += ["## PACING_TARGET", f"- avg shot {pt.get('avg_shot_len_s')}s · {pt.get('shot_count')} shots · hook by {pt.get('hook_by_s')}s · hero at {pt.get('hero_moment_at_pct')}% · {pt.get('rhythm')}", ""]
    L += ["## CAMERA_VOCAB", "```"] + list(b.get("CAMERA_VOCAB", [])) + ["```", ""]
    L += ["## AUDIO_DIRECTION", b.get("AUDIO_DIRECTION", ""), "", "## TYPOGRAPHY", b.get("TYPOGRAPHY", ""), ""]
    L += ["## Shot plan", "", "| # | beat | dur | size | camera | subject / action | light / color | product | model | why |", "|---|---|---|---|---|---|---|---|---|---|"]
    for s in b.get("shot_plan", []):
        L.append(f"| {s.get('n')} | {s.get('beat')} | {s.get('duration_s')} | {s.get('shot_size')} | {s.get('camera')} | {s.get('subject_action')} | "
                 f"{s.get('light_color')} | {'✓' if s.get('product_visible') else '–'} | {s.get('recommended_model')} | {s.get('why_model')} |")
    L += ["", "### Prompt seeds per shot", ""]
    for s in b.get("shot_plan", []):
        L += [f"**Shot {s.get('n')} ({s.get('beat')})**", f"- image: {s.get('image_prompt_seed')}", f"- video: {s.get('video_prompt_seed')}", ""]
    cl = b.get("consistency_locks_needed", {})
    L += ["## Consistency locks to write (Step 1 of the pipeline)",
          "- Characters: " + ", ".join(cl.get("characters", [])) or "- Characters: none",
          "- Locations: " + ", ".join(cl.get("locations", [])), "- Props: " + ", ".join(cl.get("props", [])), ""]
    L += ["## Risks & mitigations"] + [f"- {r}" for r in b.get("risks_and_mitigations", [])]
    L += ["", "## Do NOT copy"] + [f"- {r}" for r in b.get("do_not_copy", [])]
    return "\n".join(L) + "\n"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", action="append", required=True, help="Local video, YouTube URL, or other video URL (repeatable)")
    p.add_argument("--output", required=True, help="Output directory")
    p.add_argument("--goal", default="", help="What you're making (duration, format, product, platform). Triggers brief.md")
    p.add_argument("--brand", default="", help="Brand/product name for the brief")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--sample-fps", type=float, default=None, help="Video sampling fps for Gemini (default 1; use 2 for fast-cut ads, 0.5 for long films)")
    p.add_argument("--no-contact-sheet", action="store_true")
    p.add_argument("--scene-threshold", type=float, default=0.3, help="ffmpeg scene-change threshold (0.2 sensitive .. 0.5 strict)")
    p.add_argument("--extra", default="", help="Extra instructions appended to the analysis prompt")
    p.add_argument("--skip-existing", action="store_true", help="Reuse <name>.json if present")
    args = p.parse_args()

    os.makedirs(args.output, exist_ok=True)
    work = os.path.join(args.output, "_downloads")
    client = make_client()

    analyses, names = [], []
    for src in args.input:
        # name resolution (before upload for skip-existing)
        if is_youtube(src):
            name = slug(src.rsplit("=", 1)[-1] if "=" in src else src.rsplit("/", 1)[-1])
        elif is_url(src):
            name = None
        else:
            name = slug(os.path.splitext(os.path.basename(src))[0])
        json_path = os.path.join(args.output, f"{name}.json") if name else None
        if args.skip_existing and json_path and os.path.exists(json_path):
            log(f"Reusing {json_path}")
            with open(json_path) as f:
                analyses.append(json.load(f)); names.append(name)
            continue

        part, local_path, name = video_part(client, src, args.sample_fps, work)
        json_path = os.path.join(args.output, f"{name}.json")

        # objective measurements first (local files only)
        measured = {}
        if local_path and shutil.which("ffmpeg"):
            dur = ffprobe_duration(local_path)
            cuts = detect_cuts(local_path, args.scene_threshold)
            measured = {"duration_s": dur, "cut_times": cuts, "shot_count": len(cuts) + 1,
                        "avg_shot_len_s": round(dur / (len(cuts) + 1), 2) if dur else None}
            with open(os.path.join(args.output, f"{name}_cuts.json"), "w") as f:
                json.dump(measured, f, indent=2)
            log(f"ffmpeg: {measured['shot_count']} shots over {dur}s (avg {measured['avg_shot_len_s']}s)")
            if not args.no_contact_sheet:
                sheet = contact_sheet(local_path, cuts, os.path.join(args.output, f"{name}_contact.png"))
                if sheet:
                    log(f"Contact sheet: {sheet}")

        prompt = ANALYSIS_PROMPT
        if measured.get("cut_times"):
            prompt += f"\n\nffmpeg measured these hard-cut timestamps (seconds), use them to anchor shot boundaries: {measured['cut_times'][:80]}"
        if args.extra:
            prompt += "\n\nAdditional instructions: " + args.extra

        log(f"Analyzing {name} with {args.model} ...")
        analysis, used = generate_json(client, args.model, [part, prompt])
        analysis["_source"] = src
        analysis["_model"] = used
        if measured:
            analysis["measured"] = measured
        with open(json_path, "w") as f:
            json.dump(analysis, f, indent=2)
        with open(os.path.join(args.output, f"{name}.md"), "w") as f:
            f.write(analysis_to_md(analysis, name))
        log(f"Wrote {json_path} and {name}.md")
        analyses.append(analysis); names.append(name)

    # fused brief
    if args.goal or len(analyses) > 1:
        goal = args.goal or "Same format and length as the references, for a different product."
        compact = []
        for a, n in zip(analyses, names):
            a2 = {k: v for k, v in a.items() if k not in ("measured",)}
            compact.append(f"### {n}\n" + json.dumps(a2, ensure_ascii=False))
        prompt = BRIEF_PROMPT.format(goal=goal, brand=args.brand or "(unnamed)", n=len(analyses), analyses="\n\n".join(compact))
        log("Fusing references into brief ...")
        brief, used = generate_json(client, args.model, [prompt], temperature=0.4)
        brief["_sources"] = names
        brief["_goal"] = goal
        with open(os.path.join(args.output, "brief.json"), "w") as f:
            json.dump(brief, f, indent=2)
        with open(os.path.join(args.output, "brief.md"), "w") as f:
            f.write(brief_to_md(brief, goal, args.brand, names))
        log(f"Wrote {os.path.join(args.output, 'brief.md')}")

    # stdout summary
    print(json.dumps({
        "outputs": sorted(os.listdir(args.output)),
        "references": [{"name": n, "shots": a.get("pacing", {}).get("shot_count"),
                        "avg_shot_len_s": a.get("pacing", {}).get("avg_shot_len_s"),
                        "duration_s": a.get("meta", {}).get("duration_s")} for a, n in zip(analyses, names)],
        "brief": os.path.join(args.output, "brief.md") if (args.goal or len(analyses) > 1) else None,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
