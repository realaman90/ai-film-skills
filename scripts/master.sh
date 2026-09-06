#!/usr/bin/env bash
# Finals: conform HD takes, render high quality, master audio, write a web-ready file.
#
#   scripts/master.sh render  <project-dir> <out.mp4>          # hyperframes high-quality render → loudnorm → faststart
#   scripts/master.sh conform <in.mp4> <out.mp4> [W H] [setpts]  # 1080p/24 CFR conform (default 1920 1080); setpts e.g. 1.18 slows a 6 s take to 7 s
#   scripts/master.sh join    <out.mp4> <a.mp4:secs> <b.mp4:secs> ...   # hard-cut join of trimmed takes (for one long slot)
#   scripts/master.sh probe   <file.mp4>                         # dims, fps, duration, LUFS, true peak
#
# Targets: H.264 yuv420p, AAC 256k, -14 LUFS integrated, -1.5 dBTP, +faststart. Keep the raw render next to the master.
set -euo pipefail
cmd="${1:?render|conform|join|probe}"; shift
case "$cmd" in
  render)
    proj="${1:?project dir}"; out="${2:?output mp4}"; raw="${out%.mp4}_raw.mp4"
    "$(dirname "$0")/render_hyperframes.sh" "$proj" "$raw" --quality high
    ffmpeg -y -loglevel error -i "$raw" -c:v copy -af "loudnorm=I=-14:TP=-1.5:LRA=11" -c:a aac -b:a 256k -movflags +faststart "$out"
    "$0" probe "$out" ;;
  conform)
    in="${1:?in}"; out="${2:?out}"; W="${3:-1920}"; H="${4:-1080}"; pts="${5:-}"
    pre=""; [ -n "$pts" ] && pre="setpts=${pts}*PTS,"
    ffmpeg -y -loglevel error -i "$in" -vf "${pre}scale=${W}:${H}:force_original_aspect_ratio=increase:flags=lanczos,crop=${W}:${H},fps=24" \
      -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p -c:a aac -b:a 160k "$out"
    echo "$out $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out")s" ;;
  join)
    out="${1:?out}"; shift; tmp="$(mktemp -d)"; list="$tmp/list.txt"; i=0
    for spec in "$@"; do f="${spec%%:*}"; t="${spec##*:}"; i=$((i+1))
      ffmpeg -y -loglevel error -i "$f" -t "$t" -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p -an "$tmp/p$i.mp4"; echo "file 'p$i.mp4'" >> "$list"; done
    ffmpeg -y -loglevel error -f concat -safe 0 -i "$list" -c copy "$out"; rm -rf "$tmp"
    echo "$out $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out")s" ;;
  probe)
    f="${1:?file}"; ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate:format=duration,size -of csv=p=0 "$f"
    ffmpeg -i "$f" -af "loudnorm=print_format=summary" -f null - 2>&1 | grep -E "Input Integrated|Input True Peak" ;;
  *) echo "unknown: $cmd" >&2; exit 2 ;;
esac
