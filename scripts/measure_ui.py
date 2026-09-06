#!/usr/bin/env python3
"""Measure element boxes in an HTML mockup with headless Chrome — never guess overlay coordinates.

Renders the page at a fixed viewport, appends every element's getBoundingClientRect() to the DOM, dumps it, and prints
`TAG.class | text | left,top,width,height` for elements whose text matches --grep. Use the numbers for highlight rings,
cursor targets and punch-in origins. (The in-app browser renders local files as static snapshots, so its JS cannot
measure them; this route can.)

Usage:
    python scripts/measure_ui.py hero/hero1.html --grep "INTERVIEWS|Customer interviews" [--size 1440x900]
    python scripts/measure_ui.py hero/hero4.html --grep "LEARNED|Ferry operators" --json rects.json
Map css → composition for a 1440×900 plate covered into 1920×1080: x' = x·4/3, y' = y·4/3 − 60.
"""
import argparse, html as htmlmod, json, os, re, shutil, subprocess, tempfile

CHROME = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "google-chrome", "chromium", "chrome"]
JS = """<script>window.addEventListener('load',()=>{const r=(el)=>{const b=el.getBoundingClientRect();return [Math.round(b.left),Math.round(b.top),Math.round(b.width),Math.round(b.height)]};
const out=[]; document.querySelectorAll('body *').forEach(e=>{if(['SCRIPT','STYLE','PRE'].includes(e.tagName))return; const t=(e.textContent||'').trim().replace(/\\s+/g,' ').slice(0,60); if(t) out.push(e.tagName+'.'+(e.className||'')+' | '+t+' | '+r(e).join(','))});
const d=document.createElement('pre'); d.id='__rects'; d.textContent=out.join('\\n'); document.body.appendChild(d);});</script>"""


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("html"); p.add_argument("--grep", default=".", help="regex on tag/class/text"); p.add_argument("--size", default="1440x900")
    p.add_argument("--json", default=None); p.add_argument("--chrome", default=None)
    a = p.parse_args()
    chrome = a.chrome or next((c for c in CHROME if os.path.exists(c) or shutil.which(c)), None)
    if not chrome:
        raise SystemExit("Chrome not found; pass --chrome /path/to/chrome")
    src = open(a.html).read(); tmp = os.path.join(os.path.dirname(os.path.abspath(a.html)), "._measure_" + os.path.basename(a.html))
    open(tmp, "w").write(src.replace("</body>", JS + "</body>") if "</body>" in src else src + JS)
    try:
        dom = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={a.size.replace('x', ',')}", "--virtual-time-budget=2000", "--dump-dom", f"file://{os.path.abspath(tmp)}"],
                             capture_output=True, text=True).stdout
    finally:
        os.remove(tmp)
    m = re.search(r'<pre id="__rects">(.*?)</pre>', dom, re.S)
    if not m:
        raise SystemExit("no rects captured (page error?)")
    rows = []
    for line in htmlmod.unescape(m.group(1)).splitlines():
        if re.search(a.grep, line, re.I):
            tag, text, rect = [x.strip() for x in line.split(" | ")]; rows.append({"el": tag, "text": text, "rect": [int(v) for v in rect.split(",")]}); print(line)
    if a.json:
        json.dump(rows, open(a.json, "w"), indent=2); print("→", a.json)


if __name__ == "__main__":
    main()
