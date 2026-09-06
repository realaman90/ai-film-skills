#!/usr/bin/env python3
"""Score generated takes with Gemini and pick the best one per slot.

Rubric (1-10 each): authenticity (reads as real archival / real live-action), motion_quality (no morphing, extra limbs,
warping), era_fidelity (period-correct look and artefacts), usability (a clean 4-8 s stretch with one clear action, no
text glitches). Prints per-take scores with timestamped artefacts and the best in-point, writes picks.json.

Usage:
    source ~/config.env
    python scripts/pick_takes.py --slot "1920s print" takes/c1920_a.mp4 takes/c1920_b.mp4 \
                                 --slot "results meeting room" takes/results_a.mp4 --out picks.json
    python scripts/pick_takes.py --auto takes/           # one slot per filename stem before the last "_"

Lessons baked in: natural continuous motion beats "hold still" takes (frozen takes score lower); Omni pops phantom
figures after ~4 s, so the picker reports a best in-point and artefact times — use them to trim.
"""
import argparse, json, os, sys, glob, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_reference as ar

RUBRIC = """You are a documentary archive researcher and a commercials DoP. Judge this clip as a candidate for the "{slot}" plate in a launch film.
Score 1-10: authenticity (would a viewer believe this is real archival / real live-action footage?), motion_quality (natural human motion, no morphing, no extra limbs, no warping),
era_fidelity (period-correct look, film artefacts plausible for the era), usability (a clean 4-8 s stretch with one clear action, no text glitches).
List concrete artefacts with timestamps. Return ONLY JSON:
{{"authenticity":0,"motion_quality":0,"era_fidelity":0,"usability":0,"artefacts":[{{"t":0,"issue":""}}],"best_in_point":0.0,"verdict":""}}"""


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--slot", nargs="+", action="append", metavar=("NAME", "TAKE"), help='slot name followed by its candidate files (repeatable)')
    p.add_argument("--auto", default=None, help="directory of takes; slot = filename stem up to the last underscore")
    p.add_argument("--out", default="picks.json")
    p.add_argument("--model", default="gemini-3.8-flash")
    p.add_argument("--tmp", default=".pick_tmp")
    a = p.parse_args()
    slots = {}
    for s in a.slot or []:
        slots[s[0]] = s[1:]
    if a.auto:
        for f in sorted(glob.glob(os.path.join(a.auto, "*.mp4"))):
            stem = re.sub(r"_[^_]+$", "", os.path.splitext(os.path.basename(f))[0]); slots.setdefault(stem, []).append(f)
    if not slots:
        p.error("give --slot NAME take1.mp4 [take2.mp4 ...] or --auto DIR")
    client = ar.make_client(); os.makedirs(a.tmp, exist_ok=True); out = {}
    for slot, takes in slots.items():
        res_all = []
        for f in takes:
            if not os.path.exists(f):
                print("missing", f); continue
            part, _, _ = ar.video_part(client, f, 2, a.tmp)
            res, _ = ar.generate_json(client, a.model, [part, RUBRIC.format(slot=slot)], temperature=0.2)
            res["take"] = f; res["total"] = sum(res.get(k, 0) for k in ("authenticity", "motion_quality", "era_fidelity", "usability"))
            res_all.append(res)
            print(f"{slot:32s} {os.path.basename(f):22s} auth {res.get('authenticity')} motion {res.get('motion_quality')} era {res.get('era_fidelity')} use {res.get('usability')} | in {res.get('best_in_point')} | {res.get('verdict')}")
            for x in res.get("artefacts", []):
                print(f"      {x.get('t')}s {x.get('issue')}")
        if res_all:
            best = max(res_all, key=lambda r: r["total"]); out[slot] = {"best": best["take"], "in": best.get("best_in_point", 0), "all": res_all}
    json.dump(out, open(a.out, "w"), indent=2)
    print("\nPICKS:", {k: os.path.basename(v["best"]) for k, v in out.items()}, "→", a.out)


if __name__ == "__main__":
    main()
