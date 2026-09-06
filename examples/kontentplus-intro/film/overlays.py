#!/usr/bin/env python3
"""v13 overlay layer — THE TIMELINE DEVICE.
Era videos are masked into a module (clip-path inset, rounded) docked above a luminous axis with decade ticks.
Between eras the outgoing module pushes left and the incoming slides in from the right while the axis scrolls one tick.
At the turn the axis snaps blue and blooms; the pixel glyph locks in as the current marker. Product section breaks out full-frame.
Also: kinetic (+/−) cards riding under the module, pixel build, app moments, results chips, animated end card.
"""
import json, os, re

P = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUT_DIR", P)
PORTRAIT = os.environ.get("ASPECT") == "9:16"
FW, FH = (1080, 1920) if PORTRAIT else (1920, 1080)
HTML = f"{OUT}/index.html"
SPEC = json.load(open(f"{OUT}/scenes.json"))
T = json.load(open(f"{OUT}/timing.json"))
starts, ids = {}, {}
t = 0.0
for i, s in enumerate(SPEC["scenes"]):
    tin = s.get("transitionIn", "cut") if i else "cut"
    td = 0.0 if tin == "cut" else float(s.get("transitionDuration", 0.5))
    a = 0.0 if i == 0 else max(0.0, t - td)
    starts[s["key"]] = (a, float(s["duration"])); ids[s["key"]] = f"scene-{i + 1:02d}"; t = a + float(s["duration"])
TOTAL = t
VO = {v["n"]: v for v in T["vo"]}
FONT = '-apple-system, "Inter", system-ui, sans-serif'
K = 4 / 3; YO = -60; XO = 0
if PORTRAIT:
    K = 0.893; XO = -186; YO = 510   # UI plates (1440x900 css) placed as a card in the middle of the vertical frame


def fmt(x): return f"{x:.3f}".rstrip("0").rstrip(".")
def cx(x): return x * K + XO
def cy(y): return y * K + YO


html = open(HTML).read()
css, add, tl = [], [], []
CURSOR_SVG = ('<svg width="28" height="34" viewBox="0 0 28 34"><path d="M2 2 L2 26 L8.5 20.5 L13 31 L17.5 29 L13 18.5 L22 18.5 Z" fill="#fff" stroke="#141f29" stroke-width="2" stroke-linejoin="round"/></svg>')


def inject_into_image_scene(key, inner_html):
    global html
    sid = ids[key]
    pat = re.compile(rf'(<div id="{sid}" class="clip scene-img"[^>]*>)(<img id="{sid}-img"[^>]*/>)(</div>)')
    mo = pat.search(html)
    if not mo:
        raise SystemExit(f"scene {key} not found")
    html = html[:mo.start()] + mo.group(1) + mo.group(2) + inner_html + mo.group(3) + html[mo.end():]
    return sid


def cursor(sid, name, start, path, click_at=None):
    cid = f"{sid}-cur-{name}"; x0, y0 = cx(path[0][1]), cy(path[0][2])
    out = [f'<div id="{cid}" class="cursor" style="left:{x0:.0f}px;top:{y0:.0f}px">{CURSOR_SVG}</div>']
    tl.append(f'tl.fromTo("#{cid}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, {fmt(start + path[0][0])});')
    for (t0, x, y) in path[1:]:
        tl.append(f'tl.to("#{cid}", {{ x: {cx(x) - x0:.0f}, y: {cy(y) - y0:.0f}, duration: {fmt(t0)}, ease: "power2.inOut" }}, ">");')
    if click_at is not None:
        rid = f"{cid}-rip"; xr, yr = cx(path[-1][1]) + 4, cy(path[-1][2]) + 4
        out.append(f'<div id="{rid}" class="ripple" style="left:{xr:.0f}px;top:{yr:.0f}px"></div>')
        tl.append(f'tl.fromTo("#{rid}", {{ opacity: 0.9, scale: 0.3 }}, {{ opacity: 0, scale: 1.4, duration: 0.45, ease: "power2.out" }}, {fmt(start + click_at)});')
    return "".join(out)


# ================= 1. THE TIMELINE: modules + axis + pushes
ERAS = [("era1900", "1900s", "MERCHANT"), ("era1926", "1920s", "PRINT"), ("era1960", "1960s", "MASS MEDIA"),
        ("era1990", "1990s", "DIRECT MAIL"), ("era2010", "2010s", "PLATFORMS"), ("era2010b", "2010s", "PLATFORMS")]
MOD_T, MOD_L, MOD_R = 96, 240, 240; MOD_BOT = 774
if PORTRAIT:
    MOD_T, MOD_L, MOD_R = 520, 60, 60; MOD_BOT = 1060
MOD_B = FH - MOD_BOT   # CSS bottom inset
AXIS_Y = MOD_BOT + 120 if PORTRAIT else 1080 - 96 - 120
axis_start, axis_end = starts["era1900"][0], starts["era2010b"][0] + starts["era2010b"][1]
css.append(f"""      .era-mod {{ clip-path: inset({MOD_T}px {MOD_R}px {MOD_B}px {MOD_L}px round 18px); }}
      {"video.era-mod { position: absolute; left: %dpx; top: %dpx; width: %dpx; height: %dpx; clip-path: inset(0 round 18px); }" % (MOD_L, MOD_T, FW - MOD_L - MOD_R, MOD_BOT - MOD_T) if PORTRAIT else ""}
      #{ids["era2010b"]} {{ filter: brightness(1) saturate(1); }}   /* identity base for the turn blowout */
      .mod-grain {{ position: absolute; left: {MOD_L}px; top: {MOD_T}px; width: {FW - MOD_L - MOD_R}px; height: {MOD_BOT - MOD_T}px; border-radius: 18px; pointer-events: none;
        background: radial-gradient(ellipse at center, rgba(0,0,0,0) 58%, rgba(0,0,0,0.42) 100%), repeating-radial-gradient(circle at 37% 41%, rgba(255,255,255,0.06) 0 1px, rgba(0,0,0,0) 1px 3px); mix-blend-mode: overlay; opacity: 0.9; }}
      .axis-wrap {{ position: absolute; inset: 0; pointer-events: none; }}
      .axis-line {{ position: absolute; left: 0; width: 100%; top: {AXIS_Y}px; height: 3px; background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.75) 12%, rgba(255,255,255,0.75) 88%, rgba(255,255,255,0) 100%); transform-origin: 0 50%; }}
      .axis-glow {{ position: absolute; left: 0; width: 100%; top: {AXIS_Y - 6}px; height: 15px; background: linear-gradient(90deg, rgba(5,109,245,0) 0%, rgba(5,109,245,0.9) 15%, rgba(5,109,245,0.9) 85%, rgba(5,109,245,0) 100%); filter: blur(6px); opacity: 0; }}
      .ticks {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; }}
      .tick {{ position: absolute; top: {AXIS_Y - 14}px; width: {FW}px; text-align: center; }}
      .tick i {{ display: block; width: 14px; height: 14px; border-radius: 50%; background: #fff; margin: 0 auto 14px; box-shadow: 0 0 0 6px rgba(255,255,255,0.12); }}
      .tick b {{ display: block; font: 700 34px/1 ui-monospace, Menlo, monospace; letter-spacing: .14em; color: #fff; text-shadow: 0 2px 12px rgba(0,0,0,0.6); }}
      .tick small {{ display: block; margin-top: 8px; font: 600 18px/1 ui-monospace, Menlo, monospace; letter-spacing: .22em; color: rgba(255,255,255,0.78); }}
      .mod-frame {{ position: absolute; left: {MOD_L}px; top: {MOD_T}px; width: {FW - MOD_L - MOD_R}px; height: {FH - MOD_T - MOD_B}px; border-radius: 18px; box-shadow: 0 0 0 1px rgba(255,255,255,0.14), 0 30px 80px rgba(0,0,0,0.55); pointer-events: none; }}
      .stem {{ position: absolute; left: 50%; width: 2px; margin-left: -1px; top: {FH - MOD_B}px; height: {AXIS_Y - (FH - MOD_B)}px; background: rgba(255,255,255,0.35); transform-origin: 50% 100%; }}""")
# mask every era video into the module and give it the push motion
tick_labels = []
seen = set()
for j, (key, decade, label) in enumerate(ERAS):
    sid = ids[key]
    html = html.replace(f'<video id="{sid}" class="clip"', f'<video id="{sid}" class="clip era-mod"', 1)
    if key not in seen and not (key == "era2010b"):
        seen.add(key)
n_ticks = 5
tick_keys = ["era1900", "era1926", "era1960", "era1990", "era2010"]
tick_html = "".join(f'<div class="tick" id="tick{i}" style="left:{i * FW}px"><i></i><b>{ERAS[i][1]}</b><small>{ERAS[i][2]}</small></div>' for i in range(n_ticks))
add.append(f'<div id="axis" class="clip axis-wrap" data-start="{fmt(axis_start)}" data-duration="{fmt(axis_end - axis_start)}" data-track-index="9" style="z-index:65">'
           f'<div class="mod-frame"></div><div class="mod-grain"></div><div id="stem" class="stem"></div><div id="axis-line" class="axis-line"></div><div id="axis-glow" class="axis-glow"></div><div id="ticks" class="ticks">{tick_html}</div></div>')
tl.append(f'tl.fromTo("#axis-line", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.9, ease: "power3.out" }}, {fmt(axis_start + 0.1)});')
tl.append(f'tl.fromTo("#stem", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.4, ease: "power2.out" }}, {fmt(axis_start + 0.7)});')
tl.append(f'tl.fromTo("#tick0", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power2.out" }}, {fmt(axis_start + 0.9)});')
for i in range(1, n_ticks):
    tl.append(f'tl.set("#tick{i}", {{ opacity: 1 }}, {fmt(axis_start)});')
# pushes: at each era boundary the outgoing module slides left, incoming slides in from the right, ticks scroll one screen
for j in range(1, len(ERAS)):
    key, prev = ERAS[j][0], ERAS[j - 1][0]
    s_k, d_k = starts[key]; dur_t = 0.45
    if key == "era2010b":   # same tick (2010s) — a gentle push, no tick scroll
        tl.append(f'tl.fromTo("#{ids[key]}", {{ x: 320, opacity: 0 }}, {{ x: 0, opacity: 1, duration: {fmt(dur_t)}, ease: "power3.out" }}, {fmt(s_k)});')
        tl.append(f'tl.to("#{ids[prev]}", {{ x: -320, duration: {fmt(dur_t)}, ease: "power3.in" }}, {fmt(s_k)});')
        continue
    tl.append(f'tl.to("#{ids[prev]}", {{ x: -{FW}, duration: {fmt(dur_t)}, ease: "power3.inOut" }}, {fmt(s_k)});')
    tl.append(f'tl.fromTo("#{ids[key]}", {{ x: {FW} }}, {{ x: 0, duration: {fmt(dur_t)}, ease: "power3.inOut" }}, {fmt(s_k)});')
    tl.append(f'tl.to("#ticks", {{ x: -{FW} * {j}, duration: {fmt(dur_t)}, ease: "power3.inOut" }}, {fmt(s_k)});')
    tl.append(f'tl.fromTo("#stem", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.3, ease: "power2.out" }}, {fmt(s_k + dur_t)});')
for key, _, _ in ERAS:
    s_k, d_k = starts[key]
    tl.append(f'tl.fromTo("#{ids[key]}", {{ scale: 1.0 }}, {{ scale: 1.05, duration: {fmt(d_k)}, ease: "none" }}, {fmt(s_k)});')
# the builder's crossfade tween on the incoming video (opacity 0→1) is fine underneath the push
# the turn: the axis snaps blue and blooms, then the pixel scene takes over
turn = starts["pixel"][0]
tl.append(f'tl.fromTo("#axis-glow", {{ opacity: 0, scaleY: 0.2 }}, {{ opacity: 1, scaleY: 1, duration: 0.35, ease: "power2.out" }}, {fmt(turn - 0.7)});')
tl.append(f'tl.to("#axis-glow", {{ scaleY: 40, opacity: 0, duration: 0.7, ease: "power3.in" }}, {fmt(turn - 0.35)});')
tl.append(f'tl.to("#{ids["era2010b"]}", {{ filter: "brightness(2.4) saturate(0.6)", duration: 0.5, ease: "power3.in" }}, {fmt(turn - 0.5)});')
add.append('<div id="turn-flash" data-layout-allow-overlap></div>')
css.append("      #turn-flash { position: absolute; inset: 0; background: #fff; opacity: 0; z-index: 30; pointer-events: none; }")
tl.append(f'tl.fromTo("#turn-flash", {{ opacity: 0 }}, {{ opacity: 0.9, duration: 0.12, ease: "power3.in" }}, {fmt(turn - 0.12)});')
tl.append(f'tl.to("#turn-flash", {{ opacity: 0, duration: 0.45, ease: "power2.out" }}, {fmt(turn)});')

# ================= 2. kinetic cards riding under the module (Vela-style, one per era line)
css.append(f"""      .kt {{ position: absolute; left: {MOD_L + 24}px; top: {FH - MOD_B - 92}px; opacity: 1; }}
      .kt .w {{ display: inline-block; padding: 10px 20px; margin-right: 10px; border-radius: 12px; background: rgba(255,255,255,0.96); color: #141f29; font: 800 46px/1.05 {FONT}; letter-spacing: -0.02em; box-shadow: 0 16px 50px rgba(0,0,0,0.45); opacity: 0; transform-origin: 0 100%; }}
      .kt .w.strike {{ text-decoration: line-through; text-decoration-color: #d93025; text-decoration-thickness: 6px; color: #6e6e76; }}
      .kt .w.blue {{ background: #056df5; color: #fff; }} .kt .w.navy {{ background: #141f29; color: #fff; }}
      .kt.full {{ left: 96px; top: auto; bottom: {384 if PORTRAIT else 110}px; }} .kt.full .w {{ font-size: 54px; }}""")
KT = [("era1900", "02", 0.8, [("by face", "")]), ("era1926", "03", 0.5, [("+ reach", ""), ("− faces", "strike")]),
      ("era1960", "04", 0.6, [("+ a demographic", ""), ("+ a guess", "navy")]), ("era1990", "05", 0.6, [("+ a zip code", ""), ("+ a landfill", "navy")]),
      ("era2010b", "06", 2.0, [("+ all the data", ""), ("− no time", "strike")]),
      ("app1", "08", 0.4, [("A brain of your own", "blue")]), 
      ("app4", "10", 0.4, [("Every edit", ""), ("makes it better.", "blue")]), ("cmo", "11", 1.3, [("Grow,", ""), ("don't juggle.", "blue")])]
for i, (key, line, delay, words) in enumerate(KT):
    s_k, d_k = starts[key]; t0 = max(s_k + 0.15, VO[line]["start"] + delay); end = s_k + d_k
    full = "" if key.startswith("era") else " full"
    inner = "".join(f'<span id="kt{i}w{j}" class="w {cls}" data-layout-allow-overlap>{w}</span>' for j, (w, cls) in enumerate(words))
    add.append(f'<div id="kt{i}" class="clip" data-start="{fmt(s_k)}" data-duration="{fmt(d_k)}" data-track-index="8" style="z-index:76"><div class="kt{full}" id="kt{i}-box">{inner}</div></div>')
    for j in range(len(words)):
        tl.append(f'tl.fromTo("#kt{i}w{j}", {{ opacity: 0, y: 26, rotation: -3, scale: 0.9 }}, {{ opacity: 1, y: 0, rotation: 0, scale: 1, duration: 0.32, ease: "back.out(2.2)" }}, {fmt(t0 + j * 0.28)});')
    tl.append(f'tl.to("#kt{i}-box", {{ opacity: 0, y: -12, duration: 0.3, ease: "power2.in" }}, {fmt(end - 0.45)});')

# ================= 3. pixel beat (the glyph locks onto the line as the "now" marker)
s_p, d_p = starts["pixel"]; pid = ids["pixel"]
pat = re.compile(rf'(<div id="{pid}" class="clip title-card"[^>]*>).*?(</div>\n)', re.S)
mo = pat.search(html)
if not mo:
    raise SystemExit("pixel scene not found")
CELL = 64; G0X = FW // 2 - 160; G0Y = FH // 2 - 160
order = [(1, 3), (0, 2), (1, 1), (2, 4), (2, 0), (3, 3), (3, 1), (4, 2)]
px_html = ('<div id="px-line"></div><div id="px-glow"></div>' + "".join(
    f'<div id="px{i}" class="px{" blue" if (r, c) == (1, 3) else ""}" style="left:{G0X + c * CELL}px;top:{G0Y + r * CELL}px"></div>' for i, (r, c) in enumerate(order))
    + f'<div id="px-kt" class="kt full" style="left:0;right:0;bottom:auto;top:{FH // 2 + 300 if PORTRAIT else FH // 2 + 220}px;text-align:center"><span id="pxw0" class="w navy" data-layout-allow-overlap>So we built</span><span id="pxw1" class="w blue" data-layout-allow-overlap>an operator.</span></div>')
html = html[:mo.start()] + (mo.group(1) + px_html + mo.group(2)) + html[mo.end():]
html = re.sub(rf'\n\s*tl\.fromTo\("#{pid}-h1".*?\);', '', html)
css.append(f"""      #{pid} {{ background: #0b0f14; }}
      #px-line {{ position: absolute; left: 0; width: 100%; top: {AXIS_Y}px; height: 3px; background: linear-gradient(90deg, rgba(5,109,245,0) 0%, #056df5 15%, #056df5 85%, rgba(5,109,245,0) 100%); box-shadow: 0 0 24px 4px rgba(5,109,245,0.6); opacity: 0; }}
      .px {{ position: absolute; width: {CELL - 6}px; height: {CELL - 6}px; margin: 3px; background: #fff; opacity: 0; transform-origin: center; }}
      .px.blue {{ background: #056df5; box-shadow: 0 0 24px 6px rgba(5,109,245,0.55); }}
      #px-glow {{ position: absolute; width: 520px; height: 520px; border-radius: 50%; left: {FW // 2 - 260}px; top: {FH // 2 - 260}px; background: radial-gradient(circle, rgba(5,109,245,0.45) 0%, rgba(5,109,245,0) 62%); opacity: 0; }}""")
tl.append(f'tl.fromTo("#px-line", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, {fmt(s_p)});')
tl.append(f'tl.fromTo("#px0", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.18, ease: "power2.out" }}, {fmt(s_p + 0.35)});')
tl.append(f'tl.to("#px0", {{ opacity: 0.15, duration: 0.1 }}, {fmt(s_p + 0.65)});')
tl.append(f'tl.to("#px0", {{ opacity: 1, scale: 1.25, duration: 0.18, ease: "back.out(2)" }}, {fmt(s_p + 0.82)});')
tl.append(f'tl.fromTo("#px-glow", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.5, ease: "power2.out" }}, {fmt(s_p + 0.82)});')
tl.append(f'tl.to("#px0", {{ scale: 1, duration: 0.25, ease: "power2.inOut" }}, {fmt(s_p + 1.05)});')
for i in range(1, 8):
    tl.append(f'tl.fromTo("#px{i}", {{ opacity: 0, scale: 0.2, rotation: 90 }}, {{ opacity: 1, scale: 1, rotation: 0, duration: 0.22, ease: "back.out(2.5)" }}, {fmt(s_p + 1.15 + (i - 1) * 0.1)});')
tl.append(f'tl.to("#px-glow", {{ scale: 1.5, opacity: 0.35, duration: 0.9, ease: "sine.inOut" }}, {fmt(s_p + 1.9)});')
t0 = max(s_p + 0.15, VO["07"]["start"] + 0.1)
for j in range(2):
    tl.append(f'tl.fromTo("#pxw{j}", {{ opacity: 0, y: 26, rotation: -3, scale: 0.9 }}, {{ opacity: 1, y: 0, rotation: 0, scale: 1, duration: 0.32, ease: "back.out(2.2)" }}, {fmt(t0 + j * 0.28)});')

# ================= 4. app moments (connect / tasks / edit) + cursor
css.append(f"""      .ui2 {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0; }}
      .cursor {{ position: absolute; width: 28px; height: 34px; opacity: 0; z-index: 5; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.35)); }}
      .ripple {{ position: absolute; width: 44px; height: 44px; margin: -22px 0 0 -22px; border-radius: 50%; border: 3px solid #056df5; opacity: 0; z-index: 4; }}
      .hl {{ position: absolute; border: 3px solid #056df5; border-radius: 12px; box-shadow: 0 0 0 6px rgba(5,109,245,0.18); opacity: 0; z-index: 3; }}
      .uichip {{ position: absolute; padding: 14px 24px; border-radius: 999px; background: #141f29; color: #fff; font: 600 26px/1 {FONT}; border: 2px solid rgba(255,255,255,0.25); display: flex; gap: 10px; align-items: center; opacity: 0; box-shadow: 0 12px 40px rgba(0,0,0,0.25); z-index: 6; }}
      .uichip b {{ width: 11px; height: 11px; border-radius: 50%; background: #056df5; display: inline-block; box-shadow: 0 0 14px #056df5; }}
      .uichip.ok b {{ background: #2e9e6b; box-shadow: 0 0 14px #2e9e6b; }}
      .toast {{ position: absolute; right: 90px; top: 110px; width: 520px; padding: 16px 18px; border-radius: 14px; background: #fff; border: 1px solid #ececee; color: #1a1a1e; font-family: {FONT}; box-shadow: 0 16px 40px rgba(0,0,0,0.18); opacity: 0; z-index: 6; }}
      .toast .k {{ font: 600 12px/1 ui-monospace, Menlo, monospace; letter-spacing: .06em; color: #2e9e6b; }} .toast .t {{ font-size: 20px; margin-top: 6px; }} .toast .s {{ font-size: 15px; color: #6e6e76; margin-top: 2px; }}""")
def plate(sid):
    if PORTRAIT:
        css.append(f"#{sid} {{ background: #0b0f14; }} #{sid} img {{ position: absolute; left: {XO}px; top: {YO}px; width: {1440 * K:.0f}px; height: {900 * K:.0f}px; object-fit: fill; }}")
s1, d1 = starts["app1"]; sid = ids["app1"]
plate(sid)
inner = (cursor(sid, "a", s1, [(0.3, 700, 560), (0.8, 540, 306)], click_at=1.15)
         + f'<div id="{sid}-hl" class="hl" style="left:{cx(295):.0f}px;top:{cy(295):.0f}px;width:{cx(1082):.0f}px;height:{cy(59) - YO:.0f}px"></div>'
         + f'<div id="{sid}-chip" class="uichip" style="left:50%;bottom:190px;transform:translateX(-50%)"><b></b>48 files read · decks, sheets, transcripts, CRM</div>')
inject_into_image_scene("app1", inner)
tl.append(f'tl.fromTo("#{sid}-hl", {{ opacity: 0, scale: 1.04 }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: "power2.out" }}, {fmt(s1 + 1.15)});')
tl.append(f'tl.to("#{sid}-hl", {{ opacity: 0, duration: 0.3 }}, {fmt(s1 + 2.2)});')
tl.append(f'tl.fromTo("#{sid}-chip", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, {fmt(s1 + 2.0)});')
css.append(f"#{sid} {{ transform-origin: 40% 42%; }}")
tl.append(f'tl.fromTo("#{sid}", {{ scale: 1.0 }}, {{ scale: 1.22, duration: {fmt(d1)}, ease: "power1.inOut" }}, {fmt(s1)});')

# ================= 4a. BRAIN beat — files fly into the mark, a memory ring forms ("never forgets")
sb, db = starts["brain"]; bid = ids["brain"]
_i8 = _chars0 = None
_Wc = json.load(open(f"{P}/../audio/voB_words.json")); _c = "".join(_Wc["characters"]); _s = _Wc["character_start_times_seconds"]
_i8 = _c.find("KontentPlus learns"); tNF = VO["08"]["start"] + (_s[_c.find("never forgets", _i8)] - _s[_i8])
pat = re.compile(rf'(<div id="{bid}" class="clip title-card"[^>]*>).*?(</div>\n)', re.S)
mo = pat.search(html)
if not mo:
    raise SystemExit("brain scene not found")
import math
NODES = ["Brand voice", "ICP", "Q4 goals", "Customers", "Pricing", "Last quarter"]
RX, RY = (400, 520) if PORTRAIT else (470, 300)
node_pos = [(FW / 2 + RX * math.cos(math.radians(-90 + k * 60)), FH / 2 + RY * math.sin(math.radians(-90 + k * 60))) for k in range(6)]
FILES = [("deck_q4.pdf", 140, 200), ("interviews.docx", 220, 760), ("numbers.xlsx", 1600, 220), ("brand_guide.pdf", 1560, 800), ("crm_export.csv", 900, 940)]
FILES = [(n, int(x * FW / 1920), int(y * FH / 1080)) for n, x, y in FILES]
svg = f'<svg id="br-svg" viewBox="0 0 {FW} {FH}" width="{FW}" height="{FH}">' + "".join(
    f'<line id="br-l{k}" x1="{FW / 2:.0f}" y1="{FH / 2:.0f}" x2="{x:.0f}" y2="{y:.0f}" stroke="rgba(5,109,245,0.8)" stroke-width="3" stroke-dasharray="600" stroke-dashoffset="600"/>' for k, (x, y) in enumerate(node_pos)) + '</svg>'
nodes = "".join(f'<div id="br-n{k}" class="brnode" style="left:{x:.0f}px;top:{y:.0f}px" data-layout-allow-overlap>{n}</div>' for k, ((x, y), n) in enumerate(zip(node_pos, NODES)))
files = "".join(f'<div id="br-f{k}" class="brfile" style="left:{x}px;top:{y}px" data-layout-allow-overlap><i></i>{n}</div>' for k, (n, x, y) in enumerate(FILES))
br_html = ('<div id="br-glow"></div><div id="br-stage" data-layout-allow-overflow>' + svg + nodes + '</div>' + files + '<img id="br-mark" src="assets/images/logo-mark-white.png" alt="" data-layout-allow-overlap />'
           f'<div id="br-kt" class="kt full" style="left:0;right:0;bottom:auto;top:{FH // 2 - 600 if PORTRAIT else FH // 2 + 380}px;text-align:center"><span id="br-w0" class="w blue" data-layout-allow-overlap>never forgets.</span></div>')
html = html[:mo.start()] + (mo.group(1) + br_html + mo.group(2)) + html[mo.end():]
html = re.sub(rf'\n\s*tl\.fromTo\("#{bid}-h1".*?\);', '', html)
css.append(f"""      #{bid} {{ background: #0b0f14; overflow: hidden; font-family: {FONT}; text-align: left; }}
      #br-glow {{ position: absolute; width: 900px; height: 900px; border-radius: 50%; left: {FW // 2 - 450}px; top: {FH // 2 - 450}px; background: radial-gradient(circle, rgba(5,109,245,0.5) 0%, rgba(5,109,245,0) 60%); opacity: 0; }}
      #br-svg {{ position: absolute; left: 0; top: 0; }}
      #br-stage {{ position: absolute; inset: 0; transform-style: preserve-3d; perspective: 1400px; }}
      #br-mark {{ position: absolute; width: 176px; height: 176px; left: {FW // 2 - 88}px; top: {FH // 2 - 88}px; opacity: 0; filter: drop-shadow(0 0 30px rgba(5,109,245,0.6)); }}
      .brnode {{ position: absolute; transform: translate(-50%, -50%); padding: 16px 28px; border-radius: 999px; background: rgba(255,255,255,0.08); border: 1.5px solid rgba(255,255,255,0.35); color: #fff; font-size: 30px; font-weight: 600; opacity: 0; backdrop-filter: blur(6px); white-space: nowrap; }}
      .brfile {{ position: absolute; display: flex; gap: 12px; align-items: center; padding: 12px 20px; border-radius: 12px; background: #fff; color: #141f29; font: 500 22px/1 ui-monospace, Menlo, monospace; opacity: 0; box-shadow: 0 12px 40px rgba(0,0,0,0.4); }} .brfile i {{ width: 14px; height: 18px; border-radius: 3px; background: #056df5; }}
      #br-kt .w {{ font-size: 54px; }}""")
tl.append(f'tl.fromTo("#br-glow", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.6, ease: "power2.out" }}, {fmt(sb + 0.1)});')
tl.append(f'tl.fromTo("#br-mark", {{ opacity: 0, scale: 0.5, rotation: -8 }}, {{ opacity: 1, scale: 1, rotation: 0, duration: 0.5, ease: "back.out(1.6)" }}, {fmt(sb + 0.15)});')
for k, (n, x, y) in enumerate(FILES):
    tl.append(f'tl.fromTo("#br-f{k}", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "power2.out" }}, {fmt(sb + 0.05 + k * 0.06)});')
    tl.append(f'tl.to("#br-f{k}", {{ x: {FW / 2 - x - 90:.0f}, y: {FH / 2 - y - 20:.0f}, scale: 0.2, opacity: 0, duration: 0.55, ease: "power3.in" }}, {fmt(sb + 0.35 + k * 0.06)});')
tl.append(f'tl.to("#br-mark", {{ scale: 1.18, duration: 0.14, ease: "power2.out" }}, {fmt(sb + 0.95)});')
tl.append(f'tl.to("#br-mark", {{ scale: 1, duration: 0.3, ease: "power2.inOut" }}, {fmt(sb + 1.09)});')
for k in range(6):
    tl.append(f'tl.to("#br-l{k}", {{ strokeDashoffset: 0, duration: 0.35, ease: "power2.out" }}, {fmt(sb + 1.0 + k * 0.07)});')
    tl.append(f'tl.fromTo("#br-n{k}", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "power3.out" }}, {fmt(sb + 1.15 + k * 0.07)});')
tl.append(f'tl.fromTo("#br-w0", {{ opacity: 0, y: 26, rotation: -3, scale: 0.9 }}, {{ opacity: 1, y: 0, rotation: 0, scale: 1, duration: 0.32, ease: "back.out(2.2)" }}, {fmt(max(sb + 0.6, tNF + 0.05))});')
tl.append(f'tl.fromTo("#br-stage", {{ rotationX: 38, rotationZ: -6, scale: 1.12 }}, {{ rotationX: 14, rotationZ: 0, scale: 1, duration: {fmt(db)}, ease: "power2.out", transformOrigin: "50% 50%" }}, {fmt(sb)});')
for k in range(6):
    tl.append(f'tl.to("#br-n{k}", {{ y: {(-10 if k % 2 else 10)}, duration: {fmt(db - 1.15 - k * 0.07)}, ease: "sine.inOut" }}, {fmt(sb + 1.15 + k * 0.07)});')

# ================= 4b. OPS CANVAS — the operator at work, native HyperFrames (agent log → real outputs → what worked)
W = json.load(open(f"{P}/../audio/voB_words.json"))
_chars = "".join(W["characters"]); _st = W["character_start_times_seconds"]
_i9 = _chars.find("It runs")
def word_at(phrase):
    j = _chars.find(phrase, _i9); return VO["09"]["start"] + (_st[j] - _st[_i9])
so, do = starts["ops"]; oid = ids["ops"]
tS, tC, tE, tW = word_at("strategy"), word_at("content"), word_at("every channel"), word_at("what actually")
print(f"ops: scene {so:.2f}+{do:.2f} | strategy {tS:.2f} content {tC:.2f} channel {tE:.2f} worked {tW:.2f}")
pat = re.compile(rf'(<div id="{oid}" class="clip title-card"[^>]*>).*?(</div>\n)', re.S)
mo = pat.search(html)
if not mo:
    raise SystemExit("ops scene not found")
rows = [("Read the brain", "brand · ICP · Q4 goals · last quarter"), ("Researched 3 competitors", "2 positioning gaps found"),
        ("Wrote 3 LinkedIn posts, 1 blog, 1 landing page", "in the brand's voice, from its own facts"),
        ("Published to 4 channels", "LinkedIn · Google Ads · Email · Web"), ("Measured, reported to the CMO", "every Monday, automatically")]
log = '<div id="ops-log" class="ocard" data-layout-allow-overlap><div class="oh"><img class="ologo" src="assets/images/logo-mark.png" alt="" /><b>KontentPlus operator</b><span class="osub">Q4 launch · Nowhere Networks</span><span id="ops-spin"></span></div>' + "".join(
    f'<div id="ops-row{i}" class="orow"><span id="ops-b{i}" class="obadge"><span class="n">{i+1}</span><svg viewBox="0 0 24 24"><path id="ops-ck{i}" d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></span><div><b>{t}</b><div class="d">{d}</div></div></div>' for i, (t, d) in enumerate(rows)) + '</div>'
post = ('<div id="ops-post" class="ocard opost" data-layout-allow-overlap><span id="ops-pub" class="opill">PUBLISHED · LINKEDIN</span><div class="ph"><span class="av">N</span><div><b>Nowhere Networks</b><small>12,480 followers · 2h</small></div></div>'
        '<p>Ferry operators lose crew connectivity mid-crossing. Most blame the satellite. It\'s the failover.<br>Here\'s what a 4-second handover looks like on a Stockholm–Turku run →</p>'
        '<div class="pimg"><img src="assets/images/ferry_post.jpg" alt="" /><div id="ops-sheen"></div></div>'
        '<div class="pr"><span class="rx">👍 ❤️</span><span id="ops-likes">0</span><span class="dot">·</span><span id="ops-cmt">0</span> comments<span class="dot">·</span><span id="ops-rep">0</span> reposts</div></div>')
blog = '<div id="ops-blog" class="ocard oblog" data-layout-allow-overlap><img src="assets/images/bridge_post.jpg" alt="" /><div class="bt"><small>BLOG · nowherenetworks.com</small><b>Why RoPax fleets are replacing VSAT with bonded SD-WAN</b></div></div>'
land = '<div id="ops-land" class="ocard oland" data-layout-allow-overlap><div class="chrome"><i></i><i></i><i></i><span>nowherenetworks.com/maritime</span></div><div class="lb"><b>Connectivity that survives the crossing.</b><span>Book a demo</span></div><small>LANDING PAGE · LIVE</small></div>'
chips = '<div id="ops-chips" data-layout-allow-overlap>' + "".join(f'<span id="ops-ch{i}" class="ochip"><i></i>{n}</span>' for i, n in enumerate(["LinkedIn", "Google Ads", "Email", "Web"])) + '</div>'
chart = ('<div id="ops-chart" class="ocard" data-layout-allow-overlap><div class="ct"><b>Leads · last 8 weeks</b><span id="ops-delta" class="opill green">+12 THIS WEEK</span></div>'
         '<svg viewBox="0 0 900 340" width="900" height="340"><g stroke="#e6e3dd" stroke-width="1"><line x1="20" y1="80" x2="880" y2="80"/><line x1="20" y1="160" x2="880" y2="160"/><line x1="20" y1="240" x2="880" y2="240"/><line x1="20" y1="320" x2="880" y2="320"/></g>'
         '<path id="ops-area" d="M20 300 C140 290 200 280 300 262 C400 244 460 250 540 214 C620 178 680 170 760 120 C820 84 850 60 880 40 L880 320 L20 320 Z" fill="url(#ops-g)" opacity="0"/>'
         '<defs><linearGradient id="ops-g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#056df5" stop-opacity="0.35"/><stop offset="1" stop-color="#056df5" stop-opacity="0"/></linearGradient></defs>'
         '<path id="ops-line" d="M20 300 C140 290 200 280 300 262 C400 244 460 250 540 214 C620 178 680 170 760 120 C820 84 850 60 880 40" fill="none" stroke="#056df5" stroke-width="6" stroke-linecap="round" stroke-dasharray="1400" stroke-dashoffset="1400"/>'
         '<circle id="ops-dotc" cx="880" cy="40" r="11" fill="#056df5" stroke="#fff" stroke-width="4" opacity="0"/></svg></div>')
stats = "".join(f'<div id="ops-st{i}" class="ocard ostat" data-layout-allow-overlap><small>{l}</small><b><span id="ops-v{i}">0</span>{u}</b><em>{d}</em></div>' for i, (l, u, d) in enumerate([("QUALIFIED PIPELINE", "k", "+38% this quarter"), ("COST PER LEAD", "", "−22%"), ("HOURS SAVED / WEEK", "", "one operator, four channels")]))
nxt = '<div id="ops-next" class="ocard onext" data-layout-allow-overlap><img class="ologo" src="assets/images/logo-mark.png" alt="" /><div><small>NEXT WEEK · PROPOSED</small><b>Double down on the failover angle — CPL 2.3× better</b></div><span class="ok">Approve</span></div>'
kin = f'<div id="ops-kt" class="kt full" style="left:96px;top:{330 if PORTRAIT else 56}px;bottom:auto"><span id="ops-kw0" class="w navy" data-layout-allow-overlap>One operation.</span><span id="ops-kw1" class="w blue" data-layout-allow-overlap>Every channel.</span></div>'
ops_html = f'<div id="ops-cam" data-layout-allow-overflow><div id="ops-world" data-layout-allow-overflow>{log}{post}{blog}{land}{chips}{chart}{stats}{nxt}</div></div>{kin}'
html = html[:mo.start()] + (mo.group(1) + ops_html + mo.group(2)) + html[mo.end():]
html = re.sub(rf'\n\s*tl\.fromTo\("#{oid}-h1".*?\);', '', html)
css.append(f"""      #{oid} {{ background: #f4f2ee; background-image: radial-gradient(rgba(20,31,41,0.10) 1.2px, transparent 1.2px); background-size: 28px 28px; overflow: hidden; }}
      #ops-cam {{ position: absolute; left: 0; top: 0; width: {FW}px; height: {FH}px; transform-origin: 0 0; }}
      #ops-world {{ position: absolute; left: 0; top: 0; width: 3300px; height: 1080px; font-family: {FONT}; color: #141f29; text-align: left; line-height: 1.25; }}
      .ologo {{ width: 38px; height: 38px; flex: none; display: block; }}
      .ocard {{ position: absolute; background: #fff; border-radius: 22px; box-shadow: 0 24px 70px rgba(20,31,41,0.14), 0 2px 6px rgba(20,31,41,0.06); opacity: 0; transform-origin: 50% 50%; }}
      .omark {{ display: inline-block; width: 16px; height: 16px; background: #056df5; box-shadow: 0 0 14px rgba(5,109,245,0.6); border-radius: 3px; flex: none; }}
      #ops-log {{ left: 120px; top: 150px; width: 720px; padding: 34px 40px; }}
      #ops-log .oh {{ display: flex; align-items: center; gap: 14px; padding-bottom: 22px; border-bottom: 1px solid #ecebe7; margin-bottom: 8px; font-size: 30px; }} #ops-log .oh b {{ font-weight: 700; }} .osub {{ color: #7a7a82; font-size: 22px; flex: 1; }}
      #ops-spin {{ width: 30px; height: 30px; border-radius: 50%; border: 4px solid #dfe8f7; border-top-color: #056df5; flex: none; }}
      .orow {{ display: flex; gap: 20px; align-items: flex-start; padding: 19px 0; border-bottom: 1px solid #f1f0ec; font-size: 27px; opacity: 0; }} .orow:last-child {{ border: 0; }} .orow b {{ font-weight: 650; }} .orow .d {{ font-size: 20px; color: #7a7a82; margin-top: 3px; }}
      .obadge {{ position: relative; width: 40px; height: 40px; border-radius: 50%; border: 3px solid #cfd3da; flex: none; margin-top: 2px; display: grid; place-items: center; font: 700 17px/1 {FONT}; color: #7a7a82; }}
      .obadge svg {{ position: absolute; inset: 6px; opacity: 0; }} .obadge.done {{ background: #2e9e6b; border-color: #2e9e6b; }} .obadge.done .n {{ opacity: 0; }}
      .opill {{ position: absolute; right: 26px; top: 26px; padding: 9px 16px; border-radius: 999px; background: #0a66c2; color: #fff; font: 700 14px/1 ui-monospace, Menlo, monospace; letter-spacing: .1em; opacity: 0; }} .opill.green {{ background: #2e9e6b; position: static; }}
      .opost {{ left: 980px; top: 90px; width: 700px; padding: 30px 32px 26px; }} .ph {{ display: flex; gap: 16px; align-items: center; margin-bottom: 18px; }} .ph .av {{ width: 62px; height: 62px; border-radius: 50%; background: #141f29; color: #fff; display: grid; place-items: center; font: 800 28px/1 {FONT}; }} .ph b {{ font-size: 25px; display: block; }} .ph small {{ font-size: 18px; color: #7a7a82; }}
      .opost p {{ font-size: 24px; line-height: 1.38; margin: 0 0 18px; }} .pimg {{ position: relative; border-radius: 14px; overflow: hidden; height: 360px; }} .pimg img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
      #ops-sheen {{ position: absolute; inset: 0; background: linear-gradient(105deg, rgba(255,255,255,0) 40%, rgba(255,255,255,0.7) 50%, rgba(255,255,255,0) 60%); transform: translateX(-100%); }}
      .pr {{ display: flex; gap: 10px; align-items: center; margin-top: 16px; font-size: 21px; color: #55555e; }} .pr .rx {{ font-size: 19px; }} .pr .dot {{ color: #b7b7be; }} #ops-likes, #ops-cmt, #ops-rep {{ font-variant-numeric: tabular-nums; font-weight: 650; color: #141f29; }}
      .oblog {{ left: 1730px; top: 90px; width: 470px; overflow: hidden; }} .oblog img {{ width: 100%; height: 240px; object-fit: cover; display: block; }} .oblog .bt {{ padding: 20px 24px 24px; }} .oblog small {{ font: 700 13px/1 ui-monospace, Menlo, monospace; letter-spacing: .1em; color: #056df5; display: block; margin-bottom: 8px; }} .oblog b {{ font-size: 24px; line-height: 1.25; display: block; }}
      .oland {{ left: 1730px; top: 500px; width: 470px; padding: 0 0 20px; overflow: hidden; }} .chrome {{ display: flex; gap: 7px; align-items: center; padding: 14px 18px; background: #f0efeb; }} .chrome i {{ width: 11px; height: 11px; border-radius: 50%; background: #d3d1cb; }} .chrome span {{ margin-left: 10px; font: 500 15px/1 ui-monospace, Menlo, monospace; color: #7a7a82; }}
      .oland .lb {{ padding: 26px 24px 18px; }} .oland .lb b {{ display: block; font-size: 27px; line-height: 1.2; letter-spacing: -0.01em; margin-bottom: 16px; }} .oland .lb span {{ display: inline-block; padding: 10px 18px; border-radius: 999px; background: #056df5; color: #fff; font-size: 17px; font-weight: 600; }} .oland small {{ display: block; padding: 0 24px; font: 700 13px/1 ui-monospace, Menlo, monospace; letter-spacing: .1em; color: #2e9e6b; }}
      #ops-chips {{ position: absolute; left: 980px; top: 900px; display: flex; gap: 16px; }} .ochip {{ display: inline-flex; gap: 12px; align-items: center; padding: 16px 26px; border-radius: 999px; background: #fff; border: 2px solid #e4e2dc; color: #9a9aa2; font-size: 24px; font-weight: 600; opacity: 0; }} .ochip i {{ width: 12px; height: 12px; border-radius: 50%; background: #d3d1cb; }} .ochip.on {{ background: #141f29; border-color: #141f29; color: #fff; }} .ochip.on i {{ background: #2e9e6b; box-shadow: 0 0 12px #2e9e6b; }}
      #ops-chart {{ left: 2330px; top: 90px; width: 900px; padding: 28px 0 10px; }} .ct {{ display: flex; align-items: center; justify-content: space-between; padding: 0 36px 14px; font-size: 26px; }}
      .ostat {{ top: 560px; width: 280px; padding: 26px 30px; }} #ops-st0 {{ left: 2330px; }} #ops-st1 {{ left: 2640px; }} #ops-st2 {{ left: 2950px; }} .ostat small {{ font: 700 13px/1 ui-monospace, Menlo, monospace; letter-spacing: .1em; color: #7a7a82; }} .ostat b {{ display: block; font-size: 56px; letter-spacing: -0.03em; margin: 10px 0 4px; font-variant-numeric: tabular-nums; }} .ostat em {{ font-style: normal; color: #2e9e6b; font-weight: 650; font-size: 21px; }}
      .onext {{ left: 2330px; top: 800px; width: 900px; padding: 24px 30px; display: flex; gap: 20px; align-items: center; background: #f3faf6; border: 1px solid #cfe3d6; }} .onext small {{ font: 700 13px/1 ui-monospace, Menlo, monospace; letter-spacing: .1em; color: #2e9e6b; display: block; margin-bottom: 6px; }} .onext b {{ font-size: 25px; }} .onext div {{ flex: 1; }} .onext .ok {{ padding: 12px 22px; border-radius: 999px; background: #141f29; color: #fff; font-size: 20px; font-weight: 600; }}
      #ops-kt .w {{ font-size: 50px; }}""")
def cam(wx, wy, sc, dur, at, ease="power2.inOut"):
    tl.append(f'tl.to("#ops-cam", {{ x: {FW / 2 - wx * sc:.0f}, y: {FH / 2 - wy * sc:.0f}, scale: {sc}, duration: {fmt(dur)}, ease: "{ease}" }}, {fmt(at)});')
CAM0 = (480, 430, 1.4) if PORTRAIT else (480, 560, 1.25)
tl.append(f'tl.set("#ops-cam", {{ x: {FW / 2 - CAM0[0] * CAM0[2]:.0f}, y: {FH / 2 - CAM0[1] * CAM0[2]:.0f}, scale: {CAM0[2]} }}, {fmt(so)});')
tl.append(f'tl.fromTo("#ops-log", {{ opacity: 0, y: 30, scale: 0.96 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "power3.out" }}, {fmt(so + 0.05)});')
tl.append(f'tl.fromTo("#ops-spin", {{ rotation: 0 }}, {{ rotation: 360 * 6, duration: {fmt(do)}, ease: "none" }}, {fmt(so)});')
for i in range(5):
    tl.append(f'tl.fromTo("#ops-row{i}", {{ opacity: 0, x: -18 }}, {{ opacity: 1, x: 0, duration: 0.3, ease: "power3.out" }}, {fmt(so + 0.25 + i * 0.11)});')
def check(i, at):
    tl.append(f'tl.to("#ops-b{i}", {{ backgroundColor: "#2e9e6b", borderColor: "#2e9e6b", scale: 1.15, duration: 0.14, ease: "power2.out" }}, {fmt(at)});')
    tl.append(f'tl.to("#ops-b{i} .n", {{ opacity: 0, duration: 0.1 }}, {fmt(at)});')
    tl.append(f'tl.fromTo("#ops-b{i} svg", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)" }}, {fmt(at + 0.06)});')
    tl.append(f'tl.to("#ops-b{i}", {{ scale: 1, duration: 0.18, ease: "power2.inOut" }}, {fmt(at + 0.16)});')
check(0, max(so + 0.7, tS - 0.2)); check(1, max(so + 0.95, tS + 0.05)); check(2, tC - 0.1)
# content: the post springs out of the log; the camera glides to the outputs
cam(*((1590, 480, 0.85) if PORTRAIT else (1450, 560, 1.0)), 0.7, tC - 0.15)
tl.append(f'tl.fromTo("#ops-post", {{ opacity: 0, x: -140, scale: 0.82 }}, {{ opacity: 1, x: 0, scale: 1, duration: 0.55, ease: "power3.out" }}, {fmt(tC - 0.05)});')
tl.append(f'tl.fromTo("#ops-sheen", {{ x: "-100%" }}, {{ x: "100%", duration: 0.7, ease: "power2.inOut" }}, {fmt(tC + 0.35)});')
tl.append(f'tl.fromTo("#ops-pub", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, {fmt(tC + 0.45)});')
tl.append('const opsV = { l: 0, c: 0, r: 0, a: 0, b: 0, d: 0 };')
tl.append(f'tl.to(opsV, {{ l: 214, c: 31, r: 18, duration: 1.1, ease: "power2.out", onUpdate: () => {{ document.getElementById("ops-likes").textContent = Math.round(opsV.l); document.getElementById("ops-cmt").textContent = Math.round(opsV.c); document.getElementById("ops-rep").textContent = Math.round(opsV.r); }} }}, {fmt(tC + 0.5)});')
tl.append(f'tl.fromTo("#ops-blog", {{ opacity: 0, y: 40, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "power3.out" }}, {fmt(tC + 0.3)});')
tl.append(f'tl.fromTo("#ops-land", {{ opacity: 0, y: 40, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "power3.out" }}, {fmt(tC + 0.5)});')
# every channel: chips light in sequence, row 4 checks, kinetic pair
for i in range(4):
    tl.append(f'tl.fromTo("#ops-ch{i}", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.25, ease: "power3.out" }}, {fmt(tE - 0.35 + i * 0.07)});')
    tl.append(f'tl.to("#ops-ch{i}", {{ backgroundColor: "#141f29", borderColor: "#141f29", color: "#ffffff", duration: 0.18 }}, {fmt(tE + 0.05 + i * 0.13)});')
    tl.append(f'tl.to("#ops-ch{i} i", {{ backgroundColor: "#2e9e6b", boxShadow: "0 0 12px #2e9e6b", duration: 0.18 }}, {fmt(tE + 0.05 + i * 0.13)});')
check(3, tE + 0.5)
for j in range(2):
    tl.append(f'tl.fromTo("#ops-kw{j}", {{ opacity: 0, y: 26, rotation: -3, scale: 0.9 }}, {{ opacity: 1, y: 0, rotation: 0, scale: 1, duration: 0.32, ease: "back.out(2.2)" }}, {fmt(tE + 0.1 + j * 0.28)});')
tl.append(f'tl.to("#ops-kt", {{ opacity: 0, duration: 0.3 }}, {fmt(tW - 0.1)});')
# what actually worked: camera to the results, chart draws, counters, the proposal
cam(*((2780, 500, 1.1) if PORTRAIT else (2780, 540, 0.98)), 0.7, tW - 0.5)
tl.append(f'tl.fromTo("#ops-chart", {{ opacity: 0, y: 30, scale: 0.96 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "power3.out" }}, {fmt(tW - 0.35)});')
tl.append(f'tl.to("#ops-line", {{ strokeDashoffset: 0, duration: 0.8, ease: "power2.inOut" }}, {fmt(tW - 0.15)});')
tl.append(f'tl.to("#ops-area", {{ opacity: 1, duration: 0.5 }}, {fmt(tW + 0.45)});')
tl.append(f'tl.fromTo("#ops-dotc", {{ opacity: 0, scale: 0.3, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: "back.out(2)" }}, {fmt(tW + 0.65)});')
tl.append(f'tl.fromTo("#ops-delta", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, {fmt(tW + 0.75)});')
for i in range(3):
    tl.append(f'tl.fromTo("#ops-st{i}", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, {fmt(tW + 0.05 + i * 0.12)});')
tl.append(f'tl.to(opsV, {{ a: 412, b: 48, d: 31, duration: 0.8, ease: "power2.out", onUpdate: () => {{ document.getElementById("ops-v0").textContent = "€" + Math.round(opsV.a); document.getElementById("ops-v1").textContent = "€" + Math.round(opsV.b); document.getElementById("ops-v2").textContent = Math.round(opsV.d); }} }}, {fmt(tW + 0.2)});')
check(4, tW + 0.8)
tl.append(f'tl.fromTo("#ops-next", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, {fmt(tW + 1.0)});')
tl.append(f'tl.to("#ops-next .ok", {{ scale: 0.92, backgroundColor: "#2e9e6b", duration: 0.12, ease: "power2.in" }}, {fmt(tW + 1.45)});')
tl.append(f'tl.to("#ops-next .ok", {{ scale: 1, duration: 0.25, ease: "back.out(2)" }}, {fmt(tW + 1.57)});')
tl.append(f'tl.to("#ops-next .ok", {{ textContent: "Approved ✓", duration: 0.01 }}, {fmt(tW + 1.5)});')
tl.append(f'tl.to("#ops-cam", {{ scale: 1.02, x: "-=30", duration: {fmt(max(0.6, so + do - (tW + 1.1)))}, ease: "sine.inOut" }}, {fmt(tW + 1.1)});')

s4, d4 = starts["app4"]; sid = ids["app4"]
if PORTRAIT: YO = 576
plate(sid)
inner = (cursor(sid, "e", s4, [(0.3, 980, 640), (0.6, 640, 276)], click_at=0.95)
         + f'<div id="{sid}-hl" class="hl" style="left:{cx(295):.0f}px;top:{cy(240):.0f}px;width:{cx(1082):.0f}px;height:{cy(68) - YO:.0f}px"></div>'
         + f'<div id="{sid}-hl2" class="hl" style="left:{cx(270):.0f}px;top:{cy(337):.0f}px;width:{cx(1132):.0f}px;height:{cy(126) - YO:.0f}px;border-color:#2e9e6b;box-shadow:0 0 0 6px rgba(46,158,107,0.18)"></div>')
inject_into_image_scene("app4", inner)
tl.append(f'tl.fromTo("#{sid}-hl", {{ opacity: 0, scale: 1.04 }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: "power2.out" }}, {fmt(s4 + 0.95)});')
tl.append(f'tl.to("#{sid}-hl", {{ opacity: 0, duration: 0.3 }}, {fmt(s4 + 1.8)});')
tl.append(f'tl.fromTo("#{sid}-hl2", {{ opacity: 0, scale: 1.04 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "power2.out" }}, {fmt(s4 + 1.9)});')
css.append(f"#{sid} {{ transform-origin: 50% 52%; }}")
tl.append(f'tl.fromTo("#{sid}", {{ scale: 1.0 }}, {{ scale: 1.2, duration: {fmt(d4)}, ease: "power1.inOut" }}, {fmt(s4)});')

# results plate: light grade + vignette so the live-action sits with the film
sc, dc = starts["cmo"]; cid = ids["cmo"]
if PORTRAIT: css.append(f"#{cid} {{ position: absolute; left: {MOD_L}px; top: {MOD_T}px; width: {FW - MOD_L - MOD_R}px; height: {MOD_BOT - MOD_T}px; border-radius: 18px; }}")
# colour + vignette for the results plate come from GRADE below (canonical data-color-grading)
tl.append(f'tl.fromTo("#{cid}", {{ scale: 1.0 }}, {{ scale: 1.06, duration: {fmt(dc)}, ease: "power1.inOut" }}, {fmt(sc)});')


# ================= 6. end card (single animated lockup)
s_x, d_x = starts["end"]; xid = ids["end"]
LW = 900 if PORTRAIT else 960; CELL = LW * 356 / 2500 / 5
order = [(1, 3), (0, 2), (1, 1), (2, 4), (2, 0), (3, 3), (3, 1), (4, 2)]
pxs = "".join(f'<div id="epx{i}" class="epx{" blue" if (r, c) == (1, 3) else ""}" style="left:{c * CELL:.1f}px;top:{r * CELL:.1f}px"></div>' for i, (r, c) in enumerate(order))
pat = re.compile(rf'(<div id="{xid}" class="clip title-card"[^>]*>).*?(</div>\n)', re.S)
mo = pat.search(html)
if not mo:
    raise SystemExit("end card not found")
html = html[:mo.start()] + (mo.group(1) + '<div id="end-glow"></div><div id="end-lockup"><img id="end-logo" src="assets/images/logo-full-white.png" alt="KontentPlus" data-layout-allow-overlap />' + pxs + '</div>'
        '<h1 id="end-h1">Marketing operations, handled.</h1><div id="end-cta">Let\'s talk</div><div id="end-sub">30-day pilot · your files, your channels, your numbers</div><div id="end-url">kontentplus.com</div>' + mo.group(2)) + html[mo.end():]
html = re.sub(rf'\n\s*tl\.fromTo\("#{xid}-h1".*?\);', '', html)
html = re.sub(rf'\n\s*tl\.fromTo\("#{xid}-cta".*?\);', '', html)
css.append(f"""      #{xid} {{ background: #141f29; overflow: hidden; }}
      #end-glow {{ position: absolute; width: 1200px; height: 1200px; border-radius: 50%; left: {FW // 2 - 600}px; top: {FH // 2 - 820}px; background: radial-gradient(circle, rgba(5,109,245,0.6) 0%, rgba(5,109,245,0) 58%); opacity: 0; }}
      #end-lockup {{ position: absolute; left: 50%; top: {FH // 2 - 210}px; width: {LW}px; margin-left: {-LW // 2}px; }}
      #end-logo {{ width: 100%; display: block; opacity: 0; clip-path: inset(0 100% 0 19%); }}
      .epx {{ position: absolute; width: {CELL - 2:.1f}px; height: {CELL - 2:.1f}px; margin: 1px; background: #fff; opacity: 0; transform-origin: center; }} .epx.blue {{ background: #056df5; box-shadow: 0 0 18px 4px rgba(5,109,245,0.55); }}
      #end-h1 {{ position: absolute; left: 0; right: 0; top: {FH // 2 + 60}px; text-align: center; font: 800 {46 if PORTRAIT else 56}px/1.1 {FONT}; letter-spacing: -0.02em; color: #fff; opacity: 0; }}
      #end-cta {{ position: absolute; left: 50%; top: {FH // 2 + 150}px; transform: translateX(-50%); padding: 24px 56px; border-radius: 999px; background: #fff; color: #141f29; font: 700 34px/1 {FONT}; opacity: 0; box-shadow: 0 16px 50px rgba(5,109,245,0.35); }}
      #end-sub {{ position: absolute; left: 0; right: 0; top: {FH // 2 + 242}px; text-align: center; font: 500 24px/1 {FONT}; color: rgba(255,255,255,0.75); opacity: 0; }}
      #end-url {{ position: absolute; left: 0; right: 0; top: {FH // 2 + 296}px; text-align: center; font: 500 25px/1 ui-monospace, Menlo, monospace; letter-spacing: .08em; color: rgba(255,255,255,0.8); opacity: 0; }}""")
tl.append(f'tl.fromTo("#end-glow", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.6, ease: "power2.out" }}, {fmt(s_x + 0.2)});')
tl.append(f'tl.to("#end-glow", {{ opacity: 0.35, scale: 1.4, duration: 1.4, ease: "sine.inOut" }}, {fmt(s_x + 0.8)});')
for i in range(8):
    tl.append(f'tl.fromTo("#epx{i}", {{ opacity: 0, scale: 0.2, rotation: 90 }}, {{ opacity: 1, scale: 1, rotation: 0, duration: 0.22, ease: "back.out(2.5)" }}, {fmt(s_x + 0.35 + i * 0.07)});')
tl.append(f'tl.fromTo("#end-logo", {{ opacity: 0, clipPath: "inset(0 100% 0 19%)" }}, {{ opacity: 1, clipPath: "inset(0 0% 0 19%)", duration: 0.8, ease: "power3.out" }}, {fmt(s_x + 0.95)});')
tl.append(f'tl.fromTo("#end-h1", {{ opacity: 0, y: 30, scale: 0.92 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.55, ease: "back.out(1.6)" }}, {fmt(s_x + 1.7)});')
tl.append(f'tl.fromTo("#end-cta", {{ boxShadow: "0 16px 50px rgba(5,109,245,0.35), 0 0 0 0 rgba(255,255,255,0.7)" }}, {{ boxShadow: "0 16px 50px rgba(5,109,245,0.35), 0 0 0 24px rgba(255,255,255,0)", duration: 1.1, ease: "power2.out", repeat: 1 }}, {fmt(s_x + 3.0)});')
tl.append(f'tl.fromTo("#end-cta", {{ opacity: 0, scale: 0.8 }}, {{ opacity: 1, scale: 1, duration: 0.45, ease: "back.out(1.8)" }}, {fmt(s_x + 2.3)});')
tl.append(f'tl.fromTo("#end-sub", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.4 }}, {fmt(s_x + 2.75)});')
tl.append(f'tl.fromTo("#end-url", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {fmt(s_x + 3.0)});')
tl.append(f'tl.to("#end-lockup", {{ scale: 1.03, duration: 1.6, ease: "sine.inOut", yoyo: true, repeat: 1 }}, {fmt(s_x + 3.2)});')


# ================= 6b. SHOT MATCH — one grade so every live-action shot reads as one film
# Ola's note (2026-09-05): the era shots and the meeting-room plate don't feel like the same movie.
# Measured with `hyperframes media-treatment --analyze` (signalstats, yLow=p1 / yAvg / yHigh=p99):
#   scene-01 merchant1900  35.4 /  86.3 / 145.4   mono
#   scene-02 ref_1926      25.2 /  79.1 / 155.2   mono
#   scene-03 boardroom1960 35.6 /  78.0 / 141.8   warm  (v 134.7)
#   scene-04 mailroom1990  28.0 /  96.1 / 179.8   green (u 130.0 / v 125.9)
#   scene-05 saasdesk2010  26.8 / 106.6 / 190.4   cool  <- house anchor
#   scene-06 ref_2016b     25.0 /  61.5 / 119.6   cool, very dark, no real highlight
#   scene-12 scene_results 52.8 / 159.5 / 212.8   <- milky blacks, +50 IRE above the whole film
# Each clip is individually clean, so --analyze suggests ~nothing; the fault is RELATIVE.
# Fix = one shared print (cool shadows / warm highlights, same S-curve) + a per-shot
# match onto a common black floor (~26-30) and highlight ceiling (~180-200).
SHOW_WHEELS = {"shadows": {"hue": 205, "amount": 0.07, "level": 0},
               "highlights": {"hue": 35, "amount": 0.045, "level": 0}}
SHOW_CURVE = {"master": [[0, 0], [0.25, 0.21], [0.75, 0.79], [1, 1]]}

def _grade(adjust, *, mono=False):
    # No vignette / grain in the payload (Aman, 2026-09-06: "you added a black filter, the edges are easily visible").
    # The era modules already carry their own edge treatment (.mod-grain, sized to the module rect), and in the 9:16
    # build the <video> IS the module rect, so a shader vignette puts its full darkening right at the clip edge and
    # reads as a dark frame with a visible border. The shot-match is tonal + print only.
    g = {"adjust": adjust, "curves": SHOW_CURVE}
    if not mono:                       # archival mono stays neutral — a split-tone would read as sepia
        g["wheels"] = SHOW_WHEELS
    return g

GRADE = {
    # 1900s / 1920s archival: match the tonal range only, keep it a clean monochrome print
    "era1900":  _grade({"blacks": -0.12, "whites": 0.06, "contrast": 0.06}, mono=True),
    "era1926":  _grade({"exposure": 0.05, "contrast": 0.03}, mono=True),
    # 1960s: keep the era warmth, take the milk out of the blacks
    "era1960":  _grade({"exposure": 0.05, "contrast": 0.09, "blacks": -0.12, "whites": 0.08, "saturation": -0.16}),
    # 1990s: pull the green cast, sit it on the common floor
    "era1990":  _grade({"exposure": -0.05, "contrast": 0.07, "blacks": -0.07, "tint": -0.07, "saturation": -0.14}),
    # 2010s: the anchor everything else is matched to — barely touched
    "era2010":  _grade({"contrast": 0.05, "blacks": -0.04, "saturation": -0.20}),
    # night desk: lift it off the floor and give it a real highlight (yHigh 120 -> ~150)
    "era2010b": _grade({"exposure": 0.16, "whites": 0.20, "contrast": 0.05, "blacks": -0.04, "saturation": -0.20}),
    # meeting room: THE fix — drop it ~40 IRE, crush the milky 52.8 black floor, add contrast, cool it
    # (exposure -0.50 not -0.40: the vignette that used to take ~10 IRE off the edges is gone)
    "cmo":      _grade({"exposure": -0.50, "contrast": 0.18, "blacks": -0.45, "highlights": -0.20,
                        "temperature": -0.06, "saturation": -0.10}),
}
for _k, _g in GRADE.items():
    _sid = ids[_k]
    _payload = json.dumps(_g, separators=(",", ":")).replace('"', "&quot;")
    _needle = f'<video id="{_sid}" '
    assert _needle in html, f"grade target {_sid} ({_k}) not found"
    html = html.replace(_needle, f'{_needle}data-color-grading="{_payload}" ', 1)


html = html.replace("    </style>", "\n".join(css) + "\n    </style>", 1)
html = html.replace("\n    </div>\n    <script>", "\n" + "\n".join("      " + h for h in add) + "\n    </div>\n    <script>", 1)
html = html.replace('      window.__timelines["main"] = tl;', "      " + "\n      ".join(tl) + '\n      window.__timelines["main"] = tl;', 1)
open(HTML, "w").write(html)
print(f"overlays v13 (timeline device) injected: {len(add)} clips, {len(tl)} tweens, total {TOTAL:.1f}s")
