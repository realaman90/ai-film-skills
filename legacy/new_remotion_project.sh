#!/bin/bash
# Scaffold a new Remotion project from the ai-film-studio template.
# Usage: new_remotion_project.sh <target-dir>
set -e

TARGET="${1:?target dir required (e.g. /tmp/my-film)}"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE_DIR="$SKILL_DIR/legacy/remotion-template"

if [ ! -d "$TEMPLATE_DIR" ]; then
  echo "Template not found at $TEMPLATE_DIR" >&2
  exit 1
fi

if [ -e "$TARGET" ]; then
  echo "Target already exists: $TARGET" >&2
  exit 1
fi

echo "Scaffolding Remotion project at $TARGET..."
mkdir -p "$TARGET/public"
cp -r "$TEMPLATE_DIR/src" "$TARGET/src"
cp "$TEMPLATE_DIR/package.json" "$TARGET/package.json"
cp "$TEMPLATE_DIR/tsconfig.json" "$TARGET/tsconfig.json"
cp "$TEMPLATE_DIR/remotion.config.ts" "$TARGET/remotion.config.ts"

# Default stub scenes.json so imports resolve before the user fills it in.
cat > "$TARGET/public/scenes.json" << 'JSON'
{
  "fps": 30,
  "width": 1920,
  "height": 1080,
  "background": "#0a0a0f",
  "scenes": [
    { "type": "title", "text": "Empty Film", "durationFrames": 60 }
  ]
}
JSON

echo "Installing dependencies (Remotion pulls Chromium on first install, ~1-3 min)..."
cd "$TARGET"
npm install --no-audit --no-fund --loglevel=error

echo ""
echo "Ready. Next steps:"
echo "  1. Drop mp4/mp3/png assets into: $TARGET/public/"
echo "  2. Edit timeline:                 $TARGET/public/scenes.json"
echo "     (or use build_remotion_timeline.py to generate it)"
echo "  3. Render:                        $SKILL_DIR/scripts/render_remotion.sh $TARGET out.mp4"
