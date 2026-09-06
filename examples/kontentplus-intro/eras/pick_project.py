"""Gemini picks, per era, which Omni take reads most like real archival / real live-action footage.
Usage: source ~/config.env && python3 eras/real/pick.py
Writes eras/real/picks.json and prints the winners."""
import sys, json, os
sys.path.insert(0, os.path.expanduser('~/.claude/skills/ai-film-studio/scripts'))
import analyze_reference as ar

P = os.path.expanduser('<project>')
client = ar.make_client()
ERAS = {
    "1900s market": ("c1900_a", "c1900_b"), "1920s print": ("c1920_a", "c1920_b"), "1960s agencies": ("c1960_a", "c1960_b"),
    "1990s direct mail": ("c1990_a", "c1990_b"), "2010s platforms A (over the shoulder)": ("c2010_a",), "2010s platforms B (front-on)": ("c2010_b",),
    "results meeting room": ("results_a",),
}
RUBRIC = """You are a documentary archive researcher and a commercials DoP. Judge this clip as a candidate for a {era} plate in a launch film.
Score 1-10: authenticity (would a viewer believe this is real archival / real live-action footage?), motion_quality (natural human motion, no morphing, no extra limbs, no warping),
era_fidelity (period-correct look, film artefacts plausible for the era), usability (a clean 4-8 s stretch with a clear action, no text glitches).
List concrete artefacts with timestamps. Return ONLY JSON: {{"authenticity":0,"motion_quality":0,"era_fidelity":0,"usability":0,"artefacts":[{{"t":0,"issue":""}}],"best_in_point":0.0,"verdict":""}}"""
import re
ONLY = [t for t in os.environ.get("TAKES", "").split(",") if t]
if ONLY:
    ERAS = {f"take {t}": (t,) for t in ONLY}
out = {}
for era, takes in ERAS.items():
    res_all = []
    for t in takes:
        f = f'{P}/eras/real/{t}.mp4'
        if not os.path.exists(f):
            print("missing", f); continue
        part, _, _ = ar.video_part(client, f, 2, f'{P}/refs/_downloads')
        res, _ = ar.generate_json(client, 'gemini-3.8-flash', [part, RUBRIC.format(era=era)], temperature=0.2)
        res["take"] = t; res["total"] = sum(res.get(k, 0) for k in ("authenticity", "motion_quality", "era_fidelity", "usability"))
        res_all.append(res)
        print(f"{era:38s} {t}: auth {res.get('authenticity')} motion {res.get('motion_quality')} era {res.get('era_fidelity')} use {res.get('usability')} | in {res.get('best_in_point')} | {res.get('verdict')}")
        for a in res.get("artefacts", []): print(f"      {a.get('t')}s {a.get('issue')}")
    if res_all:
        best = max(res_all, key=lambda r: r["total"]); out[era] = {"best": best["take"], "in": best.get("best_in_point", 0), "all": res_all}
json.dump(out, open(f'{P}/eras/real/picks' + ('_' + '_'.join(ONLY) if ONLY else '') + '.json', 'w'), indent=2)
print("\nPICKS:", {k: v["best"] for k, v in out.items()})
