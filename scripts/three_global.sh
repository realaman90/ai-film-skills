#!/usr/bin/env bash
# Vendor three.js into a HyperFrames project as a classic-script GLOBAL (window.THREE).
#
# Why: three r160+ ships ES modules only. A module (or importmap) loads async, so a scene
# that builds its timeline synchronously can run before THREE exists. A classic <script>
# in index.html <head> is loaded before any sub-composition builds.
#
#   scripts/three_global.sh <project_dir> [version]      # default 0.181.2
#   → <project_dir>/assets/vendor/three.global.js
#
# Then (hf_add_sfx.mjs --head-js does this for you):
#   index.html <head>:            <script src="assets/vendor/three.global.js"></script>
#   each scene's <template> too:  <script src="assets/vendor/three.global.js"></script>
#     (satisfies lint missing_three_script; the duplicate-instance console warning is harmless)
set -euo pipefail
PROJECT="${1:?usage: three_global.sh <project_dir> [version]}"
VER="${2:-0.181.2}"
OUT="$PROJECT/assets/vendor"
mkdir -p "$OUT"
curl -fsSL -o "$OUT/three.module.js" "https://cdn.jsdelivr.net/npm/three@$VER/build/three.module.js"
curl -fsSL -o "$OUT/three.core.js" "https://cdn.jsdelivr.net/npm/three@$VER/build/three.core.js"
npx --yes esbuild@0.25.10 "$OUT/three.module.js" --bundle --format=iife --global-name=THREE --minify \
  --outfile="$OUT/three.global.js" --log-level=warning
rm -f "$OUT/three.module.js" "$OUT/three.core.js"
echo "wrote $OUT/three.global.js (three $VER, $(du -h "$OUT/three.global.js" | cut -f1))"
