#!/usr/bin/env bash
# Conform chosen takes to 1920x1080 24fps CFR and install them under the slot names the film build expects.
# Usage: eras/real/swap_in.sh <1900 take> <1920 take> <1960 take> <1990 take> <2010A take> <2010B take> [results take]
set -euo pipefail
P=<project>; R=$P/eras/real; C=$P/film/assets/clips
mkdir -p $C/_prev; cp -n $C/broll_merchant1900.mp4 $C/ref_1926.mp4 $C/broll_boardroom1960.mp4 $C/broll_mailroom1990.mp4 $C/broll_saasdesk2010.mp4 $C/ref_2016b.mp4 $C/scene_results.mp4 $C/_prev/ 2>/dev/null || true
conform(){ ffmpeg -y -loglevel error -i "$R/$1.mp4" -vf "scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,fps=24" -c:v libx264 -crf 15 -pix_fmt yuv420p -c:a aac -b:a 128k "$C/$2"; echo "  $1 -> $2 ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$C/$2")s)"; }
conform "$1" broll_merchant1900.mp4
conform "$2" ref_1926.mp4
conform "$3" broll_boardroom1960.mp4
conform "$4" broll_mailroom1990.mp4
conform "$5" broll_saasdesk2010.mp4
conform "$6" ref_2016b.mp4
[ "${7:-}" ] && conform "$7" scene_results.mp4
echo "installed; previous takes kept in $C/_prev"
