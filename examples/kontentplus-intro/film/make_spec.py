"""v13 — the TIMELINE cut: eras as modules on one axis, narration B, jazz bed."""
import json, subprocess, os
P = '.'; C = 'assets/clips'; A = 'assets/audio'; U = 'assets/ui'
MUSIC = os.environ.get("MUSIC", "bgmusic_jazz_aligned.mp3")
PORTRAIT = os.environ.get("ASPECT") == "9:16"
FW, FH = (1080, 1920) if PORTRAIT else (1920, 1080)
OUT = os.environ.get("OUT_DIR", P)


def dur(p):
    try:
        return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{P}/{p}"], capture_output=True, text=True).stdout.strip() or 0)
    except Exception:
        return 0


def V(key, src, d, tin='cut', tdur=0.5, amb=0.35, **kw):
    x = {"key": key, "type": "video", "src": src, "duration": d, "transitionIn": tin, "transitionDuration": tdur}
    if amb: x.update({"clipAudio": True, "clipAudioVolume": amb})
    x.update(kw); return x


def UI(key, src, d, tin='blur', tdur=0.5):
    return {"key": key, "type": "image", "src": f"{U}/{src}", "duration": d, "kenBurns": False, "transitionIn": tin, "transitionDuration": tdur}


# era modules: crossfade 0.45 gives the overlap the push needs (overlays add the x-motion)
scenes = [
    V("era1900", f"{C}/broll_merchant1900.mp4", 4.0, amb=0.45),
    V("era1926", f"{C}/ref_1926.mp4", 3.2, "crossfade", 0.45, amb=0.45),
    V("era1960", f"{C}/broll_boardroom1960.mp4", 3.2, "crossfade", 0.45, amb=0.45),
    V("era1990", f"{C}/broll_mailroom1990.mp4", 3.0, "crossfade", 0.45, amb=0.45),
    V("era2010", f"{C}/broll_saasdesk2010.mp4", 4.0, "crossfade", 0.45, amb=0.45),
    V("era2010b", f"{C}/ref_2016b.mp4", 4.0, "crossfade", 0.45, amb=0.45),
    {"key": "pixel", "type": "title", "text": " ", "duration": 3.0, "transitionIn": "cut"},
    UI("app1", "hero1.png", 3.4, "blur", 0.6),
    {"key": "brain", "type": "title", "text": " ", "duration": 2.2, "transitionIn": "blur", "transitionDuration": 0.5},
    {"key": "ops", "type": "title", "text": " ", "duration": 6.0, "transitionIn": "blur", "transitionDuration": 0.5},
    UI("app4", "hero4.png", 3.6),
    V("cmo", f"{C}/scene_results.mp4", 3.9, "blur", 0.5),
    {"key": "end", "type": "end_card", "text": "Marketing operations, handled.", "duration": 7.5, "cta": "Let's talk", "transitionIn": "crossfade", "transitionDuration": 0.8},
]
maxlen = {}
for s in scenes:
    if s["type"] == "video":
        L = dur(s["src"]); maxlen[s["key"]] = round(L - s.get("mediaStart", 0) - 0.02, 2) if L > 0.5 else s["duration"]
    else:
        maxlen[s["key"]] = 99
anchors = [("01", "era1900", 0.2), ("02", "era1900", 2.3), ("03", "era1926", -0.05), ("04", "era1960", -0.05), ("05", "era1990", -0.05), ("06", "era2010", -0.05),
           ("07", "pixel", 0.5), ("08", "app1", 0.15), ("09", "ops", 0.15), ("10", "app4", 0.2), ("11", "cmo", 0.15), ("12", "end", 1.4)]
GAP = 0.25; tcur = 0.3; vo = []
for n, k, off in anchors:
    d = dur(f"{A}/vB_{n}.mp3"); vo.append({"n": n, "key": k, "off": off, "start": round(tcur, 2), "end": round(tcur + d, 2)}); tcur += d + GAP
first = {}
for v in vo: first.setdefault(v["key"], v)
t = 0; st = {}
for i, sc in enumerate(scenes):
    tin = sc.get("transitionIn", "cut") if i else "cut"; td = 0 if tin == "cut" else sc.get("transitionDuration", 0.5)
    a = 0 if i == 0 else max(0, t - td)
    nxt = scenes[i + 1]["key"] if i + 1 < len(scenes) else None
    if nxt and nxt in first:
        tdn = 0 if scenes[i + 1].get("transitionIn", "cut") == "cut" else scenes[i + 1].get("transitionDuration", 0.5)
        d = max(2.2, min(first[nxt]["start"] - first[nxt]["off"] + tdn - a, maxlen[sc["key"]]))
    else:
        d = min(sc["duration"], maxlen[sc["key"]])
    if sc["key"] == "end": d = max(7.5, vo[-1]["end"] + 1.6 - a)
    sc["duration"] = round(d, 2); st[sc["key"]] = (a, a + d); t = a + d
total = t
sfx = [{"src": f"{A}/vB_{v['n']}.mp3", "start": v["start"], "volume": 1.0} for v in vo]
fx = [("ui_tick.mp3", "app1", 1.25, 0.22), ("ui_tick.mp3", "brain", 1.0, 0.18), ("ui_tick.mp3", "ops", 1.5, 0.2), ("ui_tick.mp3", "ops", 2.3, 0.2), ("ui_tick.mp3", "ops", 3.3, 0.18), ("ui_tick.mp3", "ops", 4.4, 0.2), ("ui_tick.mp3", "ops", 5.6, 0.22), ("ui_tick.mp3", "app4", 1.1, 0.22)]
sfx += [{"src": f"{A}/{f}", "start": round(st[k][0] + off, 2), "volume": v} for f, k, off, v in fx]
spec = {"title": "KontentPlus — timeline cut", "fps": 24, "width": FW, "height": FH, "aspect": "9:16" if PORTRAIT else "16:9", "background": "#0b0f14", "titleBackground": "#0b0f14",
        "titleColor": "#ffffff", "transition": "cut", "transitionDuration": 0.5, "fadeIn": 0.5, "fadeOut": 0.0, "scenes": scenes,
        "audio": {"music": f"{A}/{MUSIC}", "musicVolume": 0.16, "musicFadeIn": 0.5, "musicFadeOut": 3.0, "sfx": sfx}}
json.dump(spec, open(f'{OUT}/scenes_v13.json', 'w'), indent=2)
json.dump({"turn": st["pixel"][0], "total": total, "starts": {k: [v[0], v[1]] for k, v in st.items()}, "vo": vo}, open(f'{OUT}/timing_v13.json', 'w'))
for k, (a, b) in st.items(): print(f"{k:10s} {a:5.1f}-{b:5.1f}")
print("total", round(total, 2), "| turn", round(st["pixel"][0], 2))
