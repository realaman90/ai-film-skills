#!/bin/bash
# Render a HyperFrames project to video.
# Usage: render_hyperframes.sh <project-dir> <output-file> [--quality draft|standard|high] [extra hyperframes render flags]
#
# Examples:
#   render_hyperframes.sh /tmp/my-film/film renders/film.mp4
#   render_hyperframes.sh /tmp/my-film/film renders/draft.mp4 --quality draft
#   render_hyperframes.sh /tmp/my-film/film renders/film.gif --format gif --fps 15
#   render_hyperframes.sh /tmp/my-film/film renders/film_4k.mp4 --resolution landscape-4k
#
# Output path is relative to the project dir unless absolute.
# Runs `hyperframes lint` first and refuses to render on lint errors.
set -e

PROJECT="${1:?project dir required}"
OUTPUT="${2:?output file required}"
shift 2

if [ ! -d "$PROJECT" ]; then
  echo "Project not found: $PROJECT" >&2
  exit 1
fi

HF_VERSION="${HYPERFRAMES_VERSION:-0.8.27}"
QUALITY="high"
EXTRA=()
while [ $# -gt 0 ]; do
  case "$1" in
    --quality) QUALITY="$2"; shift 2 ;;
    *) EXTRA+=("$1"); shift ;;
  esac
done

cd "$PROJECT"
case "$OUTPUT" in
  /*) ;;
  *) mkdir -p "$(dirname "$OUTPUT")" ;;
esac

echo "== lint =="
npx --yes "hyperframes@$HF_VERSION" lint 2>&1 | grep -v "npm warn"
echo "== render ($QUALITY) =="
npx --yes "hyperframes@$HF_VERSION" render --strict --quality "$QUALITY" --output "$OUTPUT" "${EXTRA[@]}" 2>&1 \
  | grep -v "npm warn" | grep -vE '^\[INFO\]|initSession|render runtime fps'

echo ""
echo "Rendered: $OUTPUT"
command -v ffprobe >/dev/null && ffprobe -v error -show_entries format=duration:stream=codec_type,width,height -of compact "$OUTPUT" 2>/dev/null || true
