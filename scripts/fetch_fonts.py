#!/usr/bin/env python3
"""Download Google Fonts as local woff2 files + an @font-face stylesheet for a HyperFrames project.

Renders should not depend on the network, and HyperFrames lint (`font_family_without_font_face`)
only auto-resolves a few families — declare the rest yourself.

  python3 scripts/fetch_fonts.py --out <project>/assets/fonts "Barlow:400,600,700,800,900" "IBM Plex Mono:500"
  → <out>/<Family>-<weight>.woff2 + <out>/fonts.css   (latin subset)

Use it twice:
  1. link fonts.css in index.html <head> (hf_add_sfx.mjs --head-css does this);
  2. paste the printed @font-face block into each scene's <template> <style> (lint checks per file;
     urls there resolve from index.html, so they read `assets/fonts/...`).
"""
import argparse
import os
import re
import sys
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("families", nargs="+", help='"Family Name:400,700" (weights comma-separated)')
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    parts = []
    for spec in args.families:
        name, _, weights = spec.partition(":")
        weights = ";".join(sorted(set((weights or "400").split(",")), key=int))
        parts.append(f"family={urllib.parse.quote_plus(name.strip())}:wght@{weights}")
    url = "https://fonts.googleapis.com/css2?" + "&".join(parts) + "&display=block"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        css = urllib.request.urlopen(req, timeout=30).read().decode()
    except Exception as err:  # network / bad family name
        sys.exit(f"could not fetch {url}: {err}")

    faces_local, faces_project = [], []
    for subset, body in re.findall(r"/\*\s*([^*]+?)\s*\*/\s*@font-face\s*{([^}]*)}", css):
        if subset.strip() != "latin":
            continue
        fam = re.search(r"font-family:\s*'([^']+)'", body).group(1)
        weight = re.search(r"font-weight:\s*(\d+)", body).group(1)
        src = re.search(r"url\((https[^)]+)\)", body).group(1)
        fn = f"{fam.replace(' ', '')}-{weight}.woff2"
        try:
            urllib.request.urlretrieve(src, os.path.join(args.out, fn))
        except Exception as err:
            sys.exit(f"could not download {fam} {weight}: {err}")
        rule = "@font-face{font-family:'%s';font-weight:%s;font-style:normal;font-display:block;src:url('%%s') format('woff2');}" % (fam, weight)
        faces_local.append(rule % fn)
        faces_project.append(rule % f"assets/fonts/{fn}")

    with open(os.path.join(args.out, "fonts.css"), "w") as f:
        f.write("\n".join(faces_local) + "\n")
    print(f"wrote {len(faces_local)} faces + fonts.css to {args.out}\n")
    print("-- paste into each scene's <template><style> --")
    print("".join(faces_project))


if __name__ == "__main__":
    main()
