#!/bin/bash
# Scaffold a HyperFrames project for film assembly.
# Usage: new_hyperframes_project.sh <target-dir> [--aspect 16:9|9:16|1:1]
#
# Creates:
#   <target>/index.html        (blank composition, overwritten by build_hyperframes_timeline.py)
#   <target>/hyperframes.json  (CLI config, assets dir = assets/)
#   <target>/assets/           (drop clips/, images/, audio/ here)
#   <target>/package.json      (pinned hyperframes version: npm run dev|check|render)
set -e

TARGET="${1:?target dir required (e.g. /tmp/my-film/film)}"
shift || true
ASPECT="16:9"
while [ $# -gt 0 ]; do
  case "$1" in
    --aspect) ASPECT="$2"; shift 2 ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
done

case "$ASPECT" in
  16:9) RES="landscape" ;;
  9:16) RES="portrait" ;;
  1:1)  RES="square" ;;
  *) echo "aspect must be 16:9, 9:16 or 1:1" >&2; exit 2 ;;
esac

if [ -e "$TARGET" ]; then
  echo "Target already exists: $TARGET" >&2
  exit 1
fi

HF_VERSION="${HYPERFRAMES_VERSION:-0.8.27}"
PARENT="$(dirname "$TARGET")"
NAME="$(basename "$TARGET")"
mkdir -p "$PARENT"
cd "$PARENT"

echo "Scaffolding HyperFrames $HF_VERSION project at $TARGET ($ASPECT -> $RES)..."
# HYPERFRAMES_SKIP_SKILLS=1: don't re-link agent skills into ~/.claude/skills on every scaffold.
HYPERFRAMES_SKIP_SKILLS=1 npx --yes "hyperframes@$HF_VERSION" init "$NAME" \
  --example blank --non-interactive --resolution "$RES" 2>&1 | grep -v "npm warn" | tail -3

mkdir -p "$TARGET/assets/clips" "$TARGET/assets/audio" "$TARGET/assets/images" "$TARGET/renders"

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo ""
echo "Ready. Next steps:"
echo "  1. Copy assets:      cp clips/*.mp4 $TARGET/assets/clips/   (mp3/png likewise)"
echo "  2. Build timeline:   python3 $SKILL_DIR/scripts/build_hyperframes_timeline.py --project $TARGET --clip assets/clips/scene_01.mp4:6 ..."
echo "  3. Lint + check:     (cd $TARGET && npx --yes hyperframes@$HF_VERSION check)"
echo "  4. Preview (opt):    (cd $TARGET && npx --yes hyperframes@$HF_VERSION preview --background)"
echo "  5. Render:           $SKILL_DIR/scripts/render_hyperframes.sh $TARGET renders/film.mp4"
