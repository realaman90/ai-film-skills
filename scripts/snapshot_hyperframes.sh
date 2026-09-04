#!/bin/bash
# Capture key frames from a HyperFrames project as PNGs (fast visual QA without a full render).
# Usage: snapshot_hyperframes.sh <project-dir> <t1,t2,...> [output-dir]
# Example: snapshot_hyperframes.sh /tmp/my-film/film 0.5,4,9.5,14 /tmp/my-film/film/snaps
set -e
PROJECT="${1:?project dir required}"
AT="${2:?comma-separated seconds required, e.g. 0.5,4,9}"
OUT="${3:-snapshots}"
HF_VERSION="${HYPERFRAMES_VERSION:-0.8.27}"
cd "$PROJECT"
npx --yes "hyperframes@$HF_VERSION" snapshot --at "$AT" --output "$OUT" 2>&1 | grep -v "npm warn"
ls -1 "$OUT" 2>/dev/null || true
