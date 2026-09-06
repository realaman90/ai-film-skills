#!/usr/bin/env python3
"""Turn ElevenLabs character timestamps into phrase times you can key animation to.

`generate_tts.py --timestamps words.json` saves {"characters": [...], "character_start_times_seconds": [...], ...}.
This prints when each phrase starts (absolute, or relative to an anchor phrase) so camera moves, kinetic cards and
era pushes land on the spoken word instead of on a guess.

Usage:
    python scripts/vo_words.py audio/vo_words.json "strategy" "content" "every channel" "what actually"
    python scripts/vo_words.py audio/vo_words.json --anchor "It runs" "strategy" "content"      # offsets from the line start
    python scripts/vo_words.py audio/vo_words.json --all            # every word with its start time
In code:  from vo_words import phrase_time; t = line_start + phrase_time(words, "every channel", anchor="It runs")
"""
import argparse, json, re, sys


def load(path):
    w = json.load(open(path)); return "".join(w["characters"]), w["character_start_times_seconds"], w.get("character_end_times_seconds")


def phrase_time(words, phrase, anchor=None):
    """words = (chars, starts, ends) from load(). Returns seconds; relative to the anchor phrase when given."""
    chars, st, _ = words; i0 = chars.find(anchor) if anchor else 0
    if i0 < 0:
        raise ValueError(f"anchor not found: {anchor!r}")
    j = chars.find(phrase, i0)
    if j < 0:
        raise ValueError(f"phrase not found after anchor: {phrase!r}")
    return st[j] - (st[i0] if anchor else 0.0)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("words_json"); p.add_argument("phrases", nargs="*"); p.add_argument("--anchor", default=None); p.add_argument("--all", action="store_true")
    a = p.parse_intermixed_args(); words = load(a.words_json); chars, st, en = words
    if a.all:
        for m in re.finditer(r"\S+", chars):
            print(f"{st[m.start()]:7.2f}  {m.group()}")
        return
    for ph in a.phrases:
        try:
            print(f"{phrase_time(words, ph, a.anchor):7.2f}  {ph}")
        except ValueError as e:
            print(f"   --    {ph}  ({e})", file=sys.stderr)


if __name__ == "__main__":
    main()
