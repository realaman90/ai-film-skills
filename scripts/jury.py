#!/usr/bin/env python3
"""Gemini "jury of three" quality gate for a cut — BLIND by default.

Blind = the jury never sees previous scores. Feeding it its own history makes it anchor (we watched it return 7/10 for
six rounds while calling every fix "improved"). Use --anchored only to ask "what changed since the last cut?".

Scale is explicit: 10 = best-in-class launch film from a top studio, 8 = strong professional work a founder would
proudly ship, 6 = competent but generic, 4 = amateur. Run twice (--runs 2) to see the noise band.

Usage:
    source ~/config.env
    python scripts/jury.py renders/cut_v5.mp4 --brief "50 s launch film for X, an AI operator for B2B marketing" --runs 2 --out refs/jury_v5.json
    python scripts/jury.py renders/cut_v6.mp4 --brief "..." --anchored refs/jury_v5.json --changes "replaced the era plates, new end card"
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_reference as ar

DIMS = ["story", "footage_quality", "editing_rhythm", "motion_design", "sound_and_vo", "product_clarity", "b2b_persuasion", "overall"]
BLIND = """You are a jury of three: a commercial director, a brand strategist and a senior motion designer. You are watching: {brief}.
Score it 1-10 on: {dims} — where 10 = best-in-class launch film from a top studio, 8 = strong professional work a founder would proudly ship,
6 = competent but generic, 4 = amateur. Judge only what you see and hear. Be exact and honest; do not default to the middle.
Return ONLY JSON: {{"scores": {{{score_keys}}}, "strongest": [str], "weakest": [{{"t": number, "issue": str, "fix": str, "needs_new_footage": true}}], "ship": "yes|no", "verdict": str}}"""
ANCHORED = """You are the same jury of three. Your previous scores were {prev}. Since then the editor {changes}.
Re-score {dims} 1-10 with the same strictness and say what would move each dimension by one point.
Return ONLY JSON: {{"scores": {{{score_keys}}}, "improved": [str], "to_improve": [{{"priority": 1, "t": number, "dimension": str, "issue": str, "fix": str, "effort": "small|medium|large", "needs_new_footage": true}}], "verdict": str}}"""


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video"); p.add_argument("--brief", required=True, help="what the film is (one sentence)")
    p.add_argument("--runs", type=int, default=1); p.add_argument("--anchored", default=None, help="previous jury json to anchor on")
    p.add_argument("--changes", default="made changes"); p.add_argument("--dims", default=",".join(DIMS))
    p.add_argument("--model", default="gemini-3.8-flash"); p.add_argument("--out", default=None); p.add_argument("--tmp", default=".jury_tmp")
    a = p.parse_args()
    dims = [d.strip() for d in a.dims.split(",")]; score_keys = ", ".join(f'"{d}":0' for d in dims)
    client = ar.make_client(); os.makedirs(a.tmp, exist_ok=True)
    part, _, _ = ar.video_part(client, a.video, 2, a.tmp)
    if a.anchored:
        prev = json.load(open(a.anchored)); prev = prev[0] if isinstance(prev, list) else prev
        prompt = ANCHORED.format(prev=json.dumps(prev.get("scores")), changes=a.changes, dims=", ".join(dims), score_keys=score_keys)
    else:
        prompt = BLIND.format(brief=a.brief, dims=", ".join(dims), score_keys=score_keys)
    runs = []
    for k in range(a.runs):
        res, _ = ar.generate_json(client, a.model, [part, prompt], temperature=0.4 if not a.anchored else 0.3); runs.append(res)
        print(f"run {k + 1}:", res.get("scores"), "| ship:", res.get("ship", "-"))
        for w in res.get("weakest", []) or res.get("to_improve", []):
            print(f"   {w.get('t')}s [{'FOOTAGE' if w.get('needs_new_footage') else 'edit'}] {w.get('issue')} -> {w.get('fix')}")
    print("verdict:", runs[0].get("verdict"))
    if a.runs > 1:
        avg = {d: round(sum(float(r["scores"].get(d, 0)) for r in runs) / len(runs), 1) for d in dims}; print("mean:", avg)
    out = a.out or os.path.splitext(a.video)[0] + ("_jury_anchored.json" if a.anchored else "_jury.json")
    json.dump(runs if a.runs > 1 else runs[0], open(out, "w"), indent=2); print("→", out)


if __name__ == "__main__":
    main()
