#!/bin/bash
# Render a Remotion project to video.
# Usage: render_remotion.sh <project-dir> <output-file> [extra remotion flags]
set -e

PROJECT="${1:?project dir required}"
OUTPUT="${2:?output file required}"
shift 2

if [ ! -d "$PROJECT" ]; then
  echo "Project not found: $PROJECT" >&2
  exit 1
fi

cd "$PROJECT"
mkdir -p "$(dirname "$OUTPUT")"

# concurrency=1 + gl=angle avoids WebGL issues on headless Linux / EC2.
exec npx --yes remotion render src/index.ts Film "$OUTPUT" \
  --concurrency=1 \
  --gl=angle \
  "$@"
